from flask import Flask
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
import os, sys, backoff, math
from flask import render_template
import json 

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
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


@app.route("/")
def hello_world():
    graph = Graph()
    conn = create_remote_connection()
    g = graph.traversal().withRemote(conn)
    node_data = g.V().elementMap().toList()
    print("Sending request to neptune for nodes...")
    edge_data = g.E().elementMap().toList()
    print("Sending request to neptune for edges...")
    conn.close()
    id_node_name = {n["id"]:n["entity_id"] for n in node_data}
    nodes=[]
    edges=[]
    for n in node_data:
        nodes.append({
            "id":n["entity_id"],
            "attributes":"",
            "type":""
        })

    for e in edge_data:
        edges.append({
            "source":id_node_name[e["IN"]["id"]],
            "target":id_node_name[e["OUT"]["id"]],
            "label":e["label"],
            "strength":1.0
        })
    
    # union find to get list of not connected components
    parent = {n["id"]:n["id"] for n in nodes}
    rank = {n["id"]:1 for n in nodes} 

    def find(n):
        while n!=parent[n]:
            parent[n]=parent[parent[n]]
            n=parent[n]
        return n

    def union(n1,n2):
        p1,p2 = find(n1),find(n2)
        if rank[p1]>rank[p2]:
            rank[p1]+=1
            parent[p2]=p1
        else:
            rank[p2]+=1
            parent[p1]=p2

    for e in links:
        s,t = e["source"],e["target"]
        union(s,t)

    top_level_parents = set()
    for n,p in parent.items():
        top_level_parents.add(find(n))

    if len(top_level_parents)>1:
        for i,v in enumerate(top_level_parents):
            if i ==0:
                nodes.append({})
                nodes[-1]["id"]="Knowledge"
                nodes[-1]["attributes"]=""
                nodes[-1]["type"]=""
            links.append({
                "source":v,
                "target":"Knowledge",
                "label":"ManuallyAdded",
                "strength":1.0
            })

    out = {"links":links,"nodes":nodes}
    return render_template("index.html", data=out_data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='8080')