import pandas as pd
import requests
import os
from pathlib import Path



# open file
file = open(os.path.realpath('../../../MBOT-RPI/data/convex_10mx10m_5cm.log'), 'rb')
payload = {'logfile': file}

# get url
# url = 'https://api.mplevy.com/api/mbot/v1/log'
url = 'http://127.0.0.1:8505/api/mbot/v1/log'

params = {'RunId': '0', 'type': 'pkl'}

# r = requests.post(url, files=payload)
r = requests.get(url, params=params)

df = pd.read_pickle(r.content())

print(df.keys())
print(r.status_code)
print(r.json())
file.close()

# # ['BOT', 'PICKLE NAME', 'LOG NAME', 'LOG PATH', 'PICKLE PATH']
# pickle = Path('/home/michaellevy/data/mbot/mbot_table.pkl')
# df = pd.read_pickle(pickle)
# print(df.loc[0]['PICKLE PATH'])
# file_path = Path(df.loc[0]['PICKLE PATH'])
# print(file_path.parent)
# print(file_path.name)
# df.to_pickle(pickle)
# print(df.head())
# print(pickle.absolute())