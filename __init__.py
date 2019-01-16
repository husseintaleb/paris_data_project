print("coucou")

import requests
import json

res = requests.get("https://opendata.paris.fr/api/records/1.0/search/?dataset=velib-disponibilite-en-temps-reel&rows=3")

obj = json.loads(res.text)

class Dataset