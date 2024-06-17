from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_models import BedrockChat
from langchain_community.graphs import NeptuneGraph
from rdflib import Graph
import os
import boto3

file_path="../../data/documents/High_Performance_Building_Report.pdf"
template_path = "../../prompts/cypher-from-document-template-2.txt"
template_text=open(template_path,"r").read()
template = PromptTemplate.from_template(template_text)

examples_path = "../../prompts/cypher-from-document-template-examples.txt"
examples = open(examples_path,"r").read()

g = Graph()
g.parse("https://raw.githubusercontent.com/skarlekar/graph-visualizer/main/master/Knowledge_Base/ontologies/high-performance-building-report.ttl", format='ttl')
ontology = g.serialize(format='ttl')

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
content = ""
for page in pages:
  content += page.page_content

#prompt = template.invoke({"neptune_schema":graph.get_schema,"content":content,"examples":examples})
prompt = template.invoke({"neptune_schema":ontology,"content":content,"examples":examples})
print(prompt)
print("\n\n\n")
response = llm.invoke(input=prompt)
print(response.content)
