import streamlit as st
import jwt
from utils.q_util import get_q_chain
from streamlit_feedback import streamlit_feedback
from utils.translation_util import translate_text

class ChatController:

    def __init__(self, view):
        self.view = view
        
        # Set headers
        user_email = jwt.decode(st.session_state["token"]["id_token"], options={"verify_signature": False})["email"]
        self.view.set_headers(user_email)
        
        # Initialize chat messages
        self.view.init_chat_messages()

        if prompt := st.chat_input():
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

        if st.session_state.messages[-1]["role"] != "assistant":
            self.generate_q_response(prompt)


    def generate_q_response(self, prompt):
        translated_prompt = translate_text(prompt, target_language_code='en')
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                placeholder = st.empty()
                response = get_q_chain(translated_prompt, st.session_state["conversationId"],
                                           st.session_state["parentMessageId"],
                                           st.session_state["idc_jwt_token"]["idToken"])
                if "references" in response:
                    full_response = f"{response['answer']}\n\n---\n{response['references']}"
                else:
                    full_response = f"{response['answer']}\n\n---\nNo sources"
                placeholder.markdown(full_response)
                st.session_state["conversationId"] = response["conversationId"]
                st.session_state["parentMessageId"] = response["parentMessageId"]

        st.session_state.messages.append({"role": "assistant", "content": full_response}) #TODO translate back text to original language
        streamlit_feedback(feedback_type="thumbs", optional_text_label="[Optional] Please provide an explanation")
