import boto3
import json
from jinja2 import Environment, FileSystemLoader
import sys
from pathlib import Path
import os

output_name = "query-kg-test1"
model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

template_dir = os.path.abspath(os.path.join(os.getcwd(),"../..","prompts-templates"))
output_dir = os.path.abspath(os.path.join(os.getcwd(),"../..","model-results"))
ontology_dir = os.path.abspath(os.path.join(os.getcwd(),"../..","ontologies"))
ontology_name = "PropertyAppraisalOntology-v2.ttl"

template_filename = "query-kg-prompt.txt"
bedrock_runtime= boto3.client("bedrock-runtime",region_name="us-east-1")

with open(os.path.join(ontology_dir,ontology_name),"r") as f:
    ontology = f.read()

question="What is the name of the property?"

environment = Environment(loader=FileSystemLoader(template_dir))
template = environment.get_template(template_filename)
prompt = template.render(
    ontology=ontology,
    question=question
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
print("Invoking model...")
response = bedrock_runtime.invoke_model(
    modelId=model_id,
    contentType='application/json',
    accept='application/json',
    body=body
)
response_body = json.loads(response['body'].read())
with open(os.path.join(output_dir,f"{output_name}.json"),"w+") as f:
    json.dump(response_body,f)