import requests
import pandas as pd
from pathlib import Path

# _URL = 'https://api.mplevy.com/api/mbot/v1/log'
_URL = 'http://127.0.0.1:8505/api/mbot/v1/log'

# be sure to give dir/name.pkl if you plan to save (and set save=True)
def get_df(runId, name='/tmp/mbot_temp.pkl', save=False):
    '''GET A pandas df from MBOT Database and either don't save it or save it (rename directory in that case)'''
    if isinstance(runId, str):
        runId = int(runId)
    elif not isinstance(runId, int):
        return -1
    
    # pass runId into payload
    payload = {'runId': runId, 'type': 'pkl'}

    # get the data back unwrapped.
    r = requests.get(_URL, params=payload)
    if r.status_code != 200:
        print(r.text())
        return -1
    
    # open file
    file_path = Path(name)

    # delete if it's already there
    file_path.unlink(missing_ok=True)
    
    # read in content
    with open(file_path, 'wb') as fd:
        fd.write(r.content)
    
    # read in df
    df = pd.read_pickle(file_path)

    # delete file
    if save == False:
        file_path.unlink(missing_ok=False)
    return df

# must give dir/name
def get_log(runId, name):
    '''Give a runId from database and save the log file'''
    if isinstance(runId, str):
        runId = int(runId)
    elif not isinstance(runId, int):
        return -1
    
    # pass runId into payload
    payload = {'runId': runId, 'type': 'log'}

    # get the data back unwrapped.
    r = requests.get(_URL, params=payload)
    if r.status_code != 200:
        print(r.text())
        return -1
    
    # open file
    file_path = Path(name)

    # delete if it's already there
    file_path.unlink(missing_ok=True)
    
    # read in content/save
    with open(file_path, 'wb') as fd:
        fd.write(r.content)

def delete_run(runId):
    '''Delete a run'''
    if isinstance(runId, str):
        runId = int(runId)
    elif not isinstance(runId, int):
        return -1
    payload = {'runId': runId}
    r = requests.delete(url, params=payload)
    if r.response_code != 200: 
        print(r.text())
        return -1
    else:
        return 0

def post_log(path):
    '''pass in path string'''
    # read file
    file_path = Path(path)
    
    # check if correct path
    if not file_path.is_file():
        return -1
    
    # open file
    file = open(file_path, 'rb')

    # create payload
    payload = {'logfile': file}
    # post file
    r = requests.post(_URL, files=payload)
    
    # close file
    file.close()
    if r.status_code != 200: 
        print(r.text())
        return -1
    else: 
        return r.json()

if __name__ == "__main__":
    import os
    response = post_log(os.path.realpath('../../MBOT-RPI/data/convex_10mx10m_5cm.log'))
    print(str(response))
    