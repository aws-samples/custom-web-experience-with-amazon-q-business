from infrastructure.aws_services import get_qclient
import streamlit as st

def get_queue_chain(prompt_input, conversation_id, parent_message_id, token):
    amazon_q = get_qclient(token)
    if conversation_id != "":
        answer = amazon_q.chat_sync(
            applicationId=st.session_state.AMAZON_Q_APP_ID,
            userMessage=prompt_input,
            conversationId=conversation_id,
            parentMessageId=parent_message_id,
        )
    else:
        answer = amazon_q.chat_sync(
            applicationId=st.session_state.AMAZON_Q_APP_ID, userMessage=prompt_input
        )

    result = {
        "answer": answer.get("systemMessage", ""),
        "conversationId": answer.get("conversationId", ""),
        "parentMessageId": answer.get("systemMessageId", ""),
    }

    if answer.get("sourceAttributions"):
        valid_attributions = [
            f"[{attr.get('citationNumber', '')}] Title: {attr.get('title', '')}, URL: {attr.get('url', '')}"
            for attr in answer["sourceAttributions"]
        ]
        result["references"] = "\n\n".join(valid_attributions)

    return result
