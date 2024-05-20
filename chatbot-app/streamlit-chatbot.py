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
    
pre_loaded_graph = """
@prefix ns1: <http://example.org/multifamily#> .

ns1:SampleGardens a ns1:Property ;
  ns1:hasLender ns1:MidCityBank ;
  ns1:hasLenderContact ns1:WallyLendor ;
  ns1:hasLoanType ns1:ConventionalLoan ;
  ns1:hasManagementAddress ns1:OwnerAddress ;
  ns1:hasManagementAgent ns1:NSPManagementPartners ;
  ns1:hasManagementContact ns1:SusanDeveloper ;
  ns1:hasNonRevenueUnits ns1:1NonRevenueUnit ;
  ns1:hasOwnerAddress ns1:OwnerAddress ;
  ns1:hasOwnerContact ns1:SusanDeveloper ;
  ns1:hasOwnerEntity ns1:NSPDevelopmentPartners ;
  ns1:hasPropertyAddress ns1:SampleGardensAddress ;
  ns1:hasPropertyName "Sample Gardens" ;
  ns1:hasTotalRentalUnits ns1:100RentalUnits ;
  ns1:hasTotalUnits ns1:101TotalUnits;
  mf:hasPCR "3" ;
  mf:hasPropertyInspectionAgency "urgent inspection llc" ;
  mf:hasPropertyInspector "Jane Jones" ;
  mf:hasInspectionDate "03/07/2020" ;
  mf:hasUnits "101"^^xsd:int;
  mf:hasGreenBuildingCertification "yes";
  mf:hasGreenBuildingCertificationAgency "BREEAM USA";
  mf:hasGreenBuildingUpgrades "Energy Start Appliances", "Energy efficient LED lighting";
  mf:annualEnergyConsumptionReductionCommitment "25%";
  mf:annualWaterConsumptionReductionCommitment "30%".

ns1:100RentalUnits a ns1:TotalRentalUnits .

ns1:101TotalUnits a ns1:TotalUnits .

ns1:1NonRevenueUnit a ns1:NonRevenueUnits .

ns1:ConventionalLoan a ns1:LoanType .

ns1:MidCityBank a ns1:Lender .

ns1:NSPDevelopmentPartners a ns1:OwnerEntity .

ns1:NSPManagementPartners a ns1:ManagementAgent .

ns1:SampleGardensAddress a ns1:PropertyAddress ;
  ns1:hasCity "Mid City" ;
  ns1:hasState "Ohio" ;
  ns1:hasStreetAddress "123 Sample Street" ;
  ns1:hasZipCode "23445";
  mf:hasLowIncomeUnits "20" ;
  mf:hasVeryLowIncomeUnits "10" ;
  mf:isSmallMultifamilyUnitMeetingLowIncome "yes" ;
  mf:hasMSA "" .

ns1:WallyLendor a ns1:LenderContact ;
  ns1:hasEmail "wlendor@MCB.com" ;
  ns1:hasName "Wally Lendor" ;
  ns1:hasPhone "(215) 555-1214" .

ns1:SusanDeveloper a ns1:OwnerContact ;
  ns1:hasEmail "susan@NSPDP.com" ;
  ns1:hasName "Susan Developer" ;
  ns1:hasPhone "(215) 555-1212" .

ns1:OwnerAddress a ns1:OwnerAddress ;
  ns1:hasCity "Mid City" ;
  ns1:hasState "Ohio" ;
  ns1:hasStreetAddress "600 Main Street" ;
  ns1:hasZipCode "23445" .
"""

def get_knowledge_graph_input_doc(file_link,ontology_link):
    print("Call to llm!")
    #graph = extract(file_link, ontology_link)
    return pre_loaded_graph

example_graph = ""

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

        option = st.selectbox(
        'Document Type',
        ('Underwriting Narrative', 'High Performance Building Assesment', 'Appraisal Report', 'MAE data', 'PCA Report'))
        
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
    response = response.replace("<newPropertyContext>", "Underwriting Narrative Document")
    response = response.replace("<otherPropertyContext>", "Loan and Property Knowledgebase")

    # Display model response
    with st.chat_message("assistant"):
        st.markdown(response)
    
    # Now add model response to chat history
    st.session_state.messages.append({"role":"assistant","content":response})
