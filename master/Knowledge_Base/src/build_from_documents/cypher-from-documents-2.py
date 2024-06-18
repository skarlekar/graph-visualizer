from langchain_core.prompts import PromptTemplate
from langchain_community.chat_models import BedrockChat
from rdflib import Graph
import os
import boto3

from textractor import Textractor
from textractor.data.text_linearization_config import TextLinearizationConfig
from textractcaller.t_call import Textract_Features

#file_path="../../data/documents/High_Performance_Building_Report.pdf"
doc_hpbr = "High_Performance_Building_Report.pdf"
doc_ga = "GreenPoint_Green_Assessment.pdf"
template_path = "../../prompts/cypher-from-document-template-2.txt"
template_text=open(template_path,"r").read()
template = PromptTemplate.from_template(template_text)

examples_path = "../../prompts/cypher-from-document-template-examples.txt"
examples = open(examples_path,"r").read()

onto_hpbr = "https://raw.githubusercontent.com/skarlekar/graph-visualizer/main/master/Knowledge_Base/ontologies/high-performance-building-report.ttl"
onto_ga = "https://raw.githubusercontent.com/skarlekar/graph-visualizer/main/master/Knowledge_Base/ontologies/green-assessment.ttl"

def get_ontology(ontology_link):
    g = Graph()
    g.parse(ontology_link, format='ttl')
    ontology = g.serialize(format='ttl')
    return ontology

def connect_to_bedrock():
    boto_session = boto3.Session()
    aws_region = boto_session.region_name
    bedrock_runtime = boto_session.client("bedrock-runtime", region_name="us-east-1")
    
    modelId = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    llm = BedrockChat(model_id=modelId, client=bedrock_runtime, model_kwargs={"temperature": 0,"top_k":250,"max_tokens":3000})
    return llm

llm = connect_to_bedrock()

def get_text(doc):
    extractor = Textractor(region_name='us-east-1')
    response = extractor.start_document_analysis(
        file_source=f"s3://kg-input-data/{doc}",
        features=[Textract_Features.LAYOUT, Textract_Features.TABLES],
        save_image=False
    )
    
    config = TextLinearizationConfig(
        table_linearization_format='markdown',
        table_prefix='\n<TABLE>\n\n',
        table_suffix='\n</TABLE>\n\n',
        section_header_prefix='<SECTION>\n\n',
        section_header_suffix='\n\n</SECTION>'
    )
    
    text = response.get_text()
    return text

def main(doc, onto_link):
    ontology = get_ontology(onto_link)
    content = get_text(doc1)
    
    prompt = template.invoke({"neptune_schema":ontology,"content":content,"examples":examples})
    response = llm.invoke(input=prompt)
    
    print(response.content)
