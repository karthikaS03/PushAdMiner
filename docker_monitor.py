import docker
from docker_config import *
import os
import time
import datetime

client = docker.from_env()

def get_time():
	currentDT = datetime.datetime.now()
	return '['+currentDT.strftime("%Y-%m-%d %H:%M:%S") +'] '

def initiate_container(url, id, script_name, iteration_count,  container_timeout):	

	## create and setup container ##
    print(get_time() + 'container_'+id+' creating!!')
    container_id  = client.containers.run(image=docker_image,name='container_'+id,volumes = vols,
										  shm_size='1G', user=docker_user, 
										  publish_all_ports=True,stdout=True, stderr=True, detach=True )
    print(get_time() + 'container_'+id+' created successfully!!')
	
    ## wait for display to be activated ##
    time.sleep(10)
    execute_script(url, id, script_name,  iteration_count, container_timeout)

def execute_script(url, id, script_name,  iteration_count, container_timeout):	
	## Execute javascript file
	print(get_time() +'container_'+id+': Executing javascript')
	container = client.containers.get('container_'+str(id))
	stats = container.stats(decode=True)	
	logs = container.exec_run(cmd=['node',script_name,url,id,iteration_count], user=docker_user,stdout=True, stderr=True, detach=True)
	time.sleep(container_timeout-20)
	print(get_time() +'container_'+id+': Execution complete!!')	

def stop_container(id):
    container = client.containers.get('container_'+str(id))
    if container:
        print(get_time() + 'container_'+id+' stopping!!')
        container.stop()

def remove_containers():
    while client.containers.list():		
        for c in client.containers.list():
            c.stop()
            c.remove()
        
def resume_container(url, id, script_name, iteration_count, container_timeout):
    container = client.containers.get('container_'+str(id))
    if container:
        print(get_time() + 'container_'+id+' resuming!!')
        container.start()
        ## wait for display to be activated ##
        time.sleep(10)
        execute_script(url,id, script_name, iteration_count, container_timeout)

def export_container(id, count):
    container = client.containers.get('container_'+str(id))
    print(get_time() + 'container_'+id+' exporting files!!')
    dir_path = './results/container_'+id+'/'
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
    with open(dir_path+'chrome_log.tar', 'w') as f:
        bits, stat = container.get_archive('/home/pptruser/chromium/chrome_debug.log')
        for chunk in bits:
            f.write(chunk)

def docker_prune():
    ## Remove containers that are unused  ##
    try:
        client.containers.prune()		
    except Exception as e:
        print e	


def test():
    remove_containers()
    initiate_container('https://blacktv.tk/','201', 'capture_notifications.js', 120 )
    stop_container('201')
    export_container('201','0')
    time.sleep(10)
    resume_container('https://blacktv.tk/','201','capture_notifications.js',600)
    
if __name__== "__main__":
    test()
