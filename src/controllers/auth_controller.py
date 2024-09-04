from datetime import datetime, timedelta, timezone
import jwt
import streamlit as st
from utils.oauth_util import configure_oauth_component
from utils.sts_util import assume_role_with_token
from utils.token_util import refresh_iam_oidc_token, get_iam_oidc_token

class AuthController:
    selected_timezone = timezone.utc
    
    def __init__(self, view):
        self.view = view
        oauth2 = configure_oauth_component(st.session_state.OAUTH_CONFIG)
        
        if "token" not in st.session_state:
            self.view.show_authorize_button(oauth2, self.selected_timezone)
            return

        token = st.session_state["token"]
        refresh_token = token["refresh_token"]
        if st.button("Refresh Cognito Token"):
            self.refresh_token(oauth2, refresh_token)

        user_email = jwt.decode(token["id_token"], options={"verify_signature": False})["email"]
        self.validate_jwt_token(token)
        self.view.set_headers(user_email)
    
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
            st.session_state["idc_jwt_token"] = get_iam_oidc_token(token["id_token"], st.session_state.IDC_APPLICATION_ID, st.session_state.REGION)
            st.session_state["idc_jwt_token"]["expires_at"] = datetime.now(self.selected_timezone) + \
                timedelta(seconds=st.session_state["idc_jwt_token"]["expiresIn"])
        elif st.session_state["idc_jwt_token"]["expires_at"] < datetime.now(self.selected_timezone):
            try:
                st.session_state["idc_jwt_token"] = refresh_iam_oidc_token(st.session_state["idc_jwt_token"]["refreshToken"], st.session_state.IDC_APPLICATION_ID, st.session_state.REGION)
                st.session_state["idc_jwt_token"]["expires_at"] = datetime.now(self.selected_timezone) + \
                    timedelta(seconds=st.session_state["idc_jwt_token"]["expiresIn"])
            except Exception as e:
                st.error(f"Error refreshing Identity Center token: {e}. Please reload the page.")

        # Assuming the role using the refreshed IAM token
        if not st.session_state.aws_credentials:
            assume_role_with_token(st.session_state["idc_jwt_token"]["idToken"], st.session_state.IAM_ROLE, st.session_state.REGION)