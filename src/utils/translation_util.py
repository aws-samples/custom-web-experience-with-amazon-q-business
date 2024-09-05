import boto3
import streamlit as st

def translate_text(text, source_language_code='auto', target_language_code='en'):
    translate = boto3.client('translate', region_name="us-east-1")
    result = translate.translate_text(
        Text=text,
        SourceLanguageCode=source_language_code,
        TargetLanguageCode=target_language_code
    )
    return result['TranslatedText']
