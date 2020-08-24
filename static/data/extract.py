import json


with open('mv_data.json', encoding='utf8') as f:
    j = json.loads(f.read())['papers']

with open('extract.json', 'w') as f:
    f.write(json.dumps(list(map(lambda paper: paper['positionVector'], j))))
