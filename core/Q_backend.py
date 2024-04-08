import boto3
import time
from io import StringIO
from configparser import ConfigParser
import json
import os
import boto3

# Initialize the ConfigParser object
config = ConfigParser()

# Read the configuration file
config.read(os.path.join(os.path.dirname(__file__), 'data_feed_config.ini'))   
region = config["GLOBAL"]["region"]
amazon_q_app_id = config["GLOBAL"]["amazon_q_app_id"]


# This method create the Q client
def get_qclient():
    # Create a boto3 client for Amazon Q Business
    amazon_q = boto3.client('qbusiness',region)
    return amazon_q

# This code invoke chat_sync api and format the response for UI
def get_queue_chain(prompt_input,user_id, conversationId, parentMessageId):
    amazon_q = get_qclient()
    if conversationId != '':
     answer = amazon_q.chat_sync(
        applicationId=amazon_q_app_id,
        userMessage=prompt_input,
        userId = user_id,
        conversationId = conversationId,
        parentMessageId = parentMessageId
    )
    else:
        answer = amazon_q.chat_sync(
        applicationId=amazon_q_app_id,
        userMessage=prompt_input,
        userId = user_id)

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