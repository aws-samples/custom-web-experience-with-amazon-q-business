from datetime import timezone
import streamlit as st
from utils.config_util import retrieve_config
from models.config_model import ConfigModel

class InitConfigController:
    selected_timezone = timezone.utc
    
    def __init__(self):
        self.init_config()


    def init_config(self):
        """
        Retrieve and set the configuration values
        """
        config: ConfigModel = retrieve_config()
        st.session_state.OAUTH_CONFIG = config.oauth_config
        st.session_state.IAM_ROLE = config.iam_role
        st.session_state.REGION = config.region
        st.session_state.IDC_APPLICATION_ID = config.idc_application_id
        st.session_state.AMAZON_Q_APP_ID = config.amazon_q_app_id

        if "aws_credentials" not in st.session_state:
            st.session_state.aws_credentials = None

        st.set_page_config(page_title="Amazon Q Business Custom UI")
        st.title("Amazon Q Business Custom UI")