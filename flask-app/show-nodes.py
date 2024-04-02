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

    return prepare_iamdb_request(database_url)


@app.route("/")
def hello_world():
    # graph = Graph()
    # conn = create_remote_connection()
    # g = graph.traversal().withRemote(conn)
    # node_data = g.V().elementMap().toList()
    # print("Sending request to neptune for nodes...")
    # edge_data = g.E().elementMap().toList()
    # print("Sending request to neptune for edges...")
    # conn.close()
    # id_node_name = {n["id"]:n["entity_id"] for n in node_data}
    # nodes=[]
    # edges=[]
    # for n in node_data:
    #     nodes.append({
    #         "id":n["entity_id"],
    #         "attributes":"",
    #         "type":""
    #     })

    # for e in edge_data:
    #     edges.append({
    #         "source":id_node_name[e["IN"]["id"]],
    #         "target":id_node_name[e["OUT"]["id"]],
    #         "label":e["label"],
    #         "strength":1.0
    #     })
    # out_data = {"nodes":nodes,"links":edges}
    out_data={"links": [{"source": "PropertyAddress_1", "target": "FL", "label": "mfhasState", "strength": 1.0, "rationale": ""}, {"source": "PropertyAppraisal_1", "target": "PropertyAppraiser_1", "label": "mfhasAppraiser", "strength": 1.0, "rationale": ""}, {"source": "Property_1", "target": "NORTHWEST FLORIDA STATE COLLEGE FOUNDATION", "label": "mfhasOwner", "strength": 1.0, "rationale": ""}, {"source": "PropertyAddress_1", "target": "GARDEN LANE", "label": "mfhasStreetName", "strength": 1.0, "rationale": ""}, {"source": "PropertyAppraisal_1", "target": "APPRAISAL REPORT", "label": "mfhasTitle", "strength": 1.0, "rationale": ""}, {"source": "PropertyAppraisal_1", "target": "190416", "label": "mfhasAppraisalNumber", "strength": 1.0, "rationale": ""}, {"source": "PropertyAppraisal_1", "target": "PropertyAppraiser_2", "label": "mfhasAppraiser", "strength": 1.0, "rationale": ""}, {"source": "Property_1", "target": "62", "label": "mfhasUnits", "strength": 1.0, "rationale": ""}, {"source": "Property_1", "target": "PropertyAddress_1", "label": "mfhasAddress", "strength": 1.0, "rationale": ""}, {"source": "PropertyAddress_1", "target": "32578", "label": "mfhasZip", "strength": 1.0, "rationale": ""}, {"source": "PropertyAppraiser_2", "target": "Josette D. Jackson, CCIM", "label": "label", "strength": 1.0, "rationale": ""}, {"source": "PropertyAddress_1", "target": "NICEVILLE", "label": "mfhasCity", "strength": 1.0, "rationale": ""}, {"source": "PropertyAppraiser_2", "target": "RZ3275", "label": "mfhasAppraisalLicense", "strength": 1.0, "rationale": ""}, {"source": "Property_1", "target": "PropertyAppraisal_1", "label": "mfhasAppraisal", "strength": 1.0, "rationale": ""}, {"source": "PropertyAddress_1", "target": "30", "label": "mfhasStreetNumber", "strength": 1.0, "rationale": ""}, {"source": "PropertyAddress_1", "target": "28", "label": "mfhasStreetNumber", "strength": 1.0, "rationale": ""}, {"source": "Property_1", "target": "COLLEGE COURTYARD APARTMENTS & RAIDER HOUSING", "label": "mfhasName", "strength": 1.0, "rationale": ""}, {"source": "PropertyAppraiser_1", "target": "RZ3186", "label": "mfhasAppraisalLicense", "strength": 1.0, "rationale": ""}, {"source": "PropertyAppraiser_1", "target": "Jason P. Shirey, MAI, CCIM, CPM", "label": "label", "strength": 1.0, "rationale": ""}, {"source": "PropertyAppraiser_1", "target": "Knowledge", "label": "ManuallyAdded", "strength": 1.0, "rationale": ""}], "nodes": [{"id": "PropertyAddress_1", "attributes": "", "type": "http://example.org/mfPropertyAddress", "group": 1}, {"id": "FL", "attributes": "", "type": "", "group": 1}, {"id": "PropertyAppraisal_1", "attributes": "", "type": "http://example.org/mfPropertyAppraisal", "group": 1}, {"id": "PropertyAppraiser_1", "attributes": "", "type": "http://example.org/mfPropertyAppraiser", "group": 1}, {"id": "Property_1", "attributes": "", "type": "http://example.org/mfProperty", "group": 1}, {"id": "NORTHWEST FLORIDA STATE COLLEGE FOUNDATION", "attributes": "", "type": "", "group": 1}, {"id": "GARDEN LANE", "attributes": "", "type": "", "group": 1}, {"id": "APPRAISAL REPORT", "attributes": "", "type": "", "group": 1}, {"id": "190416", "attributes": "", "type": "", "group": 1}, {"id": "PropertyAppraiser_2", "attributes": "", "type": "http://example.org/mfPropertyAppraiser", "group": 1}, {"id": "62", "attributes": "", "type": "", "group": 1}, {"id": "32578", "attributes": "", "type": "", "group": 1}, {"id": "Josette D. Jackson, CCIM", "attributes": "", "type": "", "group": 1}, {"id": "NICEVILLE", "attributes": "", "type": "", "group": 1}, {"id": "RZ3275", "attributes": "", "type": "", "group": 1}, {"id": "30", "attributes": "", "type": "", "group": 1}, {"id": "28", "attributes": "", "type": "", "group": 1}, {"id": "COLLEGE COURTYARD APARTMENTS & RAIDER HOUSING", "attributes": "", "type": "", "group": 1}, {"id": "RZ3186", "attributes": "", "type": "", "group": 1}, {"id": "Jason P. Shirey, MAI, CCIM, CPM", "attributes": "", "type": "", "group": 1}, {"id": "Knowledge", "attributes": "", "type": "", "group": 1}], "groups": [{"group_id": 1, "rationale": "default group"}]}
    return render_template("index.html", data=out_data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='8080')