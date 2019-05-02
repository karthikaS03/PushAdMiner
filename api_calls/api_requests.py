import requests
import csv
import os
import time
import sys
# sys.setdefaultencoding() does not exist, here!
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

dir_path = '../seed_lists/'
insert_api_url = 'https://oyi4twvq77.execute-api.us-east-2.amazonaws.com/default/notification-db-add?'
fetch_api_url = 'https://2zbo3zz9q9.execute-api.us-east-2.amazonaws.com/default/notification-db-insert?'
update_api_url = 'https://4h39mccr97.execute-api.us-east-2.amazonaws.com/default/notification-db-update?'
insert_api_info = 'https://2kq3sya8jl.execute-api.us-east-2.amazonaws.com/default/notification_visit_info_add?'


def add_visit_info(info):
    api_url = "{}id={}&status={}&per_req={}&sw_reg={}&error={}&crash_log={}"
    api_url = api_url.format(insert_api_info,info['id'],info['status'],info['permission_req_at'],info['sw_reg_at'],info['error'],info['crash_log'])
    resp = requests.get(url=api_url)
    return resp.json()


def insert_record(url,keyword):
    query_string='seed_url='+url+'&seed_keyword='+keyword
    api_url = insert_api_url+query_string
    resp = requests.get(url=api_url)
    
    print(resp.text+ ' :: '+url)

def insert_seed_urls():
    for file in os.listdir(dir_path):        
        with open(dir_path+file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\n')            
            seed_keyword = file.split('_')[1].replace('.csv','')
            for row in csv_reader:
                seed_url = row[0].split(';')[0]
                insert_record(seed_url,seed_keyword)
            time.sleep(120)

'''
   To fetch URLS for processing
   params
	count: No of URLS to fetch at a time
	is_visited: always true for analysis, false when the URLS have to be filtered based on if they request permission
	is_desktop: false to fetch next URLS for Mobile analysis, true to get the next URLS for desktop browser analysis 
  Returns
	seed_url_id and seed_url
'''
def fetch_urls_api(count,is_visited,is_desktop):
    api_url = "{}count={}&is_visited={}&is_desktop={}"
    api_url = api_url.format(fetch_api_url,str(count),is_visited,is_desktop)
    
    resp = requests.get(url=api_url)
    return resp.json()

'''
   To fetch URL processing status
   params
	seed_url_id: id of the seed url that needs to be updated
	col_name: set of column names are (is_visited, has_permission_request, is_analyzed_desktop, is_analyzed_mobile)
	col_value: the above mentioned columns are all boolean values
	After an URL is analyzed, based on mobile or desktop set the appropriate column to true 
   Returns
    message string for success or failure
'''
def update_url_api(seed_url_id,col_name,col_val):
    api_url = "{}id={}&name={}&val={}"
    api_url = api_url.format(update_api_url,str(seed_url_id),col_name,col_val)    
    resp = requests.get(url=api_url)
    return resp.text

def main():	
	insert_seed_urls()
    #print(update_url_api(1,'is_visited','true'))

if __name__ == "__main__":
    main()
