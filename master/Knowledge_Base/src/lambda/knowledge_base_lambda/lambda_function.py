from rdf_extractor import extract, clean_up, upload_to_s3
from rdf_to_cypher_neptune import main as upload_to_neptune
import json


def lambda_handler(event, context):
    # TODO implement
    document_key = event['document']
    ontology_key = event['ontology'] + '.ttl'
    
    graph = extract(doc_link=document_key, ontology_link=ontology_key)
    upload_to_neptune(rdf_graph=graph)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda kg-1!')
    }