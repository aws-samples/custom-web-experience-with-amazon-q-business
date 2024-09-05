from streamlit_oauth import OAuth2Component

def configure_oauth_component(oauth_config):
    """
    Configure the OAuth2 component for Cognito.
    """
    cognito_domain = oauth_config["CognitoDomain"]
    authorize_url = f"https://{cognito_domain}/oauth2/authorize"
    token_url = f"https://{cognito_domain}/oauth2/token"
    refresh_token_url = f"https://{cognito_domain}/oauth2/token"
    revoke_token_url = f"https://{cognito_domain}/oauth2/revoke"
    client_id = oauth_config["ClientId"]

    return OAuth2Component(
        client_id, None, authorize_url, token_url, refresh_token_url, revoke_token_url
    )
