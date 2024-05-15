import boto3
import os
import logging
import jwt
import datetime
import urllib3
from streamlit_oauth import OAuth2Component


logger = logging.getLogger()

# Read the configuration file
APPCONFIG_APP_NAME = os.environ["APPCONFIG_APP_NAME"]
APPCONFIG_ENV_NAME = os.environ["APPCONFIG_ENV_NAME"]
APPCONFIG_CONF_NAME = os.environ["APPCONFIG_CONF_NAME"]
AWS_CREDENTIALS = {}
AMAZON_Q_APP_ID = None
IAM_ROLE = None
REGION = None
IDC_APPLICATION_ID = None
OAUTH_CONFIG = {}

def retrieve_config_from_agent():
    global IAM_ROLE, REGION, IDC_APPLICATION_ID, AMAZON_Q_APP_ID, OAUTH_CONFIG
    config = urllib3.request("GET", f"http://localhost:2772/applications/{APPCONFIG_APP_NAME}/environments/{APPCONFIG_ENV_NAME}/configurations/{APPCONFIG_CONF_NAME}").json()
    IAM_ROLE = config["IamRoleArn"]
    REGION = config["Region"]
    IDC_APPLICATION_ID = config["IdcApplicationArn"]
    AMAZON_Q_APP_ID = config["AmazonQAppId"]
    OAUTH_CONFIG = config["OAuthConfig"]
    return config

def configure_oauth_component():
    external_dns = OAUTH_CONFIG["ExternalDns"]
    cognito_domain = OAUTH_CONFIG["CognitoDomain"]
    authorize_url = f"https://{cognito_domain}/oauth2/authorize"
    token_url = f"https://{cognito_domain}/oauth2/token"
    refresh_token_url = f"https://{cognito_domain}/oauth2/token"
    revoke_token_url = f"https://{cognito_domain}/oauth2/revoke"
    client_id = OAUTH_CONFIG["ClientId"]
    # Create OAuth2Component instance
    return OAuth2Component(client_id, None, authorize_url, token_url, refresh_token_url, revoke_token_url)

def get_iam_oidc_token(id_token):
    client = boto3.client('sso-oidc', region_name=REGION)
    response = client.create_token_with_iam(
        clientId=IDC_APPLICATION_ID,
        grantType='urn:ietf:params:oauth:grant-type:jwt-bearer',
        assertion=id_token
    )
    return response

def assume_role_with_token(iam_token):
    global AWS_CREDENTIALS
    print(iam_token)
    decoded_token = jwt.decode(iam_token, options={"verify_signature": False})
    sts_client = boto3.client("sts", region_name=REGION)
    response = sts_client.assume_role(
        RoleArn=IAM_ROLE,
        RoleSessionName="qapp",
        ProvidedContexts=[
            {
                "ProviderArn": "arn:aws:iam::aws:contextProvider/IdentityCenter",
                "ContextAssertion": decoded_token["sts:identity_context"],
            }
        ],
    )
    AWS_CREDENTIALS = response["Credentials"]
    return response


# This method create the Q client
def get_qclient(access_token: str):
    # Create a boto3 client for Amazon Q Business
    if not AWS_CREDENTIALS or AWS_CREDENTIALS['Expiration'] < datetime.datetime.now(datetime.timezone.utc):
        assume_role_with_token(access_token)
    session = boto3.Session(
        aws_access_key_id=AWS_CREDENTIALS['AccessKeyId'],
        aws_secret_access_key=AWS_CREDENTIALS['SecretAccessKey'],
        aws_session_token=AWS_CREDENTIALS['SessionToken']
    )
    amazon_q = session.client('qbusiness',REGION)
    return amazon_q

# This code invoke chat_sync api and format the response for UI
def get_queue_chain(prompt_input,user_id, conversationId, parentMessageId, access_token):
    amazon_q = get_qclient(access_token)
    if conversationId != '':
     answer = amazon_q.chat_sync(
        applicationId=AMAZON_Q_APP_ID,
        userMessage=prompt_input,
        conversationId = conversationId,
        parentMessageId = parentMessageId
    )
    else:
        answer = amazon_q.chat_sync(
        applicationId=AMAZON_Q_APP_ID,
        userMessage=prompt_input)

    system_message = answer.get('systemMessage', '')
    conversationId = answer.get('conversationId', '')
    parentMessageId = answer.get('systemMessageId', '')
    result = {
        "answer": system_message,
        "conversationId": conversationId,
        "parentMessageId": parentMessageId
    }



    if 'sourceAttributions' in answer and answer['sourceAttributions']:
        attributions = answer['sourceAttributions']
        valid_attributions = []
        
        # Generate the answer references extracting citation number, the document title, and if present, the document url
        for attr in attributions:
            title = attr.get('title', '')
            url = attr.get('url', '')
            citation_number = attr.get('citationNumber', '')

            attribution_text = ""
            if citation_number:
                attribution_text += f"[{citation_number}] "
            if title:
                attribution_text += f"Title: {title}"
            if url:
                attribution_text += f", URL: {url}"

            
            valid_attributions.append(attribution_text)
        
        concatenated_attributions = "\n\n".join(valid_attributions)
        result["references"] = concatenated_attributions

        # Process the citation numbers and insert them into the system message
        citations = {}
        for attr in answer['sourceAttributions']:
            for segment in attr['textMessageSegments']:
                citations[segment['endOffset']] = attr['citationNumber']
        offset_citations = sorted(citations.items(), key=lambda x: x[0])
        modified_message = ""
        prev_offset = 0

        for offset, citation_number in offset_citations:
            modified_message += system_message[prev_offset:offset] + f"[{citation_number}]"
            prev_offset = offset

        modified_message += system_message[prev_offset:]
        result["answer"] = modified_message
    
    return result