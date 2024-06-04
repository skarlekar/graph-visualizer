from knowledge_base_lambda.rdf_extractor import extract
from knowledge_base_lambda.rdf_to_cypher_neptune import main as upload_to_neptune
import json


def lambda_handler(event, context):
    # TODO implement
    document_key = event['document']
    ontology_key = event['ontology'] + '.ttl'
    
    graph = extract(doc_link=document_key, ontology_link=ontology_key)
    upload_to_neptune(rdf_data=graph.serialize(format='ttl'))
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda kg-1!')
    }