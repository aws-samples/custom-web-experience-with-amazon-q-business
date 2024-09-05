import streamlit as st
from models.qbusiness_model import get_queue_chain
from streamlit_feedback import streamlit_feedback
from utils.translation_util import translate_text

class ChatController:

    def __init__(self, view):
        self.view = view
        # Initialize chat messages
        self.view.init_chat_messages()

        if prompt := st.chat_input():
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

        if st.session_state.messages[-1]["role"] != "assistant":
            self.generate_q_response(prompt)


    def generate_q_response(self, prompt):
        translated_prompt = prompt # translate_text(prompt, target_language_code='en')  # Translate to English TODO FIX Access Denied Error
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
