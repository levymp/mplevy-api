import requests
import os

file = open(os.path.realpath('../../../MBOT-RPI/data/convex_10mx10m_5cm.log'), 'rb')

payload = {'logfile': file}

# url = 'https://api.mplevy.com/api/mbot/v1/log'

url = 'http://127.0.0.1:8505/api/mbot/v1/log'

r = requests.post(url, files=payload)

print(r.status_code)
print(r.json())

file.close()
