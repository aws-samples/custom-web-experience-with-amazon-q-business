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

    def show_sample_questions(self):
        sample_questions = [
            "What can I cook with chicken?",
            "Que puis-je cuisiner avec du poulet?",
            "Was kann ich mit Hühnchen kochen?",
            "मैं चिकन के साथ क्या पका सकता हूँ?",
            "ماذا يمكنني أن أطبخ بالدجاج؟"
        ]
        # Display sample question buttons
        st.markdown(
            """
            <style>
            .faq-title {
                text-align: center;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 20px; /* Adjust the value as needed */
            }
            </style>
            <div class="faq-title">Frequently Asked Questions</div>
            """,
            unsafe_allow_html=True
        )
        cols = st.columns(len(sample_questions))
        for idx, question in enumerate(sample_questions):
            cols[idx].button(
                question,
                key=question,
                help="Click to ask",
                on_click=lambda q=question: self.prompt_clicked(q)
            )

    def prompt_clicked(self, question):
        st.session_state.clicked_input = question
        
    def init_chat_messages(self):
        if "clicked_input" not in st.session_state:
            st.session_state.clicked_input = ""
        # Define sample questions
        self.show_sample_questions()
    
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

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

