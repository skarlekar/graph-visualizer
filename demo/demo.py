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

from rdflib import Graph


def connect_to_bedrock():
    boto_session = boto3.Session()
    aws_region = boto_session.region_name
    bedrock_runtime = boto_session.client("bedrock-runtime", region_name=aws_region)
    
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

        ontology = st.text_area(
            label="Ontology TTL",
            height=400,
            value=get_ontology(),
        )

    with col2:
        if st.button("Generate Graph"):
            if file_link and ontology:
                loader = PyPDFLoader(file_link)
                #pages = loader.load_and_split()
                doc = loader.load()
                texts = split_documents(chunk_size=1000, document=doc)

                tab1, tab2, tab3 = st.tabs(["Graph 1", "Graph 2", "Merged Graph"])

                with tab1:
                    prompt = construct_prompt(ontology=ontology, text=texts[0].page_content)
                    response = llm.invoke(input=prompt)
                    g1 = Graph()
                    g1.parse(data=response.content, format='turtle')
                    st.text(f"""{g1.serialize(format='turtle')}""")
                
                with tab2:
                    prompt2 = construct_prompt(ontology=ontology, text=texts[1].page_content)
                    response2 = llm.invoke(input=prompt2)
                    g2 = Graph()
                    g2.parse(data=response2.content, format='turtle')
                    st.text(f"""{g2.serialize(format='turtle')}""")
                
                with tab3:
                    g3 = g1 + g2
                    st.text(f"""{g3.serialize(format='turtle')}""")
            else:
                st.error('Document or ontology is missing', icon="🚨")

if __name__ == '__main__':
    st.set_page_config(layout="wide")
    authenticate()
