
import streamlit as st
import datetime
import boto3
import jwt

def assume_role_with_token(iam_token):
    decoded_token = jwt.decode(iam_token, options={"verify_signature": False})
    sts_client = boto3.client("sts", region_name="us-east-1")
    response = sts_client.assume_role(
        RoleArn=st.session_state.IAM_ROLE,
        RoleSessionName="qapp",
        ProvidedContexts=[
            {
                "ProviderArn": "arn:aws:iam::aws:contextProvider/IdentityCenter",
                "ContextAssertion": decoded_token["sts:identity_context"],
            }
        ],
    )
    st.session_state.aws_credentials = response["Credentials"]
    
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
    amazon_q = session.client("qbusiness", "us-east-1")
    return amazon_q
