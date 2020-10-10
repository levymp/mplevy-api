import pandas as pd
import requests
import os
from pathlib import Path


# define urls
# BASE_URL = 'https://api.mplevy.com/api/mbot/v1/'

BASE_URL = 'http://127.0.0.1:8505/api/mbot/v1/log'
LOG_URL = BASE_URL + 'log'
DIRECTORY_URL = BASE_URL + 'directory'

# # open file

def main():

    file = open(os.path.realpath('../../../MBOT-RPI/data/convex_10mx10m_5cm.log'), 'rb')
    file_payload = {'logfile': file}
    params_payload = {'name': 'CLASS FILE', 'description': 'convex_10mx10m_5cm' }

    # post file
    r = requests.post(LOG_URL, files=payload, params=params_payload)

    if r.status_code != 200:
        print(r.text)
        return -1

    # get file

    r = requests.get(LOG_URL, params={'runId': r['runId']})

    # check response
    if r.status_code != 200:
        print(r.text)
        return -1

    file_path = Path('/tmp/mbot_int.pkl')
    file_path.unlink(missing_ok=True)
    # read in content
    with open(file_path, 'wb') as fd:
        fd.write(r.content)
    # read in df
    df = pd.read_pickle(file_path)
    print(df.keys())

    # get table
    r = requests.get(DIRECTORY_URL, params={'database': 'prod'})

    # check response
    if r.status_code != 200:
        print(r.text)
        return -1

    file_path = Path('/tmp/mbot_table.pkl')
    file_path.unlink(missing_ok=True)
    # read in content
    with open(file_path, 'wb') as fd:
        fd.write(r.content)
    # read in df
    df = pd.read_pickle(file_path)
    print(df.keys())

    # delete file
    r = requests.delete(LOG_URL, params={'runId': r['runId']})


if __name__ == "__main__":
    main()

