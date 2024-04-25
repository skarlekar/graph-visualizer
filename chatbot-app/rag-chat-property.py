import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.chat_models import BedrockChat
from rdflib import Graph, Literal
# import boto3
import json
from jinja2 import Environment, FileSystemLoader
import sys
from pathlib import Path
import os

# bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
template_dir = os.path.abspath(os.path.join(os.getcwd(),"..","prompts"))
model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
knowledge_base_id = os.environ["KNOWLEDGE_BASE_ID"]

def get_summary_retrieval(user_input,new_property):
    template_filename = "property-question-summary.txt"
    environment = Environment(loader=FileSystemLoader(template_dir))
    template = environment.get_template(template_filename)
    prompt = template.render(
        new_property_context = new_property,
        user_input=user_input
    )
    message={"role": "user","content": prompt}
    messages = [message]
    body=json.dumps(
    {
        'messages':messages,
        'anthropic_version':'bedrock-2023-05-31',
        'top_p':0.5,
        'temperature':0.5,
        'top_k':5,
        'max_tokens':3000
    })
    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        contentType='application/json',
        accept='application/json',
        body=body
    )
    response_body = json.loads(response['body'].read())
    return prompt

def get_relevent_docs(input_summary): 
    retrieval_response = bedrock_agent.retrieve(
        knowledgeBaseId=knowledge_base_id,
        retrievalQuery={"text":input_summary}
    )
    retrieval_rel_info = "\n\n".join(x["content"]["text"] for x in retrieval_response["retrievalResults"])
    return retrieval_rel_info

def get_user_answer(user_input,new_property,retrieval_rel_info):
    template_filename = "property-graph-prompt-goals-match-addr-template.txt"
    environment = Environment(loader=FileSystemLoader(template_dir))
    template = environment.get_template(template_filename)
    prompt = template.render(
        new_property_context = new_property,
        user_input=user_input,
        other_property_context=retrieval_rel_info
    )
    message={"role": "user","content": prompt}
    messages = [message]
    body=json.dumps(
    {
        'messages':messages,
        'anthropic_version':'bedrock-2023-05-31',
        'top_p':0.5,
        'temperature':0.5,
        'top_k':5,
        'max_tokens':3000
    })
    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        contentType='application/json',
        accept='application/json',
        body=body
    )
    response_body = json.loads(response['body'].read())
    return prompt

def main():
    new_property = open(os.path.abspath(os.path.join(os.getcwd(),"..","demo/graphs/loans & properties sample_5.txt")),"r").read()
    user_input = "Have we seen this property before, if so, what was the lender name?"
    input_summary = get_summary_retrieval(user_input,new_property)
    retrieval_rel_info=get_relevent_docs(input_summary)
    user_answer = get_user_answer(user_input,new_property,retrieval_rel_info)

main()