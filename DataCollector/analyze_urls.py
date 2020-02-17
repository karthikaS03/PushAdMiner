 
import pandas as pd 
import concurrent.futures
import docker
import time
import datetime
import os

from docker_config import *
from docker_monitor import *
from database import db_operations
from api_calls import api_requests

import logging

logging.basicConfig(filename='output_new.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s',level=logging.INFO)

client = docker.from_env()
dbo = db_operations.DBOperator()

def process_urls_parallel(analysis_urls, script_file, container_timeout, max_containers):
	futures={}
	processed_url_ids = set()
	urls = analysis_urls.copy()
	with concurrent.futures.ProcessPoolExecutor(max_workers = max_containers) as executor:
		while len(urls)>0:
			## Submit jobs to container ##
			for i in range(min(len(urls),max_containers)):
				id = urls.keys()[0]
				itm = urls.pop(id)
				url = itm['url']
				visit_count = itm['count']
				if i!=0 and i%5==0:
					time.sleep(200)
				if visit_count==0:
					## initiates docker container for the first time
					futures[executor.submit(initiate_container, url, str(id), script_file, visit_count, container_timeout)] = (str(id),visit_count)		
				else:
					## Resumes docker container and waits for notifications
					futures[executor.submit(resume_container,url, str(id), script_file, visit_count, container_timeout)] = (str(id), visit_count)	
			
			try:
				##  Keep docker container active for specific duration and stop the containe and export data 
				for future in  concurrent.futures.as_completed(futures, timeout=container_timeout):
					id, v_count = futures.pop(future)				
					try:
						logging.info(get_time() + 'Container_'+ str(id) +': Completed successfully!!'	)	
					except concurrent.futures.TimeoutError as ex:
						logging.info(get_time() +  'Container_' + str(id) +': Timeout occured!!')
					except Exception as exc:
						logging.info(get_time() +  'Container_' + str(id) +': Exception ')
						logging.info(exc)			
							
					res = export_container(id, v_count)	
					stop_container(id)
					if res:
						processed_url_ids.add(id)	
			except Exception as e:
				##  Stop the containers that didn't complete before timeout and export data
				for future in futures.keys():
					id, v_count = futures.pop(future)				
					try:				
						logging.info(get_time() + 'Container_'+ str(id) +': Timeout Occured!!'	)	
					except concurrent.futures.TimeoutError as ex:
						logging.info(get_time() +  'Container_' + str(id) +': Timeout occured!!')
					except Exception as exc:
						logging.info(get_time() +  'Container_' + str(id) +': Exception ')
						logging.info(exc)			
							
					res = export_container(id, v_count)	
					stop_container(id)
					if res:
						processed_url_ids.add(id)				
	return processed_url_ids

def stop_running_containers():
	for c in client.containers.list():
		print (c)			
		c.stop()
		c.remove()

def fetch_urls_with_notifications(count):
	if count>0:
		logging.info('Fetching URLS ::'+str(count))
		results = api_requests.fetch_urls_api(count,'true','true')
		#results = dbo.get_seed_urls()
		crawl_urls={}
		for item in results:
			id = item[0]
			url = item[1]
			crawl_urls[str(id)]={'url': url,'count':0}
			api_requests.update_url_api(id,'visit_status','11')
		return crawl_urls
	return {}

def process_urls_with_notifications():	

	URL_COUNT = 300
	notification_urls  =  fetch_urls_with_notifications(URL_COUNT)
	
	while True:			
		processed_ids = process_urls_parallel(notification_urls, notification_collection_script, ANALYSIS_TIMEOUT, ANALYSIS_MAX_CONTAINERS)
		
		for id in processed_ids:
			api_requests.update_url_api(id,'is_analyzed_desktop','true')
			api_requests.update_url_api(id,'visit_status','111')
		
		logging.info(processed_ids)
		## Retain only those containers that requested notifications
		notification_urls = {id:info for id,info in notification_urls.items() if info['count']>0 or id in processed_ids}
		for key in notification_urls.keys():
			itm = notification_urls[key]							
			if itm['count']==15:
				## Resume each containe maximum of 15 times
				notification_urls.pop(key)
			else:
				itm['count'] = itm['count']+1
		
		notification_urls.update(fetch_urls_with_notifications(URL_COUNT-len(notification_urls)))
		logging.info(notification_urls)
		time.sleep(1800)
		
	

def main():
	stop_running_containers()
	'''
	prune unused removed containers
	'''
	docker_prune()
	logging.info('PushAdMiner :: Collecting WPNs...' )
	process_urls_with_notifications()



if __name__ == "__main__":
    main()
