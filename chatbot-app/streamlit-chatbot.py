import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.chat_models import BedrockChat
from rdflib import Graph, Literal
import boto3
import importlib
from rdf_extractor_v2 import extract

ragchat = importlib.import_module('rag-chat-property')

bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

if 'kg_input_document' not in st.session_state:
    st.session_state.kg_input_document= None

def get_knowledge_graph_input_doc(file_link,ontology_link):
    print("Call to llm!")
    graph = extract(file_link, ontology_link)
    return graph

example_graph = ""

def get_model_response(user_input):
    # Write code to call model here
    response = bedrock_agent.retrieve_and_generate(
                input={'text': user_input},
                retrieveAndGenerateConfiguration={
                    'type': 'KNOWLEDGE_BASE',
                    'knowledgeBaseConfiguration': {
                        'knowledgeBaseId': "PI1IJJBF84",
                        'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0',
                        'generationConfiguration': {
                            'promptTemplate': {
                                'textPromptTemplate': f"""
                                Instructions: Use only the provided search results to answer the question at the end. Do not include any explanations in your response.
                                Search Results:
                                $search_results$
                                Question: 
                                I am providing a property and its address in the <context> tags:
                                <context>
                                {example_graph}
                                </context>
                                $query$
                                """
                                }
                            }
                        },
                    }
                )
    return response['output']['text']

with st.sidebar:
    with st.form('document'):
        file_link = st.text_input(
            label="Document Link", 
            key="file_link", 
            value="https://files.hudexchange.info/resources/documents/MFRUnderwritingTemplate-Example.pdf"
        )

        ontology_link = st.text_input(
            label="Ontology Link", 
            key="ontology_link",
            value="https://raw.githubusercontent.com/skarlekar/graph-visualizer/main/ontologies/ontology-uw-narrative.txt"
        )
        submit = st.form_submit_button("Submit")
        if submit:
            st.session_state.kg_input_document=get_knowledge_graph_input_doc(file_link,ontology_link)

    if not (st.session_state.kg_input_document):
        st.warning('Please submit your document information!', icon='⚠️')
    else:
        st.success('Proceed to enter your prompt message!', icon='👉')

# Init chatbot history
if "messages" not in st.session_state:
    st.session_state.messages=[]

# Display the previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Type your question here",disabled=not (st.session_state.kg_input_document)):

    # Display the user message
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role":"user","content":prompt})

    # Call model using user prompt
    print("kg_input_document **********")
    print(st.session_state.kg_input_document)
    response = ragchat.main(prompt, st.session_state.kg_input_document)
    response = response.replace("<modelResponse>", "")
    response = response.replace("</modelResponse>", "")

    # Display model response
    with st.chat_message("assistant"):
        st.markdown(response)
    
    # Now add model response to chat history
    st.session_state.messages.append({"role":"assistant","content":response})
