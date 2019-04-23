 
import pandas as pd 
import concurrent.futures
import docker
import time
import datetime
import os

from docker_config import *
from docker_monitor import *
from api_calls import api_requests


client = docker.from_env()

def process_urls_parallel(analysis_urls, script_file, container_timeout, max_containers, visit_count):
	futures={}
	count=0
	processed_url_ids = set()
	urls = analysis_urls.copy()
	with concurrent.futures.ProcessPoolExecutor(max_workers = max_containers) as executor:
		while len(urls)>0:
			## Submit jobs to container ##
			for i in range(min(len(urls),max_containers)):
				id = urls.keys()[0]
				url = urls.pop(id)
				if visit_count==0:
					futures[executor.submit(initiate_container, url, str(id), script_file, visit_count, container_timeout)] = str(id)		
				else:
					futures[executor.submit(resume_container,url, str(id), script_file, visit_count, container_timeout)] = str(id)	
			
			time.sleep(container_timeout)
			res_futures = concurrent.futures.wait(futures, timeout=container_timeout, return_when= concurrent.futures.ALL_COMPLETED)
			
			for future in res_futures[0]:
				id = futures.pop(future)				
				try:
					res = future.result(timeout=container_timeout)
					print (get_time() + 'Container_'+ str(id) +': Completed successfully!!'	)
						
				except Exception as exc:
					print(get_time() +  'Container_' + str(id) +': Exception ')
					print(exc)			
				stop_container(id)		
				res = export_container(id, visit_count)	
				if res:
					processed_url_ids.add(id)	
			for future in res_futures[1]:
				id =  futures.pop(future)						
				print(get_time() +  'Container_' + str(id) +': Timeout occured!!')	
				stop_container(id)		
				res = export_container(id, visit_count)	
				if res:
					processed_url_ids.add(id)					
	return processed_url_ids

def stop_running_containers():
	while client.containers.list():		
		for c in client.containers.list():
			print (c)			
			c.stop()
			c.remove()

def fetch_urls_with_notifications():
	results = api_requests.fetch_urls_api(200,'true','true')
	crawl_urls={}
	for item in results:
		id = item[0]
		url = item[1]
		crawl_urls[id]=url
		api_requests.update_url_api(id,'visit_status','4')
		
	return crawl_urls

def process_urls_with_notifications():	
	count=0
	notification_urls  =  fetch_urls_with_notifications()
	'''
	notification_urls={953:'https://goalhighlight.site/',
	475:'https://kingofgym.com/',
	833:'https://thekingwarehouse.com/',
	955:'https://vuivuitv.site/',
	599:'https://vuilen.info/',
	179:'https://kingelia.com/',
	701:'https://hotvideo.top/',
	978:'https://tipsbook.site/',
	1039:'https://xemhub.net/',
	1008:'https://evangelistjoshuaforum.com/'
	}
	'''
	while count<10:				
		processed_ids = process_urls_parallel(notification_urls, notification_collection_script, ANALYSIS_TIMEOUT, ANALYSIS_MAX_CONTAINERS, count)
		print(processed_ids)
		for id in processed_ids:
			api_requests.update_url_api(id,'is_analyzed_desktop','true')
		count +=1
		time.sleep(1800)
		
	

def main():	
	while True:
		stop_running_containers()
		'''
		prune unused removed containers
		'''
		docker_prune()
		process_urls_with_notifications()



if __name__ == "__main__":
    main()
