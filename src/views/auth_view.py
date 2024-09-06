from datetime import datetime, timedelta
import streamlit as st
import utils.token_util as token_util

class AuthView:

    def show_authorize_button(self, oauth2, selected_timezone):
        redirect_uri = f"https://{st.session_state.OAUTH_CONFIG['ExternalDns']}/component/streamlit_oauth.authorize_button/index.html"
        result = oauth2.authorize_button("Connect with Cognito", scope="openid", pkce="S256", redirect_uri=redirect_uri)
        if result and "token" in result:
            st.session_state.token = result.get("token")
            st.session_state["idc_jwt_token"] = token_util.get_iam_oidc_token(
                st.session_state.token["id_token"], 
                st.session_state.IDC_APPLICATION_ID)
            st.session_state["idc_jwt_token"]["expires_at"] = datetime.now(tz=selected_timezone) + \
                timedelta(seconds=st.session_state["idc_jwt_token"]["expiresIn"])
            st.rerun()