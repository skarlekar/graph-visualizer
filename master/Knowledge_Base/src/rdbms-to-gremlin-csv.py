import pandas as pd
import boto3
from jinja2 import Environment, FileSystemLoader
from langchain_community.chat_models import BedrockChat
import json
import os
from io import StringIO

def connect_to_bedrock():
    boto_session = boto3.Session()
    aws_region = boto_session.region_name
    bedrock_runtime = boto_session.client("bedrock-runtime", region_name="us-east-1")

    modelId = "anthropic.claude-3-sonnet-20240229-v1:0"

    llm = BedrockChat(model_id=modelId, client=bedrock_runtime, model_kwargs={"temperature": 0})
    return llm

def main():
    template_dir = "../prompts/"
    ddl="""
    CREATE TABLE "Property" (
        "property_id" INT, PRIMARY KEY("property_id"),
        "property_name" CHAR(30),
        "property_address" CHAR(50),
        "number_of_units" INT,
        "property_build_date" DATE,
        "inspection_date" DATE,
        "inspection_score" CHAR(30),
        "inspector_name" CHAR(50),
        "underwriting_date" DATE,
        "underwriting_result" CHAR(30),
        "underwriter_comments" CHAR(50),
        "inspector_comments" CHAR(100),
    )

    CREATE TABLE "Loan" (
        "loan_id" INT, PRIMARY KEY("loan_id"),
        "loan_lifecycle_state" CHAR(50),
         "loan_origination_date" DATE,
         "IsGreenLoanEligible" CHAR(10),
         "isAffordableHousingEligible" CHAR(10),
         "loan_maturity_date" DATE,
         "original_loan_amount" INT,
         "loan_upb" INT,
         "loan_proodct_id" INT,
        "property_id" INT,
        FOREIGN KEY("property_id") REFERENCES "Property"("property_id")
    )
    """
    environment=Environment(loader=FileSystemLoader(template_dir))
    template=environment.get_template("create-gremlin-vertices-headers-template.txt")
    vertices_prompt=template.render(ddl=ddl)
    template=environment.get_template("create-gremlin-edges-headers-template.txt")
    edges_prompt=template.render(ddl=ddl)

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

    # Creating Gremlin vertices csv files
    response = llm.invoke(input=vertices_prompt)
    with open("test-resp.json","w+") as f:
        json.dump(json.loads(response.content),f)
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
        v["~id"]=k+v["~id"].astype(str)

    for k,v in filtered_tables.items():
        for c in v.columns:
            if ":Date" in c:
                v[c]=pd.to_datetime(v[c])
                v[c]=v[c].dt.strftime("%Y-%m-%d")

    # Creating Gremlin edges csv files
    response = llm.invoke(input=edges_prompt)
    edges_mapping = json.loads(response.content)
    with open("test-edges-resp.json","w+") as f:
        json.dump(json.loads(response.content),f)
    edges_mapping=json.loads(open("test-edges-resp.json","r").read())
    edges_tables = []
    for f in [x["from"]["table_name"] for x in edges_mapping]:
        edges_tables.append(name_table[f])

    for i in range(len(edges_mapping)):
        e=edges_mapping[i]
        temp_table = edges_tables[i]
        rename_columns = {e["from"]["primary_key"]:"~from",e["from"]["foreign_key"]:"~to"}
        temp_table=temp_table.rename(columns=rename_columns)
        temp_table=temp_table[["~from","~to"]]
        temp_table["~from"]=e["from"]["table_name"]+temp_table["~from"].astype(str)
        temp_table["~to"]=e["to"]["table_name"]+temp_table["~to"].astype(str)
        temp_table["~id"]=temp_table["~from"].astype(str)+"-"+temp_table["~to"].astype(str)
        temp_table["~label"]=e["~label"]
        edges_tables[i]=temp_table

    # write to s3
    s3_bucket_name = os.environ["RDBMS_BUCKET_NAME"]
    s3_resource = boto3.resource("s3")
    for k,v in filtered_tables.items():
        print(k)
        print(v)
        csv_buffer=StringIO()
        v.to_csv(csv_buffer,index=False)
        s3_resource.Object(s3_bucket_name,f"{k}_vertices.csv").put(Body=csv_buffer.getvalue())

    for i in range(len(edges_mapping)):
        e=edges_mapping[i]
        output_name = e["from"]["table_name"]+"_"+e["to"]["table_name"]+"_edges.csv"
        print(output_name)
        print(edges_tables[i])
        csv_buffer=StringIO()
        edges_tables[i].to_csv(csv_buffer,index=False)
        s3_resource.Object(s3_bucket_name,output_name).put(Body=csv_buffer.getvalue())

if __name__ == '__main__':
    main()
