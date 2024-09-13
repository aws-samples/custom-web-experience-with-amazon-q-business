import streamlit as st

class UserView:

    def set_headers(self, user_email):
        col1, col2 = st.columns([1, 1])
        with col1:
            st.write("Welcome: ", user_email)
        with col2:
            st.button("Clear Chat History", on_click=self.clear_chat_history)


    def clear_chat_history(self):
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
        st.session_state.questions = []
        st.session_state.answers = []
        st.session_state.input = ""
        st.session_state["chat_history"] = []
        st.session_state["conversationId"] = ""
        st.session_state["parentMessageId"] = ""


    def init_chat_messages(self):
        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
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
        if "thinking" not in st.session_state:
            st.session_state.thinking = False

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

