import io
import requests
import boto3
from langchain_community.chat_models import BedrockChat
from langchain_core.prompts import PromptTemplate
from rdflib import Graph, Namespace
import os

from textractor import Textractor
from textractor.data.text_linearization_config import TextLinearizationConfig
from textractcaller.t_call import Textract_Features


def loader(ontology_link):
    s3 = boto3.resource("s3", region_name='us-east-1')
    
    bucket = "kg-ontologies"
    key = ontology_link
    obj = s3.Object(bucket,key)
    ontology_txt=obj.get()["Body"].read().decode("utf-8")
    
    ontology_graph = Graph()
    ontology_graph.parse(data=ontology_txt, format='ttl')
    ontology = ontology_graph.serialize(format='ttl')
    return ontology

def extract_text(doc):
    content_ls = []
    documents = []
    
    extractor = Textractor(region_name='us-east-1')
    response = extractor.start_document_analysis(
        file_source=f"s3://kg-input-doc/{doc}",
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
    num_pages = response.document.num_pages
    
    for i in range(num_pages):
        text = response.document.page(i).get_text(config)
        documents.append(text)

        if len(documents) == 200:
            content = "\\n".join(documents)
            content_ls.append(content)
            documents = [] # reset the documents list
    if documents:
        content = "\\n".join(documents)
        content_ls.append(content)
    
    return content_ls

def get_rdf_graph(content, ontology):
    prompt_dir = os.path.abspath(os.path.join(os.getcwd(),"../","prompts"))
    prompt_template = open(os.path.join(prompt_dir,"rdf-extraction-prompt.txt"), "r").read()
    prompt = PromptTemplate(input_variables=["context","ontology"],template=prompt_template)
    
    
    bedrock_runtime = boto3.client("bedrock-runtime", region_name='us-east-1')
    modelId = "anthropic.claude-3-sonnet-20240229-v1:0"
    llm = BedrockChat(model_id=modelId, client=bedrock_runtime, model_kwargs={"temperature": 0})

    response = llm.invoke(input=prompt.format(content=content,ontology=ontology))
    return response.content

def create_and_combine_graphs(content_list, ontology):
    final_graph = Graph()
    final_graph.bind('mf', Namespace("http://example.org/multifamily#"))

    for content in content_list:
        rdf_graph_string = get_rdf_graph(content, ontology)
        graph = Graph()
        graph.parse(data=rdf_graph_string, format='ttl')  # Parse each string as Turtle format
        final_graph += graph  # Combine the graphs

    return final_graph

def extract(doc_link, ontology_link):
    ontology = loader(ontology_link)
    content_ls = extract_text(doc_link)
    rdf_graph = create_and_combine_graphs(content_list=content_ls, ontology=ontology)
    result = rdf_graph.serialize(format='ttl')
    return rdf_graph

if __name__ == '__main__':
    ontology_key = 'underwriting-narrative.ttl'
    doc_key = 'MFRUnderwritingTemplate-Example.pdf'
    #graph = extract(doc_link=doc_key, ontology_link=ontology_key)
    #print(graph)
