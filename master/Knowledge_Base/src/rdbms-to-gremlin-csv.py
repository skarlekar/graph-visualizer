import pandas as pd
import boto3
from langchain_community.chat_models import BedrockChat
import json

def connect_to_bedrock():
    boto_session = boto3.Session()
    aws_region = boto_session.region_name
    bedrock_runtime = boto_session.client("bedrock-runtime", region_name="us-east-1")

    modelId = "anthropic.claude-3-sonnet-20240229-v1:0"

    llm = BedrockChat(model_id=modelId, client=bedrock_runtime, model_kwargs={"temperature": 0})
    return llm

def main():
    table_locations={
            "Loan":"../data/structured_data/Loan-data.csv",
            "Property":"../data/structured_data/Property-data.csv",
            "Underwriting":"../data/structured_data/Underwriting-data.csv",
            "Inspection":"../data/structured_data/Inspection-data.csv"
    }
    name_table = {}
    for k,v in table_locations.items():
        name_table[k]=pd.read_csv(v)
    llm = connect_to_bedrock()
    vertices_prompt = open("../prompts/gremlin-vertices-headers-from-sql","r").read()
    '''
    response = llm.invoke(input=vertices_prompt)
    with open("test-resp.json","w+") as f:
        json.dump(json.loads(response.content),f)
    '''
    vertices_mapping=json.loads(open("test-resp.json","r").read())
    #vertices_mapping = json.loads(response.content)
    expected_columns={}
    for table in vertices_mapping:
        expected_columns[table["table_name"]]=[x["sql_attribute_name"] for x in table["mapped_headers"]]

    filtered_tables = {}
    for k,v in name_table.items():
        filtered_tables[k]=v[expected_columns[k]]

    column_name_mapping = {}
    for table in vertices_mapping:
        column_name_mapping[table["table_name"]]={x["sql_attribute_name"]:x["gremlin_header"] for x in table["mapped_headers"]}

    for k,v in filtered_tables.items():
        filtered_tables[k]=v.rename(columns=column_name_mapping[k])

    for k,v in filtered_tables.items():
        v["~id"]=k+"-"+v["~id"].astype(str)

    print(filtered_tables["Loan"])
    
if __name__ == '__main__':
    main()
