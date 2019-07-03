import os
import tarfile
import shutil
import time
import hashlib

from api_calls import api_requests
from parse_logs import extract_chain
from database import db_operations

dir_path = './results/'
url_ids = []

def parse_results_notification():
        dir_path = './results/'
        processed_dir_path = './processed_results/'
        for i in range(11):
                for file in os.listdir(dir_path):		
                        id = file.replace('container_','')  
                        if os.path.exists(dir_path+file+'/'+str(i)):
                                print('Processing folder '+dir_path+file+'/'+str(i))
                                sw_log_tar_dir = dir_path+file+'/'+str(i)+'/logs.tar'	
                                chrome_tar_dir = dir_path+file+'/'+str(i)+'/chrome_log.tar'
                                log_file=None
                                chrome_file=None  
                                try:
                                        t = tarfile.open(sw_log_tar_dir,'r')
                                        log_name = 'logs/'+id+'_sw.log'   
                                        if log_name in t.getnames():
                                                log_file = t.extractfile(log_name)
                                        t2 = tarfile.open(chrome_tar_dir,'r')
                                        chrome_log_name = 'chrome_debug.log' 
                                        if chrome_log_name in t2.getnames():
                                                chrome_file = t2.extractfile(chrome_log_name)  
                                except Exception as e:
                                        print(e)        
                                extract_chain.parse_log(id, chrome_file,log_file)
                                shutil.move(dir_path+file+'/'+str(i), processed_dir_path+file+'/'+str(i))
def process_detailed_logs():
        dir_path = './processed_results/'
        processed_dir_path = './processed_results_logs/'
        for i in range(11):
                for file in os.listdir(dir_path):		
                        id = file.replace('container_','')  
                        if os.path.exists(dir_path+file+'/'+str(i)):
                                print('Processing folder '+dir_path+file+'/'+str(i))
                                sw_log_tar_dir = dir_path+file+'/'+str(i)+'/logs.tar'	
                                chrome_tar_dir = dir_path+file+'/'+str(i)+'/chrome_log.tar'
                                log_file=None
                                chrome_file=None  
                                try:
                                        t = tarfile.open(sw_log_tar_dir,'r')
                                        log_name = 'logs/'+id+'_sw.log'   
                                        if log_name in t.getnames():
                                                log_file = t.extractfile(log_name)
                                        t2 = tarfile.open(chrome_tar_dir,'r')
                                        chrome_log_name = 'chrome_debug.log' 
                                        if chrome_log_name in t2.getnames():
                                                chrome_file = t2.extractfile(chrome_log_name)  
                                except Exception as e:
                                        print(e)        
                                formatted_logs = extract_chain.parse_log(id, chrome_file,log_file)
                                dbo = db_operations.DBOperator()
                                
                                for log in formatted_logs:
                                        dbo.insert_logs(i, log)
                                shutil.move(dir_path+file+'/'+str(i), processed_dir_path+file+'/'+str(i))

def process_resources():
        dir_path = './processed_results_logs/'
        for i in range(11):
                for file in os.listdir(dir_path):		
                        id = file.replace('container_','')  
                        if os.path.exists(dir_path+file+'/'+str(i)):
                                print('\n*** Processing folder '+dir_path+file+'/'+str(i)+' ***')
                                resources_tar_dir = dir_path+file+'/'+str(i)+'/resources.tar'	
                                try:
                                        with tarfile.open(resources_tar_dir, 'r') as tar:
                                                for tarinfo in tar:
                                                        if tarinfo.isreg():
                                                                flo = tar.extractfile(tarinfo) 
                                                                hash = hashlib.sha1()
                                                                while True:
                                                                        data = flo.read(2**20)
                                                                        if not data:
                                                                                break
                                                                        hash.update(data)
                                                                flo.close()
                                                                print( hash.hexdigest(), tarinfo.name)
                                                                file_name = tarinfo.name.split('/')[2]
                                                                dbo = db_operations.DBOperator()
                                                                dbo.insert_resource_info(id,i,file_name,hash.hexdigest())
                                                                
                                except Exception as e:
                                        print(e)        
                               
                                #shutil.move(dir_path+file+'/'+str(i), processed_dir_path+file+'/'+str(i))
                

def parse_results_urls():
        dir_path = './event_logs/'
        processed_dir_path = './processed_event_logs2/'
        for file in os.listdir(dir_path):		
                id = file.replace('.log','')  
                with open(dir_path+file,'r') as event_file:
                        line = event_file.readline()
                        dbo = db_operations.DBOperator()
                        while line:
                                if 'URL ::' in line:
                                        url = (line.split('::')[1]).strip(' ')
                                        #print(url)
                                        dbo.insert_url(id, url,'','other')
                                line = event_file.readline()
                shutil.move(dir_path+file, processed_dir_path+file)

def re_run():
        dir_path = './results/'
        for i in range(2):
                for file in os.listdir(dir_path):		
                        id = file.replace('container_','')  
                        if os.path.exists(dir_path+file+'/'+str(i)):
                                print(id,i)
                                api_requests.update_url_api(id,'visit_status','1')
                                api_requests.update_url_api(id,'is_analyzed_desktop','true')


if __name__ =='__main__':
        while True:
                process_resources()
                '''
                parse_results_notification()
                parse_results_urls()
                process_detailed_logs()
                time.sleep(3600)
                '''
        #re_run()
        '''
        with open('parse_logs/9601.log','r') as f:
                extract_chain.parse_log(0,f,'')
        '''

