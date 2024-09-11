class ConfigModel:
    
    def __init__(
        self, 
        oauth_config, 
        iam_role,
        region,
        idc_application_id,
        amazon_q_app_id
    ):
        self.oauth_config = oauth_config
        self.iam_role = iam_role
        self.region = region
        self.idc_application_id = idc_application_id
        self.amazon_q_app_id = amazon_q_app_id