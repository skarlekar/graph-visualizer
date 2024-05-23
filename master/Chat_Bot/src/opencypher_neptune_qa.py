from langchain_community.graphs import NeptuneGraph
from langchain.chains import NeptuneOpenCypherQAChain
from langchain_community.chat_models import BedrockChat
from langchain_core.prompts import PromptTemplate
import boto3
import os
from langchain.chains.graph_qa.prompts import (
        CYPHER_QA_TEMPLATE
)


host = os.getenv("NEPTUNE_HOST")
port = 8182
use_https = True
region = 'us-east-1'

graph = NeptuneGraph(host=host, port=port, use_https=use_https, region_name=region)


bedrock_runtime = boto3.client("bedrock-runtime", region_name='us-east-1')
modelId = "anthropic.claude-3-sonnet-20240229-v1:0"
llm = BedrockChat(model_id=modelId, client=bedrock_runtime, model_kwargs={"temperature": 0})


prompt_dir = os.path.abspath(os.path.join(os.getcwd(),"../","prompts"))
prompt_file_name = "cypher-qa-context-examples.txt"
prompt_ex=open(os.path.join(prompt_dir,prompt_file_name),"r").read()+"\nHere is another example\n"
cypher_qa_mod_template = CYPHER_QA_TEMPLATE.replace("Here is an example",prompt_ex)
qa_prompt = PromptTemplate(input_variables=["context","question"],template=cypher_qa_mod_template)

opencypher_examples = open(os.path.join(prompt_dir,"cypher-generation-examples.txt"), "r").read()

chain = NeptuneOpenCypherQAChain.from_llm(llm=llm, graph=graph, verbose=True, qa_prompt=qa_prompt,extra_instructions=opencypher_examples)

questions = ["Have we seen Sample Gardens property and address before? If yes, what was the loan approval decision?", "Does Sample Gardens advance housing goals?","Does Sample Gardens qualify for a green loan?"]
for q in questions:
    print(q)
    chain_response=chain.invoke(q)
    print(chain_response)
