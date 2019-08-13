 
import pandas as pd 
import concurrent.futures
import docker
import time
import datetime
import os

from docker_config import *
from docker_monitor import *
from api_calls import api_requests

import logging

logging.basicConfig(filename='output_new.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s',level=logging.INFO)

client = docker.from_env()

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
					futures[executor.submit(initiate_container, url, str(id), script_file, visit_count, container_timeout)] = (str(id),visit_count)		
				else:
					futures[executor.submit(resume_container,url, str(id), script_file, visit_count, container_timeout)] = (str(id), visit_count)	
			
			#time.sleep(container_timeout)
			#res_futures = concurrent.futures.wait(futures, timeout=container_timeout, return_when= concurrent.futures.ALL_COMPLETED)
			try:
				for future in  concurrent.futures.as_completed(futures, timeout=container_timeout):
					id, v_count = futures.pop(future)				
					try:
						#res = future.result()
						logging.info(get_time() + 'Container_'+ str(id) +': Completed successfully!!'	)	
					except concurrent.futures.TimeoutError as ex:
						logging.info(get_time() +  'Container_' + str(id) +': Timeout occured!!')
					except Exception as exc:
						logging.info(get_time() +  'Container_' + str(id) +': Exception ')
						logging.info(exc)			
					stop_container(id)		
					res = export_container(id, v_count)	
					if res:
						processed_url_ids.add(id)	
			except Exception as e:
				for future in futures.keys():
					id, v_count = futures.pop(future)				
					try:
						#res = future.result()
						logging.info(get_time() + 'Container_'+ str(id) +': Timeout Occured!!'	)	
					except concurrent.futures.TimeoutError as ex:
						logging.info(get_time() +  'Container_' + str(id) +': Timeout occured!!')
					except Exception as exc:
						logging.info(get_time() +  'Container_' + str(id) +': Exception ')
						logging.info(exc)			
					stop_container(id)		
					res = export_container(id, v_count)	
					if res:
						processed_url_ids.add(id)	

			'''
			for future in res_futures[1]:
				id =  futures.pop(future)						
				logging.info(get_time() +  'Container_' + str(id) +': Timeout occured!!')	
				stop_container(id)		
				res = export_container(id, visit_count)	
				if res:
					processed_url_ids.add(id)	
			'''				
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
		crawl_urls={}
		for item in results:
			id = item[0]
			url = item[1]
			crawl_urls[str(id)]={'url': url,'count':0}
			api_requests.update_url_api(id,'visit_status','4')
		return crawl_urls
	return {}

def process_urls_with_notifications():	

	URL_COUNT = 500
	notification_urls  =  fetch_urls_with_notifications(URL_COUNT)

	'''
	notification_urls={'953':{'url':'https://goalhighlight.site/','count':0},
	'475':{'url':'https://kingofgym.com/','count':0},
	'833':{'url':'https://thekingwarehouse.com/','count':0},
	'955':{'url':'https://vuivuitv.site/','count':0},
	'599':{'url':'https://vuilen.info/','count':0},
	'179':{'url':'https://kingelia.com/','count':0},
	'701':{'url':'https://hotvideo.top/','count':0},
	'978':{'url':'https://tipsbook.site/','count':0},
	'1039':{'url':'https://xemhub.net/','count':0},
	'1008':{'url':'https://evangelistjoshuaforum.com/','count':0}
	}
	'''
	
	while True:			
		processed_ids = process_urls_parallel(notification_urls, notification_collection_script, ANALYSIS_TIMEOUT, ANALYSIS_MAX_CONTAINERS)
		for id in processed_ids:
			api_requests.update_url_api(id,'is_analyzed_desktop','true')
			api_requests.update_url_api(id,'visit_status','5')
		logging.info(processed_ids)
		notification_urls = {id:info for id,info in notification_urls.items() if info['count']>0 or id in processed_ids}
		for key in notification_urls.keys():
			itm = notification_urls[key]
			if itm['count']==10:
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
	logging.info('Started Processing')
	process_urls_with_notifications()



if __name__ == "__main__":
    main()
