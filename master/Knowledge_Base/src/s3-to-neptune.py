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

def convert_rdf_dict():
    s3 = boto3.resource("s3")
    bucket = "kg-merged-rdf"
    key = "latest-kg.ttl"

    obj = s3.Object(bucket,key)
    rdf_data=obj.get()["Body"].read().decode("utf-8")
    print(rdf_data)

    g = rdflib.Graph()
    result = g.parse(data=rdf_data,format="turtle")

    neptune_data = {}
    links = []
    for s,p,o in result:
        s,p,o=str(s),str(p),str(o)
        s = s.split(":", 1)[1] # removes prefixes, i.e. 'mf:', 'n1:'
        if s not in neptune_data:
            neptune_data[s]={}
        if "#" in o and p.split("#")[1] !="type":
            links.append([s,p.split("#")[1],o.split("#")[1]])
        if ":" in o and "http" not in o:
            links.append([s,p.split("#")[1],o.split(":")[1]])
        else:
            neptune_data[s][p.split("#")[1]]=o if "#" not in o else o.split("#")[1]
    return neptune_data,links

def main():
    graph = Graph()
    conn = create_remote_connection()
    g = graph.traversal().withRemote(conn)

    # clear graphs
    g.V().drop().iterate()
    g.E().drop().iterate()

    node_data,link_data = convert_rdf_dict()
    print("Loading Nodes...")
    for n_id in node_data.keys():
      n=node_data[n_id]
      temp_n=g.addV(n["type"]).property("entity_id",n_id).next()
      for k,v in n.items():
        if k == "type":
          continue
        g.V().has("entity_id",n_id).property(k,v).next()
    print(f"Final node number: {g.V().count().next()}")

    print("Loading Links...")
    for e in link_data:
        source,target,label = e[0],e[2],e[1]
        g.V().has("entity_id",source).addE(label).to(__.V().has("entity_id",target)).next()
        print(f"Finished adding {e}")
    print(f"Final edge number: {g.E().count().next()}")

    conn.close()

if __name__=="__main__":
    main()
