import os
from api_calls import api_requests
import tarfile 
import time
import logging

logging.basicConfig(filename='output.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s',level=logging.INFO)


dir_path = './logs/'
url_ids = []

def check_permission_request():
	for file in os.listdir(dir_path):
		print('Processiing '+file)
		try:
			log_tar_dir = dir_path+file+'/chrome_log.tar'
			t = tarfile.open(log_tar_dir,'r')
			log_name = 'chrome_debug.log'
			res=-1
			if log_name in t.getnames():
				f = t.extractfile(log_name)
				data = f.read()
				res = data.find('MalNotifications :: Permission Requested')	
			if res >-1:
				id = file.replace('container_','')
				status = api_requests.update_url_api(id,'has_permission_request','true')
				print(status)
				api_requests.update_url_api(id,'is_visited','true')
				print('Permission Request found :: '+id)
		except Exception as e:
			print(e)
			continue

        
def get_app_server_key():
	for file in os.listdir(dir_path):
		print('Processiing '+file)
		try:
			log_tar_dir = dir_path+file+'/chrome_log.tar'
			t = tarfile.open(log_tar_dir,'r')
			log_name = 'chrome_debug.log'
			res=-1
			print(t.getnames())
			id = file.replace('container_','')
			if log_name in t.getnames():
				f = t.extractfile(log_name)
				data = f.readlines()
				sub = 'MalNotifications :: Endpoint'
				indexes = map(str,range(len(data)))
				res = filter(lambda (i,x): sub in x,zip(indexes,data))
				print('Result')
				print(res)
				if res:
					i = int(res[0][0])
					lines = data[i-12:i+2]
					endpoint = data[i].split('::')[2].strip().strip('\n')
					print(endpoint)
					status = api_requests.update_url_api(id,'endpoint',endpoint)
					print(status)
					for line in lines:
						if 'Application Server Key' in line:
							app_key = line.split('::')[2].strip().strip('\n')
							print(app_key)
							status = api_requests.update_url_api(id,'app_server_key',app_key)
							print(status)
						if 'Auth Secret' in line:
							auth_key = line.split('::')[2].strip().strip('\n')
							print(auth_key)
							status = api_requests.update_url_api(id,'auth_secret',auth_key)
							print(status)
		except Exception as e:
			print(e)
			continue
		time.sleep(5)


def record_error(id,dir_path):
	log_tar_dir = dir_path+'container_'+id+'/logs.tar'	
	try:
		t = tarfile.open(log_tar_dir,'r')
		log_name = 'logs/'+id+'_sw.log'
		res=-99
		err=-1
		data=''
		if log_name in t.getnames():
			f = t.extractfile(log_name)
			data = f.read()
			res = data.find('Page Load Complete')
			err = data.find('Chromium Crashed')
		if res>0 and err<0:
			return False
		logging.info('===============================================')
		logging.info('Processiing '+'container_'+id)
		if res<=0:
			logging.info(data)
		chrome_tar_dir = dir_path+'container_'+id+'/chrome_log.tar'
		t = tarfile.open(chrome_tar_dir,'r')
		chrome_log_name = 'chrome_debug.log'
		if chrome_log_name in t.getnames():
			f = t.extractfile(chrome_log_name)
			data = f.read()
			err = data.find(':FATAL:')
		if err>-1 and data:
			logging.info(data[err-100:err+200])
		logging.info('||')
		logging.info('||')
		return True
	except Exception as e:
		logging.info(e)
		logging.info('||')
		logging.info('||')
		return False



def parse_errors():
	dir_path = './logs/'
	for file in os.listdir(dir_path):		
		id = file.replace('container_','')  
		record_error(id, dir_path)
		

parse_errors()
