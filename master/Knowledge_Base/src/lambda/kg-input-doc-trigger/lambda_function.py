import json
from urllib import parse
import boto3
from botocore.config import Config


def lambda_handler(event, context):
    # TESTING UPLOAD TO LAMBDA
    # TODO implement
    s3 = boto3.client('s3', region_name='us-east-1')
    # Get the bucket name, key, and metadata ontology value from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    obj = s3.get_object(Bucket=bucket, Key=key)
    ontology = obj['Metadata']['ontology']
    
    payload = {
        'document': key,
        'ontology': ontology
    }
    
    lambda_config = Config(
        read_timeout=900,
        connect_timeout=900,
        retries={"max_attempts": 0}
    )
    
    client = boto3.client('lambda', region_name='us-east-1', config=lambda_config)
    response = client.invoke(
        FunctionName='kg-1',
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )
    print(json.load(response['Payload']))
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from kg-input-doc-trigger!')
    }