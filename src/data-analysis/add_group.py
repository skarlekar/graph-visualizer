import json
with open("no_group.json","r") as f: 
    data = json.load(f)
for i in range(len(data["nodes"])):
    data["nodes"][i]["group"]=1
data["groups"]={"group_id":1,"rationale":"misc"}
with open("group.json","w+") as f:
    json.dump(data,f)