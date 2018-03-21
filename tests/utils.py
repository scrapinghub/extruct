import json

def jsonize_dict(d):
    return json.loads(json.dumps(d))
