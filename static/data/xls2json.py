import pandas
import json
import tqdm

with open('./mv_data.xlsx', 'rb') as f:
    result = pandas.read_excel(f)

j = json.loads(result.to_json())
keys = []
papers = []
for key in j:
    keys.append(key)

for i in tqdm.tqdm(range(len(j.get('doi')))):
    obj = {}
    for key in keys:
        obj[key] = j.get(key).get(str(i))
    papers.append(obj)

with open('./mv_data.json', 'w') as f:
    f.write(json.dumps({'papers': papers}))
