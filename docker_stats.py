
import docker 
import json
import time
import datetime
import itertools
import pprint
import concurrent.futures
import os

from docker_config import *

client = docker.from_env()
active_containers={}
stats_dir ='./stats/'
completed_containers = {}
def get_time():
	currentDT = datetime.datetime.now()
	return '['+currentDT.strftime("%Y-%m-%d %H:%M:%S") +'] '


def collect_container_stats(c):
    count=0
    print (get_time() + c.name +': started recording!!'	)
    if c.name not in active_containers:
        active_containers[c.name]=count
    else:
        count=active_containers[c.name]+1
        active_containers[c.name]=count
    with open(stats_dir+c.name+'_'+str(count)+'.json','w') as  f:
        f.write('[\n')        
        
        try:
            stat_stream = c.stats(decode=True, stream=True)
            for stat in stat_stream:
                stats = {}
                stats['name'] = stat['name']
                stats['memory_stats'] = stat['memory_stats']
                stats['cpu_stats'] = stat['cpu_stats']
                stats['time'] = get_time()
                if stat['cpu_stats']['cpu_usage']['total_usage']==0:
                    break
                json.dump(stats,f, indent = True)
                f.write(',\n')		
            completed_containers[c.name]=1
        except Exception as e:
            print('error')
        f.write(']')
    print (get_time() + c.name +': finished recording!!'	)
    return ''

def collect_stats(max_containers):
    with open('container_stats.json','w') as  f:
        f.write('[\n')
        futures={}
	with concurrent.futures.ThreadPoolExecutor(max_workers = 100) as executor:        
	    while True:	
            
                for c in client.containers.list():
                    if c.name not in active_containers or c.name in completed_containers:
                        if c.name in completed_containers:
                            completed_containers.pop(c.name)
                        print (get_time() + c.name +': container found!!'	)
                        futures[executor.submit(collect_container_stats, c)] = str(c.name)		
                      

def GetHumanReadable(size,precision=2):
    suffixes=['B','KB','MB','GB','TB']
    suffixIndex = 0
    while size > 1024:
        suffixIndex += 1 #increment the index of the suffix
        size = size/1024.0 #apply the division
    return "%.3f %s"%(size,suffixes[suffixIndex])

def keyfunc(x):
    return x['name']

def measure_docker_stats():
    stats = {}
    with open('container_stats.json','r') as out:
        stats = json.load(out)
    #stats=[{'name':'karthika','val':2},{'name':'john','val':3},{'name':'karthika','val':1}]
    stats = sorted(stats,  key= lambda i: i['name'])
    overall_mem_usage = 0
    count = 0
    max_usage = 0
    max_cpu_usage = 0
    for name, group in itertools.groupby(stats, lambda i: i['name']):        
        print('----------')
        print ('CONTAINER :: '+name)
        items = [i for i in group]        
        avg_mem_usage = sum(i['memory_stats']['usage'] for i in items)/len(items)
        overall_mem_usage += avg_mem_usage
        print('Avg Memory Usage :: ' + GetHumanReadable(avg_mem_usage))
        for itm in items:            
            cpu_usage = (float(itm['cpu_stats']['cpu_usage']['total_usage']) / itm['cpu_stats']['system_cpu_usage']) *400
            print('CPU Usage :: ' + str(cpu_usage))
            max_cpu_usage = max(max_cpu_usage, cpu_usage)
            max_usage = max(max_usage, itm['memory_stats']['max_usage'])
        count += 1
    
    print('----------All Stats-----------------')
    print('Overall Avg Memory Usage :: '+ GetHumanReadable(overall_mem_usage/count))
    print('Overall Max Memory Usage :: '+ GetHumanReadable(max_usage))
    print('Overall Max CPU Usage :: '+ str(max_cpu_usage))
    
collect_stats(ANALYSIS_MAX_CONTAINERS)
