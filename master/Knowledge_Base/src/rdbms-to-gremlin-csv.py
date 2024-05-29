import pandas as pd
import boto3
from langchain_community.chat_models import BedrockChat
import json

def connect_to_bedrock():
    boto_session = boto3.Session()
    aws_region = boto_session.region_name
    bedrock_runtime = boto_session.client("bedrock-runtime", region_name="us-east-1")

    modelId = "anthropic.claude-3-sonnet-20240229-v1:0"

    llm = BedrockChat(model_id=modelId, client=bedrock_runtime, model_kwargs={"temperature": 0})
    return llm

def main():
    table_locations={
            "Loan":"../data/structured-data/Loan-data.csv",
            "Property":"../data/structured-data/Property-data.csv",
            "Underwriting":"../data/structured-data/Underwriting-data.csv",
            "Inspection":"../data/structured-data/Inspection-data.csv"
    }
    llm = connect_to_bedrock()
    vertices_prompt = open("../prompts/gremlin-vertices-headers-from-sql","r").read()
    response = llm.invoke(input=vertices_prompt)
    vertices_mapping = json.dumps(response.content)
    print(vertices_mapping)

if __name__ == '__main__':
    main()
