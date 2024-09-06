import streamlit as st
import datetime
import boto3
from utils.sts_util import assume_role_with_token


def get_qclient(idc_id_token: str):
    """
    Create the Q client using the identity-aware AWS Session.
    """
    if not st.session_state.aws_credentials:
        assume_role_with_token(idc_id_token)
    elif st.session_state.aws_credentials["Expiration"] < datetime.datetime.now(datetime.UTC):
        assume_role_with_token(idc_id_token)

    session = boto3.Session(
        aws_access_key_id=st.session_state.aws_credentials["AccessKeyId"],
        aws_secret_access_key=st.session_state.aws_credentials["SecretAccessKey"],
        aws_session_token=st.session_state.aws_credentials["SessionToken"],
    )
    amazon_q = session.client("qbusiness", st.session_state.REGION)
    return amazon_q


def get_q_chain(prompt_input, conversation_id, parent_message_id, token):
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