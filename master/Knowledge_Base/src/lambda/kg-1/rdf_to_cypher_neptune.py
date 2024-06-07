import boto3
from langchain_community.chat_models import BedrockChat
from langchain_community.graphs import NeptuneGraph
from langchain_core.prompts import PromptTemplate
import json
import os
from io import StringIO


host = os.getenv("neptuneEndpoint")
port = 8182
use_https = True
region = 'us-east-1'

graph = NeptuneGraph(host=host, port=port, use_https=use_https, region_name=region)

def connect_to_bedrock():
  boto_session = boto3.Session()
  aws_region = boto_session.region_name
  bedrock_runtime = boto_session.client("bedrock-runtime", region_name="us-east-1")

  modelId = "anthropic.claude-3-sonnet-20240229-v1:0"

  llm = BedrockChat(model_id=modelId, client=bedrock_runtime, model_kwargs={"temperature": 0,"max_tokens":3000})
  return llm

def get_cypher_query(rdf_data):
  template = open("knowledge_base_lambda/cypher-merge-rdf-template.txt", "r").read()
  prompt_template = PromptTemplate(input_variables=['rdf_data', 'neptune_schema'], template=template)
  cypher_gen_prompt=prompt_template.format(rdf_data=rdf_data,neptune_schema=graph.get_schema)
  #print(cypher_gen_prompt)
  llm = connect_to_bedrock()
  response = llm.invoke(input=cypher_gen_prompt)
  return response

def execute_cypher_query(cypher_query):
  graph.query(cypher_query)

def main(rdf_data):
  cypher_query = get_cypher_query(rdf_data)
  #print("\n\n\n\n\n")
  #print(cypher_query)
  #print(cypher_query.content)
  execute_cypher_query(cypher_query.content)

if __name__ == '__main__':
  main()
