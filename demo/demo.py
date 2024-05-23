import streamlit as st

#from langchain_community.document_loaders import UnstructuredFileIOLoader
from langchain_community.document_loaders import PyPDFLoader

from docparser import split_documents
from prompts import construct_prompt
from ontology import get_ontology

from langchain_community.chat_models import BedrockChat
import boto3

import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

from rdflib import Graph, Literal


def connect_to_bedrock():
    boto_session = boto3.Session()
    aws_region = boto_session.region_name
    bedrock_runtime = boto_session.client("bedrock-runtime", region_name="us-east-1")
    
    modelId = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    llm = BedrockChat(model_id=modelId, client=bedrock_runtime, model_kwargs={"temperature": 0})
    return llm

def authenticate():
    with open('./config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )
    name, authentication_status, username = authenticator.login()
    if st.session_state["authentication_status"]:
        authenticator.logout('Logout', 'main', key='unique_key')
        with open('./config.yaml', 'w') as file:
            yaml.dump(config, file, default_flow_style=False)
        st.write(f'Welcome *{st.session_state["name"]}*')
        main()
    elif st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] is None:
        st.warning('Please enter your username and password')
    return name, authentication_status, username

def main():
    llm = connect_to_bedrock()

    col1, col2 = st.columns([0.4, 0.6])

    with col1:
        #uploaded_file = st.file_uploader("Choose a file")
        file_link = st.text_input(
            label="Document Link", 
            key="file_link", 
            value="https://raw.githubusercontent.com/skarlekar/graph-visualizer/1927533f5b79fd1fd529944d77462553e7fe9bde/content/Appraisal-Report.pdf"
        )

        #ontology = st.text_area(
        #    label="Ontology TTL",
        #    height=400,
        #    value=get_ontology(),
        #)
        ontology = st.text_input(
            label="Ontology TTL",
            key="ontology_link",
            value="https://raw.githubusercontent.com/skarlekar/graph-visualizer/main/ontologies/PropertyAppraisalOntology-v2.ttl"
        )

    with col2:
        if st.button("Generate Graph"):
            if file_link and ontology:
                loader = PyPDFLoader(file_link)
                doc = loader.load()
                #texts = split_documents(chunk_size=1000, document=doc)
                texts = doc

                o_graph = Graph()
                o_graph.parse("https://raw.githubusercontent.com/skarlekar/graph-visualizer/main/ontologies/PropertyAppraisalOntology-v2.ttl", format="ttl")
                ontology = o_graph.serialize(format="ttl")
                #ontology = ontology.replace("@prefix ns1: <https://raw.githubusercontent.com/skarlekar/graph-visualizer/main/ontologies/> .", "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n@prefix mf: <http://example.org/mf> .")

                tab1, tab2, tab3, tab4 = st.tabs(["Graph 1", "Graph 2", "Graph3", "Merged Graph"])

                with tab1:
                    prompt = construct_prompt(ontology=ontology, text=texts[0].page_content)
                    response = llm.invoke(input=prompt)
                    g1 = Graph()
                    g1.parse(data=response.content, format='turtle')
                    #st.text(g1.serialize(format='ttl'))

                    g1_l = Graph()
                    for s, p, o in g1:
                        if 'mf:' not in o:
                            g1_l.add((s, p, Literal(o.lower())))
                        else:
                            g1_l.add((s,  p, o))
                    st.text("**********************")
                    st.text(g1_l.serialize(format='ttl'))
                with tab2:
                    prompt2 = construct_prompt(ontology=ontology, text=texts[1].page_content)
                    response2 = llm.invoke(input=prompt2)
                    g2 = Graph()
                    g2.parse(data=response2.content, format='turtle')
                    #st.text(g2.serialize(format='ttl'))

                    g2_l = Graph()
                    for s, p, o in g2:
                        if 'mf:' not in o:
                            g2_l.add((s, p, Literal(o.lower())))
                        else:
                            g2_l.add((s, p, o))
                    st.text("************************")
                    st.text(g2_l.serialize(format='ttl'))
                with tab3:
                    prompt3 = construct_prompt(ontology=ontology, text=texts[3].page_content)
                    response3 = llm.invoke(input=prompt3)
                    g3 = Graph()
                    g3.parse(data=response3.content, format='turtle')
                    st.text(f"""{g3.serialize(format='turtle')}""")
                with tab4:
                    g4 = g1 + g2
                    #g4.serialize(destination='merged-graph.ttl')

                    g4_l = g1_l|g2_l
                    g4_l.serialize(destination='merged-graph.ttl')
                    st.text(g4_l.serialize(format='ttl'))
                    st.text('***************')

                    s3 = boto3.client('s3')
                    #response = s3.upload_file('merged-graph.ttl', 'kg-merged-rdf', 'merged-graph.ttl')

                    #st.text(g4.serialize(format='turtle'))
            else:
                st.error('Document or ontology is missing', icon="🚨")

if __name__ == '__main__':
    st.set_page_config(layout="wide")
    authenticate()
