
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
