import json


def loadType(views):
    result = []
    for viewIndex in views:
        view = views[viewIndex]
        for v in view['viewType']:
            if v['Type'] == 'small multiple':
                continue
        # v['probability'] = float(v['probability'])
        result.append([float(view['cX']), float(view['cY']),
                       float(view['cWidth']), float(view['cHeight'])])
        if view.get('mid_view'):
            children = loadType(view['mid_view'])
            for child in children:
                # child['probability'] = child['probability']
                result.append(child)
    # resObj = {}
    # for ty in result:
    #     if not resObj.get(ty['Type']):
    #         resObj[ty['Type']] = 0
    #     resObj[ty['Type']] += ty['probability']
    # res = []
    # for Type in resObj:
    #     res.append({'Type': Type, 'probability': resObj[Type]})
    return result


with open('mv_data.json', encoding='utf8') as f:
    j = json.loads(f.read())['papers']


# types = []
for paper in j:
    with open(f"mv_data/{paper['json']}", encoding='utf8') as f:
        p = json.loads(f.read())
        paper['temp'] = loadType(p['result']['views'])
        # for v in paper['temp']:
        #     if v['Type'] not in types:
        #         types.append(v['Type'])

for paper in j:
    paper['viewMatrix'] = [[0 for _ in range(40)] for _ in range(40)]
    for i, v in enumerate(paper['temp']):
        # paper['positionVector'][i] = v
        for k, v2 in enumerate(paper['temp']):
            if k == i:
                continue
            paper['viewMatrix'][i][k] = -1 if abs(
                v[0] - v2[0]) <= (v[2]+v2[2])/2 and abs(v[1] - v2[1]) <= (v[3]+v2[3])/2 else 0
        paper['viewMatrix'][i][i] = -sum(paper['viewMatrix'][i])
    # for t in types:
    #     sameProp = list(filter(lambda x: x['Type'] == t, paper['temp']))
    #     if len(sameProp):
    #         paper['positionVector'].append(sameProp[0]['probability'])
    #     else:
    #         paper['positionVector'].append(0)
    del paper['temp']

with open('mv_data.json', 'w', encoding='utf8') as f:
    f.write(json.dumps({'papers': j}))
