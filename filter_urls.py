import os
from api_calls import api_requests

dir_path = './logs_backup/'
url_ids = []

for file in os.listdir(dir_path):
    data = open(dir_path+file, 'r').read()
    res = data.find('MalNotifications :: Permission Requested')
    if res >-1:
        id = file.replace('permission_','').replace('.log','')
        api_requests.update_url_api(id,'has_permission_request','true')
        print('Permission Request found :: '+id)
        
