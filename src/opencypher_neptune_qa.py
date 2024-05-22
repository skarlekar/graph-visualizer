from langchain_community.graphs import NeptuneGraph
from langchain.chains import NeptuneOpenCypherQAChain
from langchain_community.chat_models import BedrockChat
from langchain_core.prompts import PromptTemplate
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

<question>
Does Happy Apartments advance housing goals?
</question>

MATCH (p:Property {hasPropertyName: 'Happy Apartments'})-[:hasPropertyAddress]-> (a)
RETURN p.hasUnits AS totalUnits, a.hasLowIncomeUnits AS lowIncomeUnits, a.hasVeryLowIncomeUnits AS veryLowIncomeUnits

<question>
Does Happy Apartments qualify for a green loan?
</question>

MATCH (p:Property {hasPropertyName: 'Happy Apartments'})
RETURN p.hasGreenBuildingCertification AS greenBuildingCertification, p.hasGreenBuildingCertificationAgency AS greenBuildingCertificationAgency, p.hasGreenBuildingUpgrades AS greenBuildingUpgrades, p.annualEnergyConsumptionReductionCommitment AS annualEnergyConsumptionReductionCommitment, p.annualWaterConsumptionReductionCommitment AS annualWaterConsumptionReductionCommitment 

</Examples>
"""

# Prompt from Langchain
qa_from_cypher_template = """You are an assistant that helps to form nice and human understandable answers.
The information part contains the provided information that you must use to construct an answer.
The provided information is authoritative, you must never doubt it or try to use your internal knowledge to correct it.
Make the answer sound as a response to the question. Do not mention that you based the result on the given information.
Here is an example:

Question: Which managers own Neo4j stocks?
Context:[manager:CTL LLC, manager:JANE STREET GROUP LLC]
Helpful Answer: CTL LLC, JANE STREET GROUP LLC owns Neo4j stocks.

Follow this example when generating answers.
If the provided information is empty, say that you don't know the answer.
Information:
{context}

Question: {question}
Helpful Answer:"""
qa_mock_query="Always respond with this is a test response"

#qa_prompt = PromptTemplate.from_template(qa_from_cypher_template)
qa_prompt = PromptTemplate.from_template(template=qa_mock_query)
print(qa_prompt)
chain = NeptuneOpenCypherQAChain.from_llm(llm=llm, graph=graph, verbose=True, qa_prompt=qa_prompt,extra_instructions=opencypher_examples)
chain2 = NeptuneOpenCypherQAChain.from_llm(llm=llm, graph=graph, verbose=True, extra_instructions=opencypher_examples)
chain.invoke("how many properties do we have?")
chain2.invoke("how many properties do we have?")
