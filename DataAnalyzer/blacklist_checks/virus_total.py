# Modified inital code by Omid

import base64
import sys
import json
from xml.dom.expatbuilder import theDOMImplementation
import psycopg2
import requests
import os
from datetime import datetime as dt
from datetime import timedelta
import time
import argparse
import random
import db_operations
from datetime import datetime


ApiKey = "2ac78e2efbda599b61f8f660d8aadbe887c76be9dc6f1f84e110571d8366b3fa"
db_host = '172.19.52.107'
db_name = "malvert_db_final"
db_password = "n0m0r3sp@m"
db_username ="malvert_db_admin"
db_port = "5432"


KeyList = ['071dab0c4f7501d7f0d329f831cdf942a6a7c38cfadc28b67b9e4eb8ec2b22ae',
'096592161db9f437b5a14040755aec2e3057a0b7cbeebf3a080032aa6a21a731',
'32c8089b06f0a681a76b49a22dfe2518e4d4d7f70085d08d299cf29122437bef',
'4c1bb6c459d12aa9ed297fe54b4869953cf8748665eced5d140e87c7a4b7e2f4',
'690e6c3311a8e3d615e0f796ce6b8ea1f02e7765d7941abb6a43d80d9711dda8',
'75a930592c2a82a885564c4fbb9f08e190d0d4b061cc901711231db9c857df67',
'7f8399998fc31c7498d3cd03752b35998542fe1de6f2201cf7a92d9c94ed4bee',
'962ccc7ce0cb624228f6c550c12d609f04bdafd70a334e01648998a4bdcf9b29',
'9ae64c5cdef8ba7a2299d306b198a2e17792dc73e670d0f8bf347625a3c75c96',
'ad334d76648b165b907d392ad3e8afd5aeec9d36df4239dc0ddd6624a2101b90',
'b0032c053e6838c6f821b281806f81dfb1eae01c809459a495ddaeabff827567',
'b5742fd019fd89ba4c5a2e0678004aec4899e09e605516e281662e04c9f7a762',
'c34e70738e2be6b34e3c965861abad9f56dec4395821d8b6fa14199bb750e244',
'd76379f41a1fb0e250c176bfc55853bcc65f64c85d2c02defd859fb2c16ff141',
'dc409c30ea9fd1984806afecae4bb50489877da68a4fb9b884b5736138710c55',
'57ec2a2563ac890238886742450a18a3b31d173c13c25adad02f63c8226fc4bc',
'7b39ce8331b78d1b393fd896314e27f313c0f7d647b12f69cd10b43747b11a57',
'2ac78e2efbda599b61f8f660d8aadbe887c76be9dc6f1f84e110571d8366b3fa']


#KeyList = ['b04043a00233894aa558e7d3c6801080b09de85d90f6129cfc25f9702146e220']

key_timing_dict = {'071dab0c4f7501d7f0d329f831cdf942a6a7c38cfadc28b67b9e4eb8ec2b22ae' : [ 0 , None],
'096592161db9f437b5a14040755aec2e3057a0b7cbeebf3a080032aa6a21a731' : [ 0 , None],
'32c8089b06f0a681a76b49a22dfe2518e4d4d7f70085d08d299cf29122437bef' : [ 0 , None],
'4c1bb6c459d12aa9ed297fe54b4869953cf8748665eced5d140e87c7a4b7e2f4' : [ 0 , None],
'690e6c3311a8e3d615e0f796ce6b8ea1f02e7765d7941abb6a43d80d9711dda8' : [ 0 , None],
'75a930592c2a82a885564c4fbb9f08e190d0d4b061cc901711231db9c857df67' : [ 0 , None],
'7f8399998fc31c7498d3cd03752b35998542fe1de6f2201cf7a92d9c94ed4bee' : [ 0 , None],
'962ccc7ce0cb624228f6c550c12d609f04bdafd70a334e01648998a4bdcf9b29' : [ 0 , None],
'9ae64c5cdef8ba7a2299d306b198a2e17792dc73e670d0f8bf347625a3c75c96' : [ 0 , None],
'ad334d76648b165b907d392ad3e8afd5aeec9d36df4239dc0ddd6624a2101b90' : [ 0 , None],
'b0032c053e6838c6f821b281806f81dfb1eae01c809459a495ddaeabff827567' : [ 0 , None],
'b5742fd019fd89ba4c5a2e0678004aec4899e09e605516e281662e04c9f7a762' : [ 0 , None],
'c34e70738e2be6b34e3c965861abad9f56dec4395821d8b6fa14199bb750e244' : [ 0 , None],
'd76379f41a1fb0e250c176bfc55853bcc65f64c85d2c02defd859fb2c16ff141' : [ 0 , None],
'dc409c30ea9fd1984806afecae4bb50489877da68a4fb9b884b5736138710c55' : [ 0 , None],
'57ec2a2563ac890238886742450a18a3b31d173c13c25adad02f63c8226fc4bc' : [ 0 , None],
'7b39ce8331b78d1b393fd896314e27f313c0f7d647b12f69cd10b43747b11a57' : [ 0 , None],
'2ac78e2efbda599b61f8f660d8aadbe887c76be9dc6f1f84e110571d8366b3fa' : [ 0 , None]
}

