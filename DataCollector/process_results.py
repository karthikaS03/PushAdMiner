import os
import tarfile
import shutil
import time
import hashlib
import re
from api_calls import api_requests
from parse_logs import extract_chain
from database import db_operations
from docker_monitor import *
import pandas as pd
import numpy
                                

def process_detailed_logs():
        dir_path = './containers_data/'
        processed_dir_path = './processed_data/'

        for i in range(16):
                for file in os.listdir(dir_path):		
                        id = file.replace('container_','')  
                        if os.path.exists(dir_path+file+'/'+str(i)):
                                print('Processing folder '+dir_path+file+'/'+str(i))
                                sw_log_tar_dir = dir_path+file+'/'+str(i)+'/logs.tar'	
                                chrome_tar_dir = dir_path+file+'/'+str(i)+'/chrome_log.tar'
                                resources_tar_dir = dir_path+file+'/'+str(i)+'/resources.tar'
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

                                        ## Process the files requested by SW
                                        process_resource_file(resources_tar_dir,i,id)

                                        ## Process the logs and filter required events 
                                        try:                                                
                                                formatted_logs = extract_chain.parse_log(id, i, chrome_file,log_file)
                                        except Exception as e:
                                                print('Extract chain')
                                                print(e)    
                                                          
                                        dbo = db_operations.DBOperator()
                                        ## Insert the processed events to DBB
                                        for log in formatted_logs:
                                                dbo.insert_logs(i, log)
                                        
                                        ## Find all URLs that was involved for this viit
                                        parse_results_urls(id,i)
                                        
                                        ## Move the processed data to a different folder
                                        try:
                                                shutil.move(dir_path+file+'/'+str(i), processed_dir_path+file+'/'+str(i))
                                        except Exception as e:
                                                print('Move file :'+e)
                                       
                                except Exception as e:
                                        print('Procees detailed logs')
                                        print(e)        
                                

def process_resource_file(resources_tar_dir,i,id):
        try:
                ## Calculate hash of each resource file and get a list of URLs contacted by any script file
                with tarfile.open(resources_tar_dir, 'r') as tar:
                        for tarinfo in tar:
                                if tarinfo.isreg():
                                        flo = tar.extractfile(tarinfo) 
                                        hash = hashlib.sha1()
                                        file_name = tarinfo.name.split('/')[2]
                                        #print(file_name)
                                        while True:
                                                data = flo.read(2**20)
                                                if not data:
                                                        break
                                                hash.update(data)
                                        flo.close()
                                        flo = tar.extractfile(tarinfo) 
                                        urls = flo.read()
                                        links = re.findall('"((http)s?://.*?)"', urls)
                                        links2 = re.findall("'((http)s?://.*?)'", urls)
                                        links = [l[0] for l in links]+[l[0] for l in links2]
                                        contacted_urls = ' :: '.join(links)
                                        flo.close()
                                                                                
                                        dbo = db_operations.DBOperator()
                                        dbo.insert_resource_info(id,i,file_name,hash.hexdigest(), contacted_urls)
        except Exception as e:
                print('process resources')
                print(e)


def parse_results_urls(id,count):
        dir_path = './event_logs/'
        file = id+'_'+str(count)+'.log'
        with open(dir_path+file,'r') as event_file:
                line = event_file.readline()
                dbo = db_operations.DBOperator()
                while line:
                        if 'URL ::' in line:
                                url = (line.split('::')[1]).strip(' ')                                
                                dbo.insert_url(id, url,'','other')
                        line = event_file.readline()


if __name__ =='__main__':
        while True:               
                process_detailed_logs()               
                time.sleep(3600)
               

