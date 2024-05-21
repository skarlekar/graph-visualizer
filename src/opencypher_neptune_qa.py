from langchain_community.graphs import NeptuneGraph
from langchain.chains import NeptuneOpenCypherQAChain
from langchain_community.chat_models import BedrockChat
import boto3
import os


host = os.getenv("NEPTUNE_HOST")
port = 8182
use_https = True
region = 'us-east-1'

graph = NeptuneGraph(host=host, port=port, use_https=use_https, region_name=region)


bedrock_runtime = boto3.client("bedrock-runtime", region_name='us-east-1')
modelId = "anthropic.claude-3-sonnet-20240229-v1:0"
llm = BedrockChat(model_id=modelId, client=bedrock_runtime, model_kwargs={"temperature": 0})

opencypher_examples = """
<Examples>
<question>
Who is the property inspector for Sample Gardens?
</question>

MATCH (p:Property {hasPropertyName: 'Sample Gardens'})
RETURN p.hasPropertyInspector AS property_inspector

<question>
What is the address for Sample Gardens?
</question>

MATCH (p:Property {hasPropertyName: 'Sample Gardens'})-[:hasPropertyAddress]-> (d)
RETURN d AS property_address

<question>
Does Sample Gardens have Green Building Certfication?
</question>

MATCH (p:Property {hasPropertyName: 'Sample Gardens'})
RETURN p.hasGreenBuildingCertification AS green_building_certification

<question>
Who is the lender for Sample Gardens?
</question>

MATCH (p:Property {hasPropertyName: 'Sample Gardens'})-[:hasLender]-> (d)
RETURN d AS lender

</Examples>
"""

chain = NeptuneOpenCypherQAChain.from_llm(llm=llm, graph=graph, verbose=True)

chain.invoke("How many units does Sample Gardens property have?")
