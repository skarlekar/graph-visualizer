import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.chat_models import BedrockChat
from rdflib import Graph, Literal

if 'kg_input_document' not in st.session_state:
    st.session_state.kg_input_document= None

def get_knowledge_graph_input_doc(file_link,ontology_link):
    print("Call to llm!")
    ontology_graph = Graph()
    ontology_graph.parse(ontology_link, format="ttl")
    ontology = ontology_graph.serialize(format="ttl")

    loader = PyPDFLoader(file_link)
    texts = loader.load()

    return "example graph"

def get_model_response(user_input):
    # Write code to call model here
    return "mock model response"

with st.sidebar:
    with st.form('document'):
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
    response = get_model_response(prompt)

    # Display model response
    with st.chat_message("assistant"):
        st.markdown(response)
    
    # Now add model response to chat history
    st.session_state.messages.append({"role":"assistant","content":response})