import requests
import pandas
import json
import tqdm

proxies = {
    "http": 'http://127.0.0.1:7890',
    "https": 'http://127.0.0.1:7890',
}


def loadImage(href):
    while True:
        try:
            sess = requests.session()
            webPage = sess.get(href, proxies=proxies, timeout=2)
            docId = webPage.url.split('/')[-2]
            figureConfig = sess.get(
                f'https://ieeexplore.ieee.org/rest/document/{docId}/figures', headers={
                    'Host': 'ieeexplore.ieee.org',
                    'Referer': webPage.url
                }, proxies=proxies, timeout=2).text
            try:
                figureConfig = json.loads(figureConfig)
            except Exception as e:
                return ''
            if not figureConfig.get('figures') or len(figureConfig.get('figures')) == 0:
                return ''
            figureName = figureConfig.get(
                'figures')[0].get('graphic').get('large')
            # figure = sess.get(
            #     f"https://ieeexplore.ieee.org{figureConfig.get('mediaPath')}/{figureName}", proxies=proxies, timeout=5)
            # with open(f'../images/{figureName}', 'wb') as f:
            #     f.write(figure.content)
            return figureName
        except Exception as e:
            print('Retry', href)


with open('./vispubdata.xlsx', 'rb') as f:
    result = pandas.read_excel(f)

j = json.loads(result.to_json())
keys = []
papers = []
for key in j:
    keys.append(key)

for i in tqdm.tqdm(range(len(j.get('Conference')))):
    obj = {}
    for key in keys:
        obj[key] = j.get(key).get(str(i))
    obj['image'] = loadImage(obj['Link'])
    papers.append(obj)

with open('./config.json', 'w') as f:
    f.write(json.dumps({'papers': papers}))
