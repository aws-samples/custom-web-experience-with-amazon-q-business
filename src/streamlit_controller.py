from datetime import datetime, timedelta, timezone

import jwt
import jwt.algorithms
import streamlit as st  # all streamlit commands will be available through the "st" alias
import utils
from user_view import UserView
from streamlit_feedback import streamlit_feedback


class StreamlitController:

    selected_timezone = timezone.utc

    def __init__(self, view):
        self.view: UserView = view

        self.init_config()
        oauth2 = utils.configure_oauth_component()
        if "token" not in st.session_state:
            self.view.show_authorize_button(oauth2, self.selected_timezone)
            return

        token = st.session_state["token"]
        if st.button("Refresh Cognito Token"):
            # If refresh token button is clicked or the token is expired, refresh the token
            token = self.refresh_token(oauth2)

        user_email = jwt.decode(token["id_token"], options={
                                "verify_signature": False})["email"]
        self.validate_jwt_token(user_email)
        self.view.set_headers()

        # Initialize the chat messages in the session state if it doesn't exist
        self.view.init_chat_messages()

        # User-provided prompt
        if prompt := st.chat_input():
            st.session_state.messages.append(
                {"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

        # If the last message is from the user, generate a response from the Q_backend
        if st.session_state.messages[-1]["role"] != "assistant":
            self.generate_q_response(prompt)

    def init_config(self):
        # Init configuration
        utils.retrieve_config_from_agent()
        if "aws_credentials" not in st.session_state:
            st.session_state.aws_credentials = None

        st.set_page_config(
            page_title="Amazon Q Business Custom UI")  # HTML title
        st.title("Amazon Q Business Custom UI")  # page title

    def refresh_token(self, oauth2):
        token = oauth2.refresh_token(token, force=True)
        # saving the long lived refresh_token
        refresh_token = token["refresh_token"]
        # Put the refresh token in the session state as it is not returned by Cognito
        token["refresh_token"] = refresh_token
        # Retrieve the Identity Center token

        st.session_state.token = token
        st.rerun()
        return token

    def validate_jwt_token(self, token):
        if "idc_jwt_token" not in st.session_state:
            st.session_state["idc_jwt_token"] = utils.get_iam_oidc_token(
                token["id_token"])
            st.session_state["idc_jwt_token"]["expires_at"] = datetime.now(self.selected_timezone) + \
                timedelta(
                    seconds=st.session_state["idc_jwt_token"]["expiresIn"])
        elif st.session_state["idc_jwt_token"]["expires_at"] < datetime.now(self.selected_timezone):
            # If the Identity Center token is expired, refresh the Identity Center token
            try:
                st.session_state["idc_jwt_token"] = utils.refresh_iam_oidc_token(
                    st.session_state["idc_jwt_token"]["refreshToken"]
                )
                st.session_state["idc_jwt_token"]["expires_at"] = datetime.now(self.selected_timezone) + \
                    timedelta(
                        seconds=st.session_state["idc_jwt_token"]["expiresIn"])
            except Exception as e:
                st.error(f"Error refreshing Identity Center token: {
                    e}. Please reload the page.")

    def generate_q_response(self, prompt):
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                placeholder = st.empty()
                response = utils.get_queue_chain(prompt, st.session_state["conversationId"],
                                                 st.session_state["parentMessageId"],
                                                 st.session_state["idc_jwt_token"]["idToken"])
                if "references" in response:
                    full_response = f"""{
                        response["answer"]}\n\n---\n{response["references"]}"""
                else:
                    full_response = f"""{
                        response["answer"]}\n\n---\nNo sources"""
                placeholder.markdown(full_response)
                st.session_state["conversationId"] = response["conversationId"]
                st.session_state["parentMessageId"] = response["parentMessageId"]

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response})
        feedback = streamlit_feedback(
            feedback_type="thumbs",
            optional_text_label="[Optional] Please provide an explanation",
        )
