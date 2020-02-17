import os
from api_calls import api_requests
import tarfile 
import time
import logging

logging.basicConfig(filename='output.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s',level=logging.INFO)


dir_path = './visit_logs/'
url_ids = []

''' Helper Method  '''
def get_activity_timestamp(data, sub_text)
    indexes = map(str,range(len(data)))
    res = int(filter(lambda (i,x): sub_text in x, zip(indexes,data))[0][0])
    timestamp = ''
    for i in range(res,0,-1):
        line = data[i]        
        if 'LOG::Forensics' in line and line.count(':')>1:
            time = line.split(':')[2] 
            timestamp = datetime(2019, int(time[:2]), int(time[2:4]), int(time[5:7]),int(time[7:9]), int(time[9:11]), int(time[12:]))
            break
    return timestamp

def get_request_duration(dir_path,id):        
    chrome_tar_dir = dir_path+'container_'+id+'/chrome_log.tar'
    t = tarfile.open(chrome_tar_dir,'r')
    chrome_log_name = 'chrome_debug.log'
    error=''
    perm_request_time = None
    sw_req_time = None
    log_start_time = None
    perm_req_duration = 0
    sw_req_duration= 0
    if chrome_log_name in t.getnames():
        f = t.extractfile(chrome_log_name)
        data = f.readlines()
        sub_text = 'INFO:Forensics.cpp'
        log_start_time = get_activity_timestamp(data, sub_text)
        sub_text = '-*#$interface=ServiceWorkerContainer'
        sw_req_time = get_activity_timestamp(data, sub_text)
        sub_text = 'MalNotifications :: Permission Requested'
        perm_request_time = get_activity_timestamp(data, sub_text)
    if log_start_time:
        if perm_request_time:
            perm_req_duration = (perm_request_time - log_start_time).total_seconds()
        if sw_req_time:
            sw_req_duration = (sw_req_time - log_start_time).total_seconds()
    return (sw_req_duration, perm_req_duration)

        

def record_error(dir_path,id):        
		chrome_tar_dir = dir_path+'container_'+id+'/chrome_log.tar'
		t = tarfile.open(chrome_tar_dir,'r')
		chrome_log_name = 'chrome_debug.log'
        error=''
		if chrome_log_name in t.getnames():
			f = t.extractfile(chrome_log_name)
			data = f.read()
			err = data.find(':FATAL:')
		if err>-1 and data:
			error = data[err-100:err+200]
		return error

def find_status(data):        
		res = data.find('Page Load Complete')
		err = data.find('Chromium Crashed')
		if res>0 and err<0:
			return 1
		if err>-1:
			return 2
        return 0

def parse_log(dir_path, id):
    log_tar_dir = dir_path+'container_'+id+'/logs.tar'	
    info= {'status':-99,'sw_reg_at':0,'permission_req_at':0,'error':'', 'crash_log':''}
	try:
		t = tarfile.open(log_tar_dir,'r')
		log_name = 'logs/'+id+'_sw.log'
		data=''
        res=-99
        status =-99
		if log_name in t.getnames():
			f = t.extractfile(log_name)
			data = f.read()
            status = find_status(data)
        info['status']=status
        if status==2:
            info['crash_log']=record_error(dir_path,id)
            info['error'] = data
        elif status ==0:
            info['error'] = data
        sw_req, perm_req = get_request_duration(dir_path,id)
        info['sw_reg_at'] = sw_req
        info['permission_req_at'] = perm_req
        print(info)
    except Exception as e:
        print(e)



def parse_visit_logs():
	dir_path = './logs/'
	for file in os.listdir(dir_path):		
		id = file.replace('container_','')  
		parse_log( dir_path, id)
		

parse_visit_logs()
