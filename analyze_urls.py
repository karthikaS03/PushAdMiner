 
import pandas as pd 
import concurrent.futures
import docker
import time
import datetime
from docker_monitor import *
import os
from docker_config import *

client = docker.from_env()

def get_time():
	currentDT = datetime.datetime.now()
	return '['+currentDT.strftime("%Y-%m-%d %H:%M:%S") +'] '

def process_urls_parallel(analysis_urls, script_file, container_timeout, max_containers, visit_count):
	futures={}
	count=0
	processed_url_ids = []
	urls = analysis_urls.copy()
	with concurrent.futures.ThreadPoolExecutor(max_workers = max_containers) as executor:
		while len(urls)>0:
			## Submit jobs to container ##
			for i in range(min(len(urls),max_containers)):
				id = urls.keys()[0]
				url = urls.pop(id)
				if visit_count==0:
					futures[executor.submit(initiate_container, url, str(id), script_file, container_timeout)] = str(id)		
				else:
					futures[executor.submit(resume_container,url, str(id), script_file, container_timeout)] = str(id)	
				
			res_futures = concurrent.futures.wait(futures, timeout=container_timeout, return_when= concurrent.futures.ALL_COMPLETED)
			
			for future in res_futures[0]:
				id = futures.pop(future)				
				try:
					log = future.result(timeout=container_timeout)
					print (get_time() + 'Container_'+ str(id) +': Completed successfully!!'	)
					processed_url_ids.append(id)		
				except Exception as exc:
					print(get_time() +  'Container_' + str(id) +': Exception ')
					print(exc)					
				export_container(id, visit_count)
				stop_container(id)
			for future in res_futures[1]:
				id =  futures.pop(future)						
				print(get_time() +  'Container_' + str(id) +': Timeout occured!!')	
				export_container(id, visit_count)	
				stop_container(id)								
			
	return processed_url_ids


'''
df = pd.read_csv('top-1m-filtered.csv',skiprows=range(1,1000),nrows=10)
print df.columns
'''


def stop_running_containers():
	while client.containers.list():		
		for c in client.containers.list():
			print (c)			
			c.stop()
			c.remove()

def fetch_urls_with_notifications():
	urls = [
		'https://serialifilmi.com/',            
		'https://mydramaoppa.com/',  
		'https://www.tubebg.com/',
		'https://shippuden.tv/',
		'https://igg-games.com/',
		'https://www.okanime.com/',
		'https://www.2giga.link/',
		'https://blacktv.tk/',
		'https://kinogo2019.com/',
		'https://www.nopeporno.com/',
		'https://aserialov.net/']
	start_id = 9500
	urls = ['https://shippuden.tv/', 'https://beneguy.com', 'https://blacktv.tk' ]
	notification_urls = {start_id+i:url for i,url in enumerate(urls) }
	return notification_urls


def process_urls_with_notifications():	
	count=0
	while count<5:
		notification_urls  =  fetch_urls_with_notifications()
		processed_urls = process_urls_parallel(notification_urls, notification_collection_script, ANALYSIS_TIMEOUT, ANALYSIS_MAX_CONTAINERS, count)
		print(processed_urls)
		count +=1
		time.sleep(1200)
	

def main():	
	stop_running_containers()
	'''
	prune unused removed containers
	'''
	#docker_prune()
	process_urls_with_notifications()



if __name__ == "__main__":
    main()