#key_timing_dict = {'b04043a00233894aa558e7d3c6801080b09de85d90f6129cfc25f9702146e220':[0,None]}


userAgents = ['Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
'Dalvik/1.6.0 (Linux; U; Android 4.4.4; WT19M-FI Build/KTU84Q)',
'Opera/9.80 (J2ME/MIDP; Opera Mini/4.2/28.3492; U; en) Presto/2.8.119 Version/11.10',
'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0',
'Mozilla/5.0 (Windows NT 6.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586',
'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) electron-tutorial/1.0.0 Chrome/47.0.2526.110 Electron/0.36.7 Safari/537.36',
'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) electron/1.0.0 Chrome/53.0.2785.113 Electron/1.4.3 Safari/537.36',
'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0']



parser = argparse.ArgumentParser()
parser.add_argument('--check',action='store_true' , help='checks the report after scans')
parser.add_argument('--scan',action='store_true' , help='scans the URL fon VT')

args = parser.parse_args()

args = vars(args)
print(args)

if( not args['check'] and not args['scan'] ):
    print ('wrong invocation. either --worker or --checker should be present , exiting')
    exit()

# initialize dates to now
for key in key_timing_dict:
    key_timing_dict[key][1] = dt.now()

print ( "init completed" )

def getKey ( thedic ):

    the_list = thedic.keys()
    while True :
        # if there is no item to vhoose from , wait for time to pass by!
        if( len(the_list ) ==0 ):
            time.sleep(2)
            the_list = thedic.keys()

        pick = random.choice( the_list  )

        the_list.remove( pick )

        if thedic[pick][1] is None :
            thedic[pick][1] = dt.now()

        if thedic[pick][1] <= dt.now() :
            return pick


# check if the prtogram is started as worker, start an  infinite loop
try :
        counter =0
        dbo = db_operations.DBOperator()
        while (True):         
            print('started')   
            #urls = ['https://disweb.deploys.io/channels/index.html?_sw-precache=527f447f356db3d634a7f7ca0aec7efe']
            urls = dbo.get_vt_check_urls() if args['check'] else dbo.get_vt_check_urls()
            print(len(urls))
            if( len(urls) > 0 ):
                key_index  =0
                for url in urls :                  
                    key = getKey(key_timing_dict )
                    #key = 'b04043a00233894aa558e7d3c6801080b09de85d90f6129cfc25f9702146e220'
                    print(url)

                    headers = {
                        "Accept-Encoding": "gzip, deflate",
                        "User-Agent": random.choice( userAgents )
                    }
                                      
                    if args['check']:
                        vt_url = 'https://www.virustotal.com/vtapi/v2/url/report'
                        params = {'apikey': key, 'resource': url}
                        
                    else:
                        vt_url = 'https://www.virustotal.com/vtapi/v2/url/scan'
                        params = {'apikey': key, 'url': url}  
                        

                    key_index+=1
                    counter+=1

                    try:
                        response = requests.post(vt_url,params=params, headers=headers)
                        print(response)
                        json_response = response.json()
                        results = response.text

                        detectionCount = 0
                        total =0
                        permaLink = ''
                        status = 'SCAN'
                        print (results)
                        
                        # figure sout the status and set it
                        if (not json_response['response_code'] == 1):
                            # the kurkl was not found
                            status = "UNKNOWN"
                        else:                            
                            if args['check']:
                                detectionCount = json_response["positives"]
                                total = json_response["total"]
                                percentage =float( total -  detectionCount)/ float( total)

                                print (percentage)

                                if(  percentage >= 0.90 ):
                                    status = "KNOWN GOOD"
                                elif percentage < 0.90 and percentage> 0.50  :
                                    status = "KNOWN UNCERTAIN"
                                elif percentage <= 0.50 :
                                    status = "KNOWN BAD"

                            permaLink = json_response["permalink"]


                        query_time = datetime.now()
                        result ={  'url':url,
                                    'vt_link': permaLink.replace('',''), 
                                    'positive':detectionCount, 
                                    'total':total, 
                                    'text': results.replace("'","''"),
                                    'status':status
                                }        
                        dbo.update_vt_table(result, query_time)
                        
                    except Exception as inst:
                        results = ""
                        status = 4
                        detectionCount = 0
                        print(inst)

                    finally:
                        time.sleep(10)
                    
                    if len(results.strip())<10 :
                        if key_timing_dict[key][0] ==1:
                            key_timing_dict[key][1] = dt.now() + timedelta(1, 0)
                        elif key_timing_dict[key][0] ==0 :
                            key_timing_dict[key][0] = 1
                            key_timing_dict[key][1] = dt.now() + timedelta(0, 15)
                    else :
                        key_timing_dict[key][0]=0
                        key_timing_dict[key][1] = dt.now() + timedelta(0,15)

            else :
                # if no records was found to be processed sleep for a short time ( not to overload the DB! )
                time.sleep(3600)
            

   
except Exception as e:
    print(e)
