from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_models import BedrockChat
from langchain_community.graphs import NeptuneGraph
import os
import boto3

file_path="../data/documents/MFRUnderwritingTemplate-Example.pdf"
template_path = "../prompts/cypher-from-document-template.txt"
template_text=open(template_path,"r").read()
template = PromptTemplate.from_template(template_text)

host = os.getenv("NEPTUNE_HOST")
port = 8182
use_https = True
region = 'us-east-1'

def connect_to_bedrock():
  boto_session = boto3.Session()
  aws_region = boto_session.region_name
  bedrock_runtime = boto_session.client("bedrock-runtime", region_name="us-east-1")

  modelId = "anthropic.claude-3-sonnet-20240229-v1:0"

  llm = BedrockChat(model_id=modelId, client=bedrock_runtime, model_kwargs={"temperature": 0,"top_k":250,"max_tokens":3000})
  return llm

graph = NeptuneGraph(host=host, port=port, use_https=use_https, region_name=region)
llm = connect_to_bedrock()

loader=PyPDFLoader(file_path)
pages = loader.load_and_split()
content = pages[5].page_content

prompt =template.invoke({"neptune_schema":graph.get_schema,"content":content})
print(prompt)
print("\n\n\n")
response = llm.invoke(input=prompt)
print(response.content)
