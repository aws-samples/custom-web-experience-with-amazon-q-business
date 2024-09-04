from datetime import datetime, timedelta, timezone
import jwt
import streamlit as st
from utils.oauth_util import configure_oauth_component
from utils.config_util import retrieve_config
from utils.sts_util import assume_role_with_token
from utils.token_util import refresh_iam_oidc_token, get_iam_oidc_token
from models.qbusiness_model import get_queue_chain
from streamlit_feedback import streamlit_feedback

class StreamlitController:
    selected_timezone = timezone.utc

    def __init__(self, view):
        self.view = view

        self.init_config()
        oauth2 = configure_oauth_component(st.session_state.OAUTH_CONFIG)
        
        if "token" not in st.session_state:
            self.view.show_authorize_button(oauth2, self.selected_timezone)
            return

        token = st.session_state["token"]
        refresh_token = token["refresh_token"]
        if st.button("Refresh Cognito Token"):
            self.refresh_token(oauth2, refresh_token)

        user_email = jwt.decode(token["id_token"], options={"verify_signature": False})["email"]
        self.validate_jwt_token(token)
        self.view.set_headers(user_email)

        # Initialize chat messages
        self.view.init_chat_messages()

        if prompt := st.chat_input():
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

        if st.session_state.messages[-1]["role"] != "assistant":
            self.generate_q_response(prompt)

    def init_config(self):
        """
        Retrieve and set the configuration values
        """
        config = retrieve_config()
        st.session_state.OAUTH_CONFIG = config["OAuthConfig"]
        st.session_state.IAM_ROLE = config["IamRoleArn"]
        st.session_state.REGION = config["Region"]
        st.session_state.IDC_APPLICATION_ID = config["IdcApplicationArn"]
        st.session_state.AMAZON_Q_APP_ID = config["AmazonQAppId"]

        if "aws_credentials" not in st.session_state:
            st.session_state.aws_credentials = None

        st.set_page_config(page_title="Amazon Q Business Custom UI")
        st.title("Amazon Q Business Custom UI")

    def refresh_token(self, oauth2, refresh_token):
        """
        Refresh the Cognito token when expired
        """
        token = oauth2.refresh_token(st.session_state["token"], force=True)
        token["refresh_token"] = refresh_token
        st.session_state.token = token
        st.rerun()

    def validate_jwt_token(self, token):
        """
        Validate and refresh the IAM OIDC token
        """
        if "idc_jwt_token" not in st.session_state:
            st.session_state["idc_jwt_token"] = get_iam_oidc_token(token["id_token"], st.session_state.IDC_APPLICATION_ID, st.session_state.REGION)
            st.session_state["idc_jwt_token"]["expires_at"] = datetime.now(self.selected_timezone) + \
                timedelta(seconds=st.session_state["idc_jwt_token"]["expiresIn"])
        elif st.session_state["idc_jwt_token"]["expires_at"] < datetime.now(self.selected_timezone):
            try:
                st.session_state["idc_jwt_token"] = refresh_iam_oidc_token(st.session_state["idc_jwt_token"]["refreshToken"], st.session_state.IDC_APPLICATION_ID, st.session_state.REGION)
                st.session_state["idc_jwt_token"]["expires_at"] = datetime.now(self.selected_timezone) + \
                    timedelta(seconds=st.session_state["idc_jwt_token"]["expiresIn"])
            except Exception as e:
                st.error(f"Error refreshing Identity Center token: {e}. Please reload the page.")

        # Assuming the role using the refreshed IAM token
        if not st.session_state.aws_credentials:
            assume_role_with_token(st.session_state["idc_jwt_token"]["idToken"], st.session_state.IAM_ROLE, st.session_state.REGION)

    def generate_q_response(self, prompt):
        translated_prompt = prompt #translate_text(prompt, target_language_code='en')  # Translate to English TODO
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                placeholder = st.empty()
                response = get_queue_chain(translated_prompt, st.session_state["conversationId"],
                                           st.session_state["parentMessageId"],
                                           st.session_state["idc_jwt_token"]["idToken"])
                if "references" in response:
                    full_response = f"{response['answer']}\n\n---\n{response['references']}"
                else:
                    full_response = f"{response['answer']}\n\n---\nNo sources"
                placeholder.markdown(full_response)
                st.session_state["conversationId"] = response["conversationId"]
                st.session_state["parentMessageId"] = response["parentMessageId"]

        st.session_state.messages.append({"role": "assistant", "content": full_response})
        streamlit_feedback(feedback_type="thumbs", optional_text_label="[Optional] Please provide an explanation")
