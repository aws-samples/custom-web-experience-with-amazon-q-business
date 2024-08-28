import boto3

def refresh_iam_oidc_token(refresh_token):
    client = boto3.client("sso-oidc", region_name="us-east-1")
    response = client.create_token(
        clientId="YOUR_CLIENT_ID",
        grantType="refresh_token",
        refreshToken=refresh_token,
    )
    return response

def get_iam_oidc_token(id_token):
    client = boto3.client("sso-oidc", region_name="us-east-1")
    response = client.create_token(
        clientId="YOUR_CLIENT_ID",
        grantType="urn:ietf:params:oauth:grant-type:jwt-bearer",
        assertion=id_token,
    )
    return response
