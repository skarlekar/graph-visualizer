import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.chat_models import BedrockChat
from rdflib import Graph, Literal
from rag-chat-property import main
import boto3

bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

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

example_graph = """<mf:Property1> a mf:Property ;
	mf:hasAddress <mf:PropertyAddress1> ;
	mf:hasName "College Courtyard Apartments & Raider Housing" ;
	mf:hasOwner "Northwest Florida State College Foundation" ;
	mf:hasPCR "4" ;
	mf:hasPropertyInspectionAgency "florida property inspection llc" ;
	mf:hasPropertyInspector "john d. goodhouse" ;
	mf:hasInspectionDate "01/03/2018" ;
	mf:hasUnits "62"^^xsd:int .

<mf:PropertyAddress1> a mf:PropertyAddress ;
	mf:hasCity "niceville" ;
	mf:hasState "fl" ;
	mf:hasStreetName "garden lane" ;
	mf:hasStreetNumber "28",
	  "30" ;
	mf:hasZip "32578" ;
	mf:hasLowIncomeUnits "12" ;
	mf:hasVeryLowIncomeUnits "5" ;
	mf:isSmallMultifamilyUnitMeetingLowIncome "yes" ;
	mf:hasMSA "" .
 """

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
    response = main(prompt)

    # Display model response
    with st.chat_message("assistant"):
        st.markdown(response)
    
    # Now add model response to chat history
    st.session_state.messages.append({"role":"assistant","content":response})
