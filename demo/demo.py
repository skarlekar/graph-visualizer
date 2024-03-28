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
                #loader = PyPDFLoader(file_link)
                #doc = loader.load()
                #texts = split_documents(chunk_size=1000, document=doc)

                tab1, tab2, tab3, tab4 = st.tabs(["Graph 1", "Graph 2", "Graph3", "Merged Graph"])

                with tab1:
                    #prompt = construct_prompt(ontology=ontology, text=texts[0].page_content)
                    #response = llm.invoke(input=prompt)
                    #g1 = Graph()
                    #g1.parse(data=response.content, format='turtle')
                    st.text(f"""@prefix mf: <http://example.org/mf> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<mf:PropertyAppraisal_1> a mf:PropertyAppraisal ;
    mf:hasAppraisalNumber "190416" ;
    mf:hasAppraiser <mf:PropertyAppraiser_1>,
        <mf:PropertyAppraiser_2> ;
    mf:hasTitle "APPRAISAL REPORT" .

<mf:Property_1> a mf:Property ;
    mf:hasAddress <mf:PropertyAddress_1> ;
    mf:hasName "COLLEGE COURTYARD APARTMENTS & RAIDER HOUSING" ;
    mf:hasOwner "NORTHWEST FLORIDA STATE COLLEGE FOUNDATION" ;
    mf:hasUnits "62"^^xsd:int .

<mf:PropertyAddress_1> a mf:PropertyAddress ;
    mf:hasCity "NICEVILLE" ;
    mf:hasState "FL" ;
    mf:hasStreetName "GARDEN LANE" ;
    mf:hasStreetNumber "28",
        "30" ;
    mf:hasZip "32578" .

<mf:PropertyAppraiser_1> a mf:PropertyAppraiser ;
    rdfs:label "Jason P. Shirey, MAI, CCIM, CPM" ;
    mf:hasAppraisalLicense "RZ3186" .

<mf:PropertyAppraiser_2> a mf:PropertyAppraiser ;
    rdfs:label "Josette D. Jackson, CCIM" ;
    mf:hasAppraisalLicense "RZ3275" .""")
                
                with tab2:
                    #prompt2 = construct_prompt(ontology=ontology, text=texts[1].page_content)
                    #response2 = llm.invoke(input=prompt2)
                    #g2 = Graph()
                    #g2.parse(data=response2.content, format='turtle')
                    #st.text(f"""{g2.serialize(format='turtle')}""")
                    st.text(f"""@prefix mf: <http://example.org/mf> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<mf:Property1> a mf:Property ;
    mf:hasAddress <mf:PropertyAddress1> ;
    mf:hasAppraisal <mf:PropertyAppraisal1> ;
    mf:hasName "College Courtyard Apartments & Raider Housing" ;
    mf:hasOwner "Northwest Florida State College Foundation" ;
    mf:hasUnits "62"^^xsd:int .

<mf:PropertyInspectionDate1> a mf:PropertyInspectionDate ;
    mf:hasDay "N/A" ;
    mf:hasMonth "N/A" ;
    mf:hasYear "N/A" .

<mf:PropertyAddress1> a mf:PropertyAddress ;
    mf:hasCity "Niceville" ;
    mf:hasState "FL" ;
    mf:hasStreetName "Garden Lane" ;
    mf:hasStreetNumber "28",
        "30" ;
    mf:hasZip "32578" .

<mf:PropertyAppraisal1> a mf:PropertyAppraisal ;
    mf:hasAppraisedValue "N/A" ;
    mf:hasAppraiser "Jason P. Shirey, MAI, CCIM",
        "Josette D. Jackson, CCIM" ;
    mf:hasDate <mf:PropertyAppraisalDate1> ;
    mf:hasRemarks "Of Existing Multi-Family Property" ;
    mf:hasTitle "APPRAISAL REPORT" .

<mf:PropertyAppraisalDate1> a mf:PropertyAppraisalDate ;
    mf:hasDay 13 ;
    mf:hasMonth "December" ;
    mf:hasYear 2019 .""")
                
                with tab3:
                    #prompt3 = construct_prompt(ontology=ontology, text=texts[2].page_content)
                    #response3 = llm.invoke(input=prompt3)
                    #g3 = Graph()
                    #g3.parse(data=response3.content, format='turtle')
                    #st.text(f"""{g3.serialize(format='turtle')}""")
                    st.text(f"""@prefix mf: <http://example.org/mf> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<mf:Property1> a mf:Property ;
    mf:hasAddress <mf:PropertyAddress1> ;
    mf:hasAppraisal <mf:PropertyAppraisal1> ;
    mf:hasName "College Courtyard Apartments & Raider Housing" ;
    mf:hasOwner "Northwest Florida State College Foundation" ;
    mf:hasUnits "62"^^xsd:int .

<mf:PropertyAddress1> a mf:PropertyAddress ;
    mf:hasCity "Niceville" ;
    mf:hasState "FL" ;
    mf:hasStreetName "Garden Lane" ;
    mf:hasStreetNumber "28"^^xsd:string,
        "30"^^xsd:string ;
    mf:hasZip "32578" .

<mf:PropertyAppraisal1> a mf:PropertyAppraisal ;
    mf:hasAppraisedValue "Current Market Value" ;
    mf:hasAppraiser "EquiValue Appraisal LLC" ;
    mf:hasDate <mf:PropertyAppraisalDate1> ;
    mf:hasRemarks "File No. EQ 190416" ;
    mf:hasTitle "Appraisal of College Courtyard Apartments & Raider Housing" .

<mf:PropertyAppraisalDate1> a mf:PropertyAppraisalDate ;
    mf:hasDay "13"^^xsd:int ;
    mf:hasMonth "December" ;
    mf:hasYear "2019"^^xsd:int .""")
                
                with tab4:
                    #g4 = g1 + g2 + g3
                    #st.text(f"""{g4.serialize(format='turtle')}""")
                    st.text(f"""@prefix mf: <http://example.org/mf> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<mf:Property1> a mf:Property ;
    mf:hasAddress <mf:PropertyAddress1> ;
    mf:hasAppraisal <mf:PropertyAppraisal1> ;
    mf:hasName "College Courtyard Apartments & Raider Housing" ;
    mf:hasOwner "Northwest Florida State College Foundation" ;
    mf:hasUnits "62"^^xsd:int .

<mf:PropertyAppraisal_1> a mf:PropertyAppraisal ;
    mf:hasAppraisalNumber "190416" ;
    mf:hasAppraiser <mf:PropertyAppraiser_1>,
        <mf:PropertyAppraiser_2> ;
    mf:hasTitle "APPRAISAL REPORT" .

<mf:PropertyInspectionDate1> a mf:PropertyInspectionDate ;
    mf:hasDay "N/A" ;
    mf:hasMonth "N/A" ;
    mf:hasYear "N/A" .

<mf:Property_1> a mf:Property ;
    mf:hasAddress <mf:PropertyAddress_1> ;
    mf:hasName "COLLEGE COURTYARD APARTMENTS & RAIDER HOUSING" ;
    mf:hasOwner "NORTHWEST FLORIDA STATE COLLEGE FOUNDATION" ;
    mf:hasUnits "62"^^xsd:int .

<mf:PropertyAddress1> a mf:PropertyAddress ;
    mf:hasCity "Niceville" ;
    mf:hasState "FL" ;
    mf:hasStreetName "Garden Lane" ;
    mf:hasStreetNumber "28",
        "28"^^xsd:string,
        "30",
        "30"^^xsd:string ;
    mf:hasZip "32578" .

<mf:PropertyAddress_1> a mf:PropertyAddress ;
    mf:hasCity "NICEVILLE" ;
    mf:hasState "FL" ;
    mf:hasStreetName "GARDEN LANE" ;
    mf:hasStreetNumber "28",
        "30" ;
    mf:hasZip "32578" .

<mf:PropertyAppraisal1> a mf:PropertyAppraisal ;
    mf:hasAppraisedValue "Current Market Value",
        "N/A" ;
    mf:hasAppraiser "EquiValue Appraisal LLC",
        "Jason P. Shirey, MAI, CCIM",
        "Josette D. Jackson, CCIM" ;
    mf:hasDate <mf:PropertyAppraisalDate1> ;
    mf:hasRemarks "File No. EQ 190416",
        "Of Existing Multi-Family Property" ;
    mf:hasTitle "APPRAISAL REPORT",
        "Appraisal of College Courtyard Apartments & Raider Housing" .

<mf:PropertyAppraisalDate1> a mf:PropertyAppraisalDate ;
    mf:hasDay 13,
        "13"^^xsd:int ;
    mf:hasMonth "December" ;
    mf:hasYear 2019,
        "2019"^^xsd:int .

<mf:PropertyAppraiser_1> a mf:PropertyAppraiser ;
    rdfs:label "Jason P. Shirey, MAI, CCIM, CPM" ;
    mf:hasAppraisalLicense "RZ3186" .

<mf:PropertyAppraiser_2> a mf:PropertyAppraiser ;
    rdfs:label "Josette D. Jackson, CCIM" ;
    mf:hasAppraisalLicense "RZ3275" .""")
            else:
                st.error('Document or ontology is missing', icon="🚨")

if __name__ == '__main__':
    st.set_page_config(layout="wide")
    authenticate()
