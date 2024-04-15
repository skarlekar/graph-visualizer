import streamlit as st

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.chat_models import BedrockChat
import boto3

from prompts import construct_prompt

import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

from rdflib import Graph, Literal

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

def connect_to_bedrock():
    boto_session = boto3.Session()
    aws_region = boto_session.region_name
    bedrock_runtime = boto_session.client("bedrock-runtime", region_name='us-east-1')
    
    modelId = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    llm = BedrockChat(model_id=modelId, client=bedrock_runtime, model_kwargs={"temperature": 0})
    
    bedrock_agent = boto_session.client('bedrock-agent-runtime', region_name='us-east-1')
    
    return llm, bedrock_agent

def main():
    llm, bedrock_agent = connect_to_bedrock()
    file_link = st.text_input(
        label="Document Link", 
        key="file_link", 
        value="https://raw.githubusercontent.com/skarlekar/graph-visualizer/1927533f5b79fd1fd529944d77462553e7fe9bde/content/Appraisal-Report.pdf"
    )

    ontology_link = st.text_input(
        label="Ontology Link", 
        key="ontology_link",
        value="https://raw.githubusercontent.com/skarlekar/graph-visualizer/main/ontologies/PropertyAppraisalOntology-v2.ttl"
    )

    col1, col2 = st.columns([0.6, 0.4])

    with col1:
        if st.button("Generate Graph"):
            if file_link and ontology_link:

                ontology_graph = Graph()
                ontology_graph.parse(ontology_link, format="ttl")
                ontology = ontology_graph.serialize(format="ttl")


                loader = PyPDFLoader(file_link)
                texts = loader.load()

                tab1, tab2, tab3, tab4 = st.tabs(["Graph 1", "Graph 2", "Graph3", "Merged Graph"])

                with tab1:
                    prompt1 = construct_prompt(ontology=ontology, text=texts[0].page_content)
                    response1 = llm.invoke(input=prompt1)
                    g1 = Graph()
                    g1.parse(data=response1.content, format='ttl')
                    #st.text(g1.serialize(format='ttl'))

                    g1_l = Graph()
                    for s, p, o in g1:
                        if 'mf:' not in o:
                            g1_l.add((s, p, Literal(o.lower())))
                        else:
                            g1_l.add((s, p, o))
                    st.text("*************************")
                    st.text(g1_l.serialize(format='ttl'))
                    
                
                with tab2:
                    prompt2 = construct_prompt(ontology=ontology, text=texts[1].page_content)
                    response2 = llm.invoke(input=prompt2)
                    g2 = Graph()
                    g2.parse(data=response2.content, format='ttl')
                    #st.text(g2.serialize(format='ttl'))

                    g2_l = Graph()
                    for s, p, o in g2:
                        if 'mf:' not in o:
                            g2_l.add((s, p, Literal(o.lower())))
                        else:
                            g2_l.add((s, p, o))
                    st.text("*************************")
                    st.text(g2_l.serialize(format='ttl'))
                    
                
                with tab3:
                    prompt3 = construct_prompt(ontology=ontology, text=texts[3].page_content)
                    response3 = llm.invoke(input=prompt3)
                    
                    g3 = Graph()
                    g3.parse(data=response3.content, format='ttl')
                    #st.text(g3.serialize(format='ttl'))

                    g3_l = Graph()
                    for s, p, o in g3:
                        if 'mf:' not in o:
                            g3_l.add((s, p, Literal(o.lower())))
                        else:
                            g3_l.add((s, p, o))
                    st.text("*************************")
                    st.text(g3_l.serialize(format='ttl'))
                
                with tab4:
                    #g4 = g1 + g2
                    #st.text(g4.serialize(format='ttl'))

                    g4_l = g1_l|g2_l
                    g4_l.serialize(destination='merged-graph.ttl')
                    st.text("*************************")
                    st.text(g4_l.serialize(format='ttl'))

                    s3_client = boto3.client('s3')
                    #response = s3_client.upload_file('merged-graph.ttl', 'kg-merged-rdf', 'merged-graph.ttl')
            else:
                st.error('Document or ontology is missing', icon="🚨")
    
    with col2:
        def get_model_response(user_input):
            # Write code to call model here
            response = bedrock_agent.retrieve_and_generate(
                input={'text': user_input},
                retrieveAndGenerateConfiguration={
                    'type': 'KNOWLEDGE_BASE',
                    'knowledgeBaseConfiguration': {
                        'knowledgeBaseId': "PI1IJJBF84",
                        'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0'
                        }
                    }
                )
            return response['output']['text']

        # Init chatbot history
        if "messages" not in st.session_state:
            st.session_state.messages=[]

        # Display the previous messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # React to user input
        if prompt := st.chat_input("Type your question here"):

            # Display the user message
            st.chat_message("user").markdown(prompt)
            # Add user message to chat history
            st.session_state.messages.append({"role":"user","content":prompt})

            # Call model using user prompt
            response = get_model_response(prompt)

            # Display model response
            with st.chat_message("assistant"):
                st.markdown(response)
            
            # Now add model response to chat history
            st.session_state.messages.append({"role":"assistant","content":response})

            st.rerun()

if __name__ == '__main__':
    st.set_page_config(layout="wide")
    authenticate()
