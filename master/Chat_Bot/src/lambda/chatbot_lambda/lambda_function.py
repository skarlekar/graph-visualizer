from langchain_community.graphs import NeptuneGraph
from langchain.chains import NeptuneOpenCypherQAChain
from langchain_community.chat_models import BedrockChat
from langchain_core.prompts import PromptTemplate
import boto3
import os
from langchain.chains.graph_qa.prompts import (
        CYPHER_QA_TEMPLATE
)
import json


def lambda_handler(event, context):
    # TODO implement
    host = os.getenv("neptuneHost")
    port = os.getenv("neptunePort")
    use_https = True
    region = 'us-east-1'

    graph = NeptuneGraph(host=host, port=port, use_https=use_https, region_name=region)


    bedrock_runtime = boto3.client("bedrock-runtime", region_name='us-east-1')
    modelId = "anthropic.claude-3-sonnet-20240229-v1:0"
    llm = BedrockChat(model_id=modelId, client=bedrock_runtime, model_kwargs={"temperature": 0})


    prompt_dir = "chatbot_lambda/prompts"
    prompt_file_name = "cypher-qa-context-examples.txt"
    prompt_ex=open(os.path.join(prompt_dir,prompt_file_name),"r").read()+"\nHere is another example\n"
    cypher_qa_mod_template = CYPHER_QA_TEMPLATE.replace("Here is an example",prompt_ex)
    qa_prompt = PromptTemplate(input_variables=["context","question"],template=cypher_qa_mod_template)

    opencypher_examples = open(os.path.join(prompt_dir,"cypher-generation-examples.txt"), "r").read()

    chain = NeptuneOpenCypherQAChain.from_llm(llm=llm, graph=graph, verbose=True, qa_prompt=qa_prompt,extra_instructions=opencypher_examples)
    
    query = event['query']
    response = chain.invoke(query)
    
    return {
        'statusCode': 200,
        'body': json.dumps(response['result'])
    }