from streamlit_oauth import OAuth2Component

class OauthModel:
    
    def __init__(self, cognito_domain, client_id):
        self.authorize_url = f"https://{cognito_domain}/oauth2/authorize"
        self.token_url = f"https://{cognito_domain}/oauth2/token"
        self.refresh_token_url = f"https://{cognito_domain}/oauth2/token"
        self.revoke_token_url = f"https://{cognito_domain}/oauth2/revoke"
        self.client_id = client_id
        
    def get_outh2_component(self):
        return OAuth2Component(
            self.client_id, 
            None, 
            self.authorize_url, 
            self.token_url, 
            self.refresh_token_url, 
            self.revoke_token_url
        )