from datetime import datetime, timedelta

import streamlit as st  # all streamlit commands will be available through the "st" alias
import utils


class UserView:

    # Define a function to clear the chat history
    def clear_chat_history(self):
        st.session_state.messages = [
            {"role": "assistant", "content": "How may I assist you today?"}]
        st.session_state.questions = []
        st.session_state.answers = []
        st.session_state.input = ""
        st.session_state["chat_history"] = []
        st.session_state["conversationId"] = ""
        st.session_state["parentMessageId"] = ""

    def show_authorize_button(self, oauth2, selected_timezone):
        # If not, show authorize button
        redirect_uri = f"https://{utils.OAUTH_CONFIG['ExternalDns']}/component/streamlit_oauth.authorize_button/index.html"
        result = oauth2.authorize_button(
            "Connect with Cognito", scope="openid", pkce="S256", redirect_uri=redirect_uri)
        if result and "token" in result:
            # If authorization successful, save token in session state
            st.session_state.token = result.get("token")
            # Retrieve the Identity Center token
            st.session_state["idc_jwt_token"] = utils.get_iam_oidc_token(
                st.session_state.token["id_token"])
            st.session_state["idc_jwt_token"]["expires_at"] = datetime.now(tz=selected_timezone) + \
                timedelta(
                    seconds=st.session_state["idc_jwt_token"]["expiresIn"])
            st.rerun()

    def init_chat_messages(self):
        if "messages" not in st.session_state:
            st.session_state["messages"] = [
                {"role": "assistant", "content": "How can I help you?"}]

        if "conversationId" not in st.session_state:
            st.session_state["conversationId"] = ""

        if "parentMessageId" not in st.session_state:
            st.session_state["parentMessageId"] = ""

        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []

        if "questions" not in st.session_state:
            st.session_state.questions = []

        if "answers" not in st.session_state:
            st.session_state.answers = []

        if "input" not in st.session_state:
            st.session_state.input = ""

        # Display the chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    def set_headers(self, user_email):
        col1, col2 = st.columns([1, 1])
        with col1:
            st.write("Welcome: ", user_email)
        with col2:
            st.button("Clear Chat History", on_click=self.clear_chat_history)
