import os
import urllib3
import json

def retrieve_config():
    """
    Retrieve the configuration from the AppConfig agent.
    """
    app_name = os.environ["APPCONFIG_APP_NAME"]
    env_name = os.environ["APPCONFIG_ENV_NAME"]
    config_name = os.environ["APPCONFIG_CONF_NAME"]
    
    url = f"http://localhost:2772/applications/{app_name}/environments/{env_name}/configurations/{config_name}"
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    
    return json.loads(response.data.decode('utf-8'))
