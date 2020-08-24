from sklearn.manifold import TSNE
import numpy as np
import json

with open('mv_data.json') as f:
    j = json.loads(f.read())


def distance(a, b):
    return np.linalg.norm(a.reshape((40, 40))-b.reshape((40, 40)))


data = np.array(list(map(lambda x: np.array(x).flatten(),
                         map(lambda x: x['viewMatrix'], j['papers']))))
embed = TSNE(metric=distance).fit_transform(data)
embed -= embed.min(axis=0)
embed /= embed.max(axis=0)
embed *= 2
embed -= 1

with open('tsne.json', 'w') as f:
    f.write(json.dumps(embed.tolist()))
