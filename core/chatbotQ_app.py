import streamlit as st #all streamlit commands will be available through the "st" alias
import Q_backend #reference to local lib script

from streamlit.web.server.websocket_headers import _get_websocket_headers
import jwt
import uuid
import json
from streamlit_feedback import streamlit_feedback

# This function attempts to decode the session token from the Streamlit websocket headers
# It uses the JWT library to decode the token, but does not verify its authenticity
def process_session_token():
    '''
    WARNING: We use unsupported features of Streamlit
             However, this is quite fast and works well with
             the latest version of Streamlit (1.27)
             Also, this does not verify the session token's
             authenticity. It only decodes the token.
    '''
    headers = _get_websocket_headers()
    if not headers or "X-Amzn-Oidc-Data" not in headers:
        return {}
    return jwt.decode(
        headers["X-Amzn-Oidc-Data"], algorithms=["ES256"], options={"verify_signature": False}
    )



st.set_page_config(page_title="Amazon Q Business Custom UI") #HTML title
st.title("Amazon Q Business Custom UI") #page title


session_token = process_session_token()

if session_token:
    user_email = session_token['email']
    
else :
    user_email= 'test@abc.com'       


# Define a function to clear the chat history
def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.input = ""
    st.session_state["chat_history"] = []
    st.session_state['conversationId'] = ''
    st.session_state['parentMessageId'] = ''


col1, col2 = st.columns([1,1])

with col1:
    st.write('Welcome: ', user_email)
with col2:
    st.button('Clear Chat History', on_click=clear_chat_history)


# Initialize the chat messages in the session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

# Check if the user ID is already stored in the session state
if 'user_id' in st.session_state:
    user_id = st.session_state['user_id']

# If the user ID is not yet stored in the session state, generate a random UUID
else:
    user_id = str(uuid.uuid4())
    st.session_state['user_id'] = user_id

if 'conversationId' not in st.session_state:
    st.session_state['conversationId'] = ''

if 'parentMessageId' not in st.session_state:    
    st.session_state['parentMessageId'] = ''

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

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


# User-provided prompt
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)


# If the last message is from the user, generate a response from the Q_backend
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            placeholder = st.empty()
            response = Q_backend.get_queue_chain(prompt,user_email,st.session_state['conversationId'], st.session_state['parentMessageId'])
            if "references" in response:
                full_response = f'''{response["answer"]}\n\n---\n{response["references"]}'''
            else:
                full_response = f'''{response["answer"]}\n\n---\nNo sources'''
            placeholder.markdown(full_response)
            st.session_state['conversationId'] = response["conversationId"]
            st.session_state['parentMessageId'] = response["parentMessageId"]


    st.session_state.messages.append({"role": "assistant", "content": full_response})
    feedback = streamlit_feedback(
        feedback_type="thumbs",
        optional_text_label="[Optional] Please provide an explanation",
    )
    

