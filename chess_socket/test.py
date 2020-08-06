import json
m ='{"id": 2, "name": "abc"}'
jsonObj = json.loads(m)
jsono = json.dumps(jsonObj)
print(jsonObj['id'])
print(jsono)