import boto3
import rdflib
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
import networkx as nx
import json
import os, sys, backoff, math
from random import randint
from gremlin_python import statics
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.driver.protocol import GremlinServerError
from gremlin_python.driver import serializer
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.process.traversal import T
from gremlin_python.structure.graph import Graph
from aiohttp.client_exceptions import ClientConnectorError
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import ReadOnlyCredentials
from types import SimpleNamespace

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


reconnectable_err_msgs = [
    'ReadOnlyViolationException',
    'Server disconnected',
    'Connection refused',
    'Connection was already closed',
    'Connection was closed by server',
    'Failed to connect to server: HTTP Error code 403 - Forbidden'
]

retriable_err_msgs = ['ConcurrentModificationException'] + reconnectable_err_msgs

network_errors = [OSError, ClientConnectorError]

retriable_errors = [GremlinServerError, RuntimeError, Exception] + network_errors

def prepare_iamdb_request(database_url):

    service = 'neptune-db'
    method = 'GET'

    access_key = os.environ['AWS_ACCESS_KEY_ID']
    secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
    region = os.environ['SERVICE_REGION']

    session_token = os.environ['AWS_SESSION_TOKEN']

    creds = SimpleNamespace(
        access_key=access_key, secret_key=secret_key, token=session_token, region=region,
    )

    request = AWSRequest(method=method, url=database_url, data=None)
    SigV4Auth(creds, service, region).add_auth(request)

    return (database_url, request.headers)

def create_remote_connection():
    (database_url, headers) = connection_info()

    return DriverRemoteConnection(
        database_url,
        'g',
        pool_size=1,
        message_serializer=serializer.GraphSONSerializersV2d0(),
        headers=headers)

def connection_info():

    database_url = 'wss://{}:{}/gremlin'.format(os.environ['neptuneEndpoint'], os.environ['neptunePort'])

    if 'USE_IAM' in os.environ and os.environ['USE_IAM']=="true":
        return prepare_iamdb_request(database_url)
    else:
        return (database_url,{})

def convert_rdf_json():
    s3 = boto3.resource("s3")
    bucket = "kg-merged-rdf"
    key = "merged-graph.ttl"

    obj = s3.Object(bucket,key)
    rdf_data=obj.get()["Body"].read().decode("utf-8")
    print(rdf_data)

    g = rdflib.Graph()
    result = g.parse(data=rdf_data,format="turtle")

    nodes = []
    found_nodes=dict()
    for s,p,o in result:
        for n in ([s,o] if "#type" not in p else [s]):
            if n not in found_nodes:
                found_nodes[n]=len(nodes)
                nodes.append({})
                nodes[-1]["id"]=str(n.replace("mf:",""))
                nodes[-1]["attributes"]=""
                nodes[-1]["type"]=""
        if "#type" in p:
            nodes[found_nodes[s]]["type"]=str(o)

    links = []
    for s,p,o in result:
        if "#type" in p:
            continue
        s = s.replace("mf:","")
        o= o.replace("mf:","")
        p = p.replace("mf:","")
        if "#" in p:
            p=p.split("#")[1]
        if "/" in p:
            p=p.split("/")[-1]
        links.append({
            "source":s,
            "target":o,
            "label":p,
            "strength":1.0,
        })

    out = {"links":links,"nodes":nodes}

def main():
    graph = Graph()
    conn = create_remote_connection()
    g = graph.traversal().withRemote(conn)

    data = convert_rdf_json()
    
    # clear graphs
    g.V().drop().iterate()
    g.E().drop().iterate()
    
    print("Loading Nodes...")
    nodes = data["nodes"]
    for n in nodes:
        matching_node_by_id = g.V().has("entity_id",n["id"]).count().next()
        if matching_node_by_id==0:
            if n["type"]:
                g.addV("entity").property("type",n["type"]).property("entity_id",n["id"]).next()
            else:
                g.addV("entity").property("entity_id",n["id"]).next()
            print(f"Added {n}")
        print(f"Final node number: {g.V().count().next}")

    print("Loading Links...")
    edges= data["links"]
    for e in edges:
        source,target,label = e["source"],e["target"],e["label"]
        g.V().has("entity_id",source).addE(label).to(__.V().has("entity_id",target)).next()
        print(f"Finished adding {e}")    
    print(f"Final edge number: {g.E().count().next}")

    conn.close()

if __name__=="__main__":
    main()