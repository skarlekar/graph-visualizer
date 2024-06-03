import pandas as pd
import boto3
from jinja2 import Environment, FileSystemLoader
from langchain_community.chat_models import BedrockChat
from langchain_community.graphs import NeptuneGraph
import json
import os
from io import StringIO


host = os.getenv("NEPTUNE_HOST")
port = 8182
use_https = True
region = 'us-east-1'

graph = NeptuneGraph(host=host, port=port, use_https=use_https, region_name=region)

def connect_to_bedrock():
  boto_session = boto3.Session()
  aws_region = boto_session.region_name
  bedrock_runtime = boto_session.client("bedrock-runtime", region_name="us-east-1")

  modelId = "anthropic.claude-3-sonnet-20240229-v1:0"

  llm = BedrockChat(model_id=modelId, client=bedrock_runtime, model_kwargs={"temperature": 0})
  return llm

def get_cypher_query(rdf_data):
  template_dir = "../prompts/"
  environment=Environment(loader=FileSystemLoader(template_dir))
  template=environment.get_template("cypher-merge-rdf-template.txt")
  cypher_gen_prompt=template.render(rdf_data=rdf_data,neptune_schema=graph.get_schema)

  llm = connect_to_bedrock()
  response = llm.invoke(input=cypher_gen_prompt)
  return response

def execute_cypher_query(cypher_query):
  graph.query(cypher_query)

def main():
  rdf_data="""
  @prefix mf: <http://example.org/multifamily#> .
  @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

  <mf:100RentalUnits> a mf:TotalRentalUnits .

  <mf:101TotalUnits> a mf:TotalUnits .

  <mf:1NonRevenueUnit> a mf:NonRevenueUnits .

  <mf:ConventionalLoan> a mf:LoanType .

  <mf:MidCityBank> a mf:Lender .

  <mf:NSPDevelopmentPartners> a mf:OwnerEntity .

  <mf:NSPManagementPartners> a mf:ManagementAgent .

  <mf:OwnerAddress> a mf:OwnerAddress ;
      mf:hasCity "Mid City" ;
      mf:hasState "Ohio" ;
      mf:hasStreetAddress "600 Main Street" ;
      mf:hasZipCode "23445" .

  <mf:SampleGardens> a mf:Property ;
      mf:annualEnergyConsumptionReductionCommitment "25%" ;
      mf:annualWaterConsumptionReductionCommitment "30%" ;
      mf:hasApprovalDate "01/04/2018" ;
      mf:hasApprovalDecision "yes" ;
      mf:hasApprovalNotes "Based on the strength and experience of the sponsor including managing other seniors assets in the same market and state for many years as well as the financial improvement of the as
set, this supplemental transaction is recommended for Loan Committee Approval." ;
      mf:hasAssetManagementNotes "The property is maintained well and the rentals have met projected expectations." ;
      mf:hasAssetManagementNotesDate "01/05/2021" ;
      mf:hasGreenBuildingCertification "yes" ;
      mf:hasGreenBuildingCertificationAgency "BREEAM USA" ;
      mf:hasGreenBuildingUpgrades "Energy Start Appliances",
          "Energy efficient LED lighting" ;
      mf:hasInspectionDate "03/07/2020" ;
      mf:hasLender mf:MidCityBank ;
      mf:hasLenderContact mf:WallyLendor ;
      mf:hasLoanType mf:ConventionalLoan ;
      mf:hasManagementAddress mf:OwnerAddress ;
      mf:hasManagementAgent mf:NSPManagementPartners ;
      mf:hasManagementContact mf:SusanDeveloper ;
      mf:hasNonRevenueUnits mf:1NonRevenueUnit ;
      mf:hasOwnerAddress mf:OwnerAddress ;
      mf:hasOwnerContact mf:SusanDeveloper ;
      mf:hasOwnerEntity mf:NSPDevelopmentPartners ;
      mf:hasPCR "3" ;
      mf:hasPropertyAddress mf:SampleGardensAddress ;
      mf:hasPropertyInspectionAgency "urgent inspection llc" ;
      mf:hasPropertyInspector "Jane Jones" ;
      mf:hasPropertyName "Sample Gardens" ;
      mf:hasTotalRentalUnits mf:100RentalUnits ;
      mf:hasTotalUnits mf:101TotalUnits ;
      mf:hasUnits "101"^^xsd:int .

  <mf:SampleGardensAddress> a mf:PropertyAddress ;
      mf:hasCity "Mid City" ;
      mf:hasLowIncomeUnits "20" ;
      mf:hasMSA "" ;
      mf:hasState "Ohio" ;
      mf:hasStreetAddress "123 Sample Street" ;
      mf:hasVeryLowIncomeUnits "10" ;
      mf:hasZipCode "23445" ;
      mf:isSmallMultifamilyUnitMeetingLowIncome "yes" .

  <mf:SusanDeveloper> a mf:OwnerContact ;
      mf:hasEmail "susan@NSPDP.com" ;
      mf:hasName "Susan Developer" ;
      mf:hasPhone "(215) 555-1212" .

  <mf:WallyLendor> a mf:LenderContact ;
      mf:hasEmail "wlendor@MCB.com" ;
      mf:hasName "Wally Lendor" ;
      mf:hasPhone "(215) 555-1214" .
  """
  cypher_query = get_cypher_query(rdf_data)
  print(cypher_query.content)
  #execute_cypher_query(cypher_query)

if __name__ == '__main__':
  main()
