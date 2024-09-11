from datetime import datetime, timedelta, timezone
import streamlit as st
from utils.sts_util import assume_role_with_token
from utils.token_util import refresh_iam_oidc_token, get_iam_oidc_token
from models.oauth_model import OauthModel

class AuthController:
    selected_timezone = timezone.utc
    
    def __init__(self, view):
        self.view = view
    
    def authenticate(self):
        oauth_comp_model: OauthModel = OauthModel(
            cognito_domain=st.session_state.OAUTH_CONFIG["CognitoDomain"], 
            client_id=st.session_state.OAUTH_CONFIG["ClientId"]
        )
        oauth2 = oauth_comp_model.get_outh2_component()
        
        if "token" not in st.session_state:
            self.view.show_authorize_button(oauth2, self.selected_timezone)
            return False

        token = st.session_state["token"]
        refresh_token = token["refresh_token"]
        if st.button("Refresh Cognito Token"):
            self.refresh_token(oauth2, refresh_token)

        self.validate_jwt_token(token)
        return True
    
    def refresh_token(self, oauth2, refresh_token):
        """
        Refresh the Cognito token when expired
        """
        token = oauth2.refresh_token(st.session_state["token"], force=True)
        token["refresh_token"] = refresh_token
        st.session_state.token = token
        st.rerun()

    def validate_jwt_token(self, token):
        """
        Validate and refresh the IAM OIDC token
        """
        if "idc_jwt_token" not in st.session_state:
            st.session_state["idc_jwt_token"] = get_iam_oidc_token(token["id_token"], st.session_state.IDC_APPLICATION_ID)
            st.session_state["idc_jwt_token"]["expires_at"] = datetime.now(self.selected_timezone) + \
                timedelta(seconds=st.session_state["idc_jwt_token"]["expiresIn"])
        elif st.session_state["idc_jwt_token"]["expires_at"] < datetime.now(self.selected_timezone):
            try:
                st.session_state["idc_jwt_token"] = refresh_iam_oidc_token(st.session_state["idc_jwt_token"]["refreshToken"], st.session_state.IDC_APPLICATION_ID)
                st.session_state["idc_jwt_token"]["expires_at"] = datetime.now(self.selected_timezone) + \
                    timedelta(seconds=st.session_state["idc_jwt_token"]["expiresIn"])
            except Exception as e:
                st.error(f"Error refreshing Identity Center token: {e}. Please reload the page.")

        # Assuming the role using the refreshed IAM token
        if not st.session_state.aws_credentials:
            assume_role_with_token(st.session_state["idc_jwt_token"]["idToken"])