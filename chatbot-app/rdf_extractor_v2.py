from PIL import Image
import io
import fitz
import requests
import boto3
from langchain_community.document_loaders import AmazonTextractPDFLoader
from langchain_community.chat_models import BedrockChat
from rdflib import Graph


def loader(doc_link, ontology_link):
    res = requests.get(doc_link)
    doc = fitz.open(stream=res.content, filetype="pdf")

    res2 = requests.get(ontology_link)
    ontology = res2.text
    return doc, ontology

def get_images(doc):
    for i in range(len(doc)):
        # load the page
        page = doc.load_page(i)

        # render the page as a png image
        pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))

        # save the png image
        output_path = f"images/page_{i}.png"
        pix.save(output_path)

def extract_text(doc):
    client = boto3.client(service_name='textract', region_name='us-east-1')
    content_ls = []
    documents = []
    for i in range(len(doc)):
        loader = AmazonTextractPDFLoader(
            f"images/page_{i}.png",
            client=client
        )
        docs = loader.load()
        documents.append(docs[0].page_content)

        if len(documents) == 20:
            content = "\\n".join(documents)
            content_ls.append(content)
            documents = [] # reset the documents list
    if documents:
        content = "\\n".join(documents)
        content_ls.append(content)
    return content_ls

def get_rdf_graph(content, ontology):
    prompt = f"""
    Instructions: Use only the context provided in the <context> tags and ontology provided in the <ontology> tags to perform your task.
    <context>
    {content}
    </content>

    <ontology>
    {ontology}
    </ontology>

    Task: Generate an RDF Graph using the provided context and ontology. Do not provide any explanation or description.
    """
    
    bedrock_runtime = boto3.client("bedrock-runtime", region_name='us-east-1')
    modelId = "anthropic.claude-3-sonnet-20240229-v1:0"
    llm = BedrockChat(model_id=modelId, client=bedrock_runtime, model_kwargs={"temperature": 0})

    response = llm.invoke(input=prompt)
    return response.content

def create_and_combine_graphs(content_list, ontology):
    final_graph = Graph()

    for content in content_list:
        rdf_graph_string = get_rdf_graph(content, ontology)
        rdf_graph_string = "@prefix rdfs: <http://www.w3.org/1999/02/22-rdf-syntax-ns2#> .\n" + rdf_graph_string
        graph = Graph()
        graph.parse(data=rdf_graph_string, format="turtle")  # Parse each string as Turtle format
        final_graph += graph  # Combine the graphs

    return final_graph

def extract(doc_link, ontology_link):
    doc, ontology = loader(doc_link, ontology_link)
    get_images(doc)
    content_ls = extract_text(doc)
    rdf_graph = create_and_combine_graphs(content_list=content_ls, ontology=ontology)
    result = rdf_graph.serialize(format='ttl')
    return result

if __name__ == '__main__':
    ontology_link = 'https://raw.githubusercontent.com/skarlekar/graph-visualizer/main/ontologies/ontology-uw-narrative.txt'
    doc_link = 'https://files.hudexchange.info/resources/documents/MFRUnderwritingTemplate-Example.pdf'
    graph = extract(doc_link=doc_link, ontology_link=ontology_link)
    print(graph)