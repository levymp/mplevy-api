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


runId = 0
params = {'runId': runId, 'type': 'pkl'}

delparam = {'runId': 0}

# r = requests.post(url, files=payload)
r = requests.get(url, params=params)
# r = requests.delete(url, params=delparam)

# path to temporary file and delete previous ones


file_path = Path('/tmp/mbot_int')
file_path.unlink(missing_ok=True)
# read in content
with open(file_path, 'wb') as fd:
    fd.write(r.content)
# read in df
df = pd.read_pickle(file_path)

# delete file
file_path.unlink(missing_ok=False)
print(df.keys())
print(r.json())
file.close()
