
import docker 
import json
import time
import itertools
import pprint
client = docker.from_env()


def collect_docker_stats():
    with open('container_stats.json','w') as  f:
        f.write('[\n')
        while True:	
            for c in client.containers.list():
                stats = {}
                try:
                    stat = c.stats( stream=False)	
                    stats['name'] = stat['name']
                    stats['memory_stats'] = stat['memory_stats']
                    stats['cpu_stats'] = stat['cpu_stats']
                    stats['time'] = stat['read']
                    json.dump(stats,f, indent = True)
                    f.write(',\n')		
                except Exception as e:
                    continue
            time.sleep(60)        
            if not client.containers.list():
                break
        f.write(']')

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
    
measure_docker_stats()