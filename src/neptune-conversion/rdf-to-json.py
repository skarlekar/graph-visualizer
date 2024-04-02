import rdflib
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
import networkx as nx
import json
import os

output_dir = "output-graph/"
file_name = "page_1_graph"

g = rdflib.Graph()
result = g.parse(os.path.join("data/",file_name.split(".json")[0]+".ttl"))

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
            nodes[-1]["group"]=1
    print(s,p,o)
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
        "rationale":""
    })

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

for i,v in enumerate(top_level_parents):
    if i ==0:
        nodes.append({})
        nodes[-1]["id"]="Knowledge"
        nodes[-1]["attributes"]=""
        nodes[-1]["type"]=""
        nodes[-1]["group"]=1
    links.append({
        "source":v,
        "target":"Knowledge",
        "label":"ManuallyAdded",
        "strength":1.0,
        "rationale":""
    })

out = {"links":links,"nodes":nodes,"groups":[{"group_id":1,"rationale":"default group"}]}

with open(os.path.join(output_dir,file_name.split(".json")[0]+"-graph.json"),"w+") as f:
    json.dump(out,f)