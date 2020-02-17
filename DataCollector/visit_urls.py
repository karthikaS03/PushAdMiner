import sys
# sys.setdefaultencoding() does not exist, here!
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

import pandas as pd 
import concurrent.futures
import docker
import time
import datetime
import os
import shutil
import tarfile

from docker_config import *
from docker_monitor import *
from api_calls import api_requests


client = docker.from_env()

def process_urls_parallel(analysis_urls, script_file, container_timeout, max_containers):
	futures={}	
	processed_url_ids = []
	urls = analysis_urls.copy()
	
	with concurrent.futures.ThreadPoolExecutor(max_workers = max_containers) as executor:
		while len(urls)>0:
			## Submit jobs to container ##
			for i in range(min(len(urls),max_containers)):
				id = urls.keys()[0]
				url = urls.pop(id)				
				futures[executor.submit(initiate_container, url, str(id), script_file,0, container_timeout)] = str(id)		
			res_futures = concurrent.futures.wait(futures, timeout=container_timeout, return_when= concurrent.futures.ALL_COMPLETED)
			
			for future in res_futures[0]:
				id = futures.pop(future)	
				res = -1			
				try:
					res = future.result(timeout=container_timeout)		
				except Exception as exc:
					print(get_time() +  'Container_' + str(id) +': Exception ')
					print(exc)				

				res = export_log(id)	
				if res >0:
					print (get_time() + 'Container_'+ str(id) +': URL Visited successfully!!')
					api_requests.update_url_api(id,'is_visited','true')
					api_requests.update_url_api(id,'visit_status','1')
					processed_url_ids.append(id)
				elif res==-99:
					print (get_time() + 'Container_'+ str(id) +': Chromium Crashed!!')
					api_requests.update_url_api(id,'visit_status','3')
				else:
					print (get_time() + 'Container_'+ str(id) +': URL Visit failed!!')
					api_requests.update_url_api(id,'visit_status','2')
					
			for future in res_futures[1]:
				id =  futures.pop(future)						
				print(get_time() +  'Container_' + str(id) +': Timeout occured!!')	
				stop_container(id)	
				export_log(id)			
				api_requests.update_url_api(id,'is_visited','false')			
			
	return processed_url_ids


def stop_running_containers():
	while client.containers.list():		
		for c in client.containers.list():			
			c.stop()
			c.remove()
	print('Stopped Running Containers')

def fetch_urls_for_crawling():
	results = api_requests.fetch_urls_api(180,'false','false')
	crawl_urls={}
	for item in results:
		id = item[0]
		url = item[1]
		crawl_urls[id]=url
		api_requests.update_url_api(id,'visit_status','-1')		
	return crawl_urls

def crawl_urls_for_permission_requests():
	while True:
		crawl_urls = fetch_urls_for_crawling()
		processed_url_ids = process_urls_parallel(crawl_urls, permission_collection_script, CRAWL_TIMEOUT, CRAWL_MAX_CONTAINERS)
		print(processed_url_ids)
		print('Count of successful parsing: ',len(processed_url_ids))
		time.sleep(600)
		docker_prune()
		
def main():	
	stop_running_containers()
	docker_prune()
	time.sleep(30)
	crawl_urls_for_permission_requests()

if __name__ == "__main__":
    main()
