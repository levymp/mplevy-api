import os
import uuid
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from pytz import timezone

# Global Directories
_ROOT = Path('/home/michaellevy/data/')

# Setup Prod and Backup Directories
_PROD = _ROOT.joinpath('prod/mbot/')
_BACKUP = _ROOT.joinpath('backup/mbot/')

# Setup Pickle Data Table
_PICKLE = _PROD.joinpath('mbot_table.pkl')


def get_time():
    # current time in EST
    date = datetime.now(tz=timezone('US/Eastern'))

    # get directory and file_name formats
    yyyy_mm_dd = date.strftime('%Y_%m_%d')
    hh_mm_ss = date.strftime('%H:%M:%S')
    full_time = date.strftime('%Y-%m-%d-%H:%M:%S')

    return [yyyy_mm_dd, hh_mm_ss, full_time, date]

def get_file_info(time, prod):
    # return file name
    
    if not isinstance(prod, bool):
        return -1 

    if prod is True:
        _LOG = _PROD.joinpath('log')
        _PKL = _PROD.joinpath('pickle')
    else:
        _LOG = _BACKUP.joinpath('log')
        _PKL = _BACKUP.joinpath('pickle')

    time = get_time()
    
    # yyyy-mm-dd-H:M:S
    base_file_name = time[0] + '_' + time[1]

    # setup result
    payload = {'log': {}, 'pkl_initial': {}, 'pkl_final': {}}

    # write time data
    payload['DATE'] = time[2]
    payload['DATETIME'] = time[3]

    # New log directory
    NEW_LOG = _LOG.joinpath(time[0])
    NEW_LOG.mkdir(exist_ok=True)
    
    # New pickle directory
    NEW_PKL = _PKL.joinpath(time[0])
    NEW_PKL.mkdir(exist_ok=True)

    # setup log name and path
    payload['log']['name'] = base_file_name + '.log'
    payload['log']['path'] = NEW_LOG.joinpath(payload['log']['name'])
    
    # setup initial pickle name and path
    # this is created in the log directory and then moved to the pickle directory
    payload['pkl_initial']['name'] = base_file_name + '_log' + '.pkl'
    payload['pkl_initial']['path'] = NEW_LOG.joinpath(payload['pkl_initial']['name'])
    
    # setup final pkl name and path
    payload['pkl_final']['name'] = base_file_name + '.pkl'
    payload['pkl_final']['path'] = NEW_PKL.joinpath(payload['pkl_final']['name'])

    return payload

def update_mbot_table(botname, description,file_info, prod):
    '''Append File Structure Lookup Pandas DataFrame'''
    if not isinstance(botname, str): 
        return -1
    elif not isinstance(file_info, dict):
        return -1
    elif not isinstance(prod, bool):
        return -1
    
    # COLUMNS TO APPEND
    columns = ['BOT NAME', 'PICKLE NAME', 'PICKLE PATH', 'LOG NAME', 'LOG PATH', 'DESCRIPTION', 'DATE', 'DATETIME']
    
    # setup new row list to write to data frame
    new_row = []
    
    # trim botname
    botname.replace(' ', '')
    
    # add botname
    new_row.append(botname)
    
    # check pickle and write to row
    if file_info['pkl_final']['path'].is_file():
        new_row.append(file_info['pkl_final']['name'])
        new_row.append(str(file_info['pkl_final']['path'].absolute()))
    else:
        new_row.extend(['-', '-'])
        
    # check log and write to row
    if file_info['log']['path'].is_file():
        new_row.append(file_info['log']['name'])
        new_row.append(str(file_info['log']['path'].absolute()))
    else:
        new_row.extend(['-', '-'])

    # add description
    new_row.append(description)

    new_row.append(file_info['DATE'])
    new_row.append(file_info['DATETIME'])

    # check prod database
    if prod is True: 
        pickle_path = _PROD.joinpath('mbot_table.pkl')
    else:
        pickle_path = _BACKUP.joinpath('mbot_table.pkl')


    # write to true table
    if pickle_path.is_file():
        # read pickle and update
        df = pd.read_pickle(pickle_path)
        # keep track of runId
        runId = len(df)
        df.loc[runId] = new_row
        # write pickle
        df.to_pickle(pickle_path)
        file_info['runId'] = runId
        file_info['result'] = dict(zip(columns, new_row))
        return 0
    else:
        print('TABLE NOT UPDATED!')
        return -2

def get_file_address(runId, column):
    if _PICKLE.is_file():
        df = pd.read_pickle(_PICKLE)
    else: 
        return -1
    # check for valid runId
    if runId < len(df) and runId >= 0:
        return Path(df.loc[runId][column])
    else:
        return -1

def delete_run(runId):
    if isinstance(runId, str):
        runId = int(runId)
    
    # read in df
    if _PICKLE.is_file():
        df = pd.read_pickle(_PICKLE)
    else: 
        return -1
    
    # check if valid runId
    if runId < len(df) and runId >= 0:
        
        # delete log file
        log = Path(df.loc[runId]['LOG PATH'])
        log.unlink(missing_ok=True)

        # if pickle write failed... check if it is in log directory
        pkl = df.loc[runId]['PICKLE PATH']
        if pkl == '-':
            pkl = Path(df.loc[3]['LOG PATH'].replace('.', '_') + '.pkl')
        else:
            pkl = Path(pkl)

        # delete
        pkl.unlink(missing_ok=True)

        # delete row
        df = df.drop([runId])
        # overwrite pickle
        df = df.reset_index(drop=True)
        df.to_pickle(_PICKLE)
        return 0
    else:
        return -1
