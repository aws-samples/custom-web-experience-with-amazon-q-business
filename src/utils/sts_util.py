import jwt
import boto3
import streamlit as st

def assume_role_with_token(iam_token):
    """
    Assume IAM role using the IAM OIDC idToken.
    """
    decoded_token = jwt.decode(iam_token, options={"verify_signature": False})
    sts_client = boto3.client("sts", region_name=st.session_state.REGION)
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
