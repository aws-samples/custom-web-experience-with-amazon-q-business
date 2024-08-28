import boto3

def refresh_iam_oidc_token(refresh_token, idc_application_id, region):
    """
    Refresh the IAM OIDC token using the refresh token.
    """
    client = boto3.client("sso-oidc", region_name=region)
    response = client.create_token(
        clientId=idc_application_id,
        grantType="refresh_token",
        refreshToken=refresh_token,
    )
    return response

def get_iam_oidc_token(id_token, idc_application_id, region):
    """
    Retrieve the IAM OIDC token using the ID token.
    """
    client = boto3.client("sso-oidc", region_name=region)
    response = client.create_token(
        clientId=idc_application_id,
        grantType="urn:ietf:params:oauth:grant-type:jwt-bearer",
        assertion=id_token,
    )
    return response
