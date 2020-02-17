import docker
import os
import time
import datetime
import logging
import tarfile

from docker_config import *
from api_calls import api_requests

client = docker.from_env()


logging.basicConfig(filename='output2.log', filemode='w', format='%(name)s - %(funcName)20s() - %(message)s',level=logging.INFO)
export_path = './containers_data/container_'

def get_time():
	currentDT = datetime.datetime.now()
	return '['+currentDT.strftime("%Y-%m-%d %H:%M:%S") +'] '

def initiate_container(url, id, script_name, iteration_count,  container_timeout):	
    try:
        ## create and setup container ##
        logging.info(get_time() + 'container_'+id+' creating!!')
        container_id  = client.containers.create(image=docker_image,name='container_'+id,volumes = vols,
                                                shm_size='1G', user=docker_user, 
                                                publish_all_ports=True, detach=False)
        container = client.containers.get('container_'+str(id))
        container.start()
        logging.info(get_time() + 'container_'+id+' created successfully!!')    
        
        ## wait for display to be activated ##
        time.sleep(10)
        ## Exeecute the browser automation script
        execute_script(url, id, script_name,  iteration_count, container_timeout-100)
    except Exception as e:
        logging.info(e) 

def execute_script(url, id, script_name,  iteration_count, container_timeout):
    try:	
        ## Execute javascript file
        logging.info(get_time() +'container_'+id+': Executing javascript')
        container = client.containers.get('container_'+str(id))               
        #logs = container.attach(stream=True,stdout=True,stderr=True)
        _,logs = container.exec_run(cmd=['node',script_name,url,id,str(iteration_count),str(container_timeout)], user=docker_user, detach=False, stream=True)
        time.sleep(container_timeout)        
        for log in logs:
            logging.info('Container_'+id+'LOG :: '+log)
    
        logging.info(get_time() +'container_'+id+': Execution complete!!')	
        
    except Exception as e:
        logging.info('Exception ')
        logging.info(e)

def stop_container(id):
    try:
        container = client.containers.get('container_'+str(id))
        if container:
            logging.info(get_time() + 'container_'+id+' stopping!!')
            container.pause()
            time.sleep(2)
            container.stop()
    except Exception as e:
        logging.info(e)

def remove_containers():
    while client.containers.list():		
        try:
            for c in client.containers.list():
                c.stop()
                c.remove()
        except Exception as e:
            print(e)
        
def resume_container(url, id, script_name, iteration_count, container_timeout):
    container = client.containers.get('container_'+str(id))
    if container:
        logging.info(get_time() + 'container_'+id+'_'+str(iteration_count)+' resuming!!')
        container.start()
        ## wait for display to be activated ##
        time.sleep(10)
        ##   Open a blank page on the browser and wait for notifications 
        execute_script('about:blank',id, script_name, iteration_count, container_timeout-100)

def export_container(id, count):
    container = client.containers.get('container_'+str(id))
    logging.info(get_time() + 'container_'+id+'_'+str(count)+' exporting files!!')
    dir_path = export_path+id+'/'
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    dir_path = dir_path+ str(count)+'/'
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(dir_path+'screenshots.tar', 'w') as f:
        bits, stat = container.get_archive('/home/pptruser/screenshots/')
        for chunk in bits:
            f.write(chunk)
    with open(dir_path+'logs.tar', 'w') as f:
        bits, stat = container.get_archive('/home/pptruser/logs/')
        for chunk in bits:
            f.write(chunk)
    with open(dir_path+'resources.tar', 'w') as f:
        bits, stat = container.get_archive('/home/pptruser/resources/')
        for chunk in bits:
            f.write(chunk)
    with open(dir_path+'dowanloads.tar', 'w') as f:
        bits, stat = container.get_archive('/home/pptruser/Downloads/')
        for chunk in bits:
            f.write(chunk)
    with open(dir_path+'chrome_log.tar', 'w') as f:
        bits, stat = container.get_archive('/home/pptruser/chromium/chrome_debug.log')
        for chunk in bits:
            f.write(chunk)
    return check_if_success(id,count)

def export_log(id):
	container = client.containers.get('container_'+str(id))
	print(get_time() + 'container_'+id+' exporting files!!')
	dir_path = './permission_results/container_'+id+'/'
	if not os.path.exists(dir_path):
		os.makedirs(dir_path)
	with open(dir_path+'chrome_log.tar', 'w') as f:
		bits, stat = container.get_archive('/home/pptruser/chromium/chrome_debug.log')
		for chunk in bits:
	    		f.write(chunk)
	with open(dir_path+'logs.tar', 'w') as f:
		bits, stat = container.get_archive('/home/pptruser/logs/')
		for chunk in bits:
	    		f.write(chunk)
	log_tar_dir = 'permission_results/container_'+id+'/logs.tar'
	t = tarfile.open(log_tar_dir,'r')
	log_name = 'logs/'+id+'_sw.log'
	res=-99
	err=-1
	if log_name in t.getnames():
		f = t.extractfile(log_name)
		data = f.read()
		res = data.find('Page Load Complete')
		err = data.find('Chromium Crashed')
	if err>-1:
		return -99
	stop_container(id)
	return res

def export_screenshot(id):
    container = client.containers.get('container_'+str(id))    
    dir_path = './lu_screenshots/'
    screenshots_tar_dir = dir_path+'/screenshot.tar'    
    logging.info(get_time() + 'container_'+id+' exporting files!!')
    with open(screenshots_tar_dir, 'w') as f:
        bits, _ = container.get_archive('/home/pptruser/screenshots/')
        for chunk in bits:
            f.write(chunk)
    
    import tarfile
    t = tarfile.open(screenshots_tar_dir,'r')
    t.extractall(path = dir_path)

def export_resources(id):
    container = client.containers.get('container_'+str(id))    
    dir_path = './category_html_files/'
    screenshots_tar_dir = dir_path+'/resources.tar'    
    logging.info(get_time() + 'container_'+id+' exporting files!!')
    with open(screenshots_tar_dir, 'w') as f:
        bits, _ = container.get_archive('/home/pptruser/resources/')
        for chunk in bits:
            f.write(chunk)
    
    import tarfile
    t = tarfile.open(screenshots_tar_dir,'r')
    t.extractall(path = dir_path)
    

def check_if_success(id,count):
    import tarfile
    logging.info(get_time() + 'container_'+id+' checking status!!')
    log_tar_dir = export_path+id+'/'+str(count)+'/logs.tar'
    t = tarfile.open(log_tar_dir,'r')
    log_name = 'logs/'+id+'_sw.log'
    res=-99
    if log_name in t.getnames():
        f = t.extractfile(log_name)
        data = f.read()
        res = data.find('Service Worker Registered')
    if res>-1:
        return True
    return False
		

def docker_prune():
    ## Remove containers that are unused  ##
    try:
        client.containers.prune()		
    except Exception as e:
        logging.info(e)


def test():
    '''
    remove_containers()
    initiate_container('https://evangelistjoshuaforum.com/','tes_100', 'capture_notifications.js','0', 330 )    
    count=0
    while count<2:
        stop_container('tes_100')
        export_container('tes_100',str(count-1))
        time.sleep(300)
        resume_container('https://evangelistjoshuaforum.com/','tes_100','capture_notifications.js',count,330)
        count=count+1
    '''
    #export_container('833','9')
    logging.info(check_if_success('1786','0'))
   
    
if __name__== "__main__":
    test()
