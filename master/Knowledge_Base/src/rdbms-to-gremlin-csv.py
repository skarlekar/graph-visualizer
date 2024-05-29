import pandas as pd
import boto3

def connect_to_bedrock():
    boto_session = boto3.Session()
    aws_region = boto_session.region_name
    bedrock_runtime = boto_session.client("bedrock-runtime", region_name="us-east-1")

    modelId = "anthropic.claude-3-sonnet-20240229-v1:0"

    llm = BedrockChat(model_id=modelId, client=bedrock_runtime, model_kwargs={"temperature": 0})
    return llm

def main():
    llm = connect_to_bedrock()
    vertices_prompt = open("../prompts/gremlin-vertices-headers-from-sql","r").read()

if __name__ == '__main__':
    main()
