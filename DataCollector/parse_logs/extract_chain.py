# High priority things:
#

# Low priority things:
# python extract_chain_new.py ~/scratch/ad_jsgraph.log "http://www.reimagemac.com/lp/medd/index.php?tracking=expXML-mac&banner=Feed1_Open1_US_0.85_MAC4_86675&adgroup=&ads_name=Movies&keyword=86675&xml_uuid=28A11302-2457-4AE9-B5C6-A702D2745504&nms=1&lpx=mac4"
# Fix above
# When you see line 235505, , then you should take that runner into account when parsing
# line 236549. Keep a structure for these frames that are opened and when there is
# a WillLoadFrame, then immediately track that back and set up a redirection chain.
# Implemented the above fix using "pending_unknown_html_node_insert_frame_ids".
# TODO: Investigate this later and see what we are missing out.


# TODO: Inspect if Service workers are causing the bug below:
# line - 2443319 in ~/scratch/service_worker_bug.log has no runner.
# For now, this is simply handled by muting the assert in get_current_runner and in process set timeout
# Should inspect this further... later on

import argparse
import pprint
from collections import defaultdict
import timeout_decorator
from datetime import datetime
from database import db_operations

from parse_utils import parse_log_entry, ignore_entry_url, peek_next_line
from utils import process_urls

REDIRECT_LIMIT = 30
LOG_PARSER_TIMEOUT = 300  # Time out in seconds

debug_url = "https://serve.popads.net/s?cid=18&iuid=1206431516&ts=1528126113&ps=2612706935&pw=281&pl=%21BVlaJy45jInpvQV7Ao%2BO2Jn0l71RpjJ2ixo87lhiuyhSeLDZavOrsHysyuICxgcmDCOvj4pFWyvCGMy6bSYFBN9Vevq2T0DSaUsCrPuvVD3%2BL4hyNdQIxMWnlMsXTNHD6yM5sGiI6NdRgjdHCosRBWX8tBhBUZs4KY7Z9HUpvZpJZNnKLBRQI3hJLuVsc3HEhZSL8UVm0MfN0vbv8eD3wYKqXVSTwb%2FARskgZJa6AfV3PsUVOKflQzrtMNsM%2BrYg0xv16rAGJK8WCRVzgu0PYA%3D%3D&s=1375,738,1,1375,738&v=nt.v&m=275,350,1,0,0,275,350,4,0,2,-1,-1,1375,738,1375,738"
class ChainExtractor(object):
    # The generated load_url in this code doesn't match the one from the redirect chain.
    # Its better to pass it explicitly to this function (after getting it from crawler logs)
    def __init__(self, chrome_log_file,log_id, load_url=None):
        self.log_file = chrome_log_file
        self.load_url = load_url
        self.all_urls = set()
        self.ordered_urls=[]
        self.frame_urls = {}
        self.notification_logs=[]
        self.log_id=log_id
        self.notification_count=0

        # TODO: A frame can add a child frame that can also add an eventlistener(1),
        # or navigate frame(2)
        # While the JS spawned by the original frame is running? See below:
        # (1) line 64800 of test_js_eventlistener.txt
        # (2) line 115488 of test_iframe_src.txt
        # TODO: Are we introducing any ambiguity by not considering frame id
        # along with URL in redirections?
        # Consider this in the light of inter-frame redirections that we
        # might be missing othwerwise.
        # TODO: Our tracking of redirections misses this:
        # Consider what happens when a script includes an inline script
        # using dom.write. Since the newly added script will have the
        # original base HTML as the URL, that base HTML will be taken as the chain
        # originator.
        # But, probably, the above case is not that common as its not useful.

        # of form: frame_id --> [[],[],[]...]
        # The list can be: [frame_id, "compiled_script", script_id, script_src_URL]
        #                : [frame_id, "event_listener", event_target_id, event_name]
        #                : [frame_id, "scheduled_action", "function" or "code", value]
        #                : [frame_id, "request_animation_frame", callback_id]
        self.caller_stack = {}
        # of form: frame_id --> (target_id, event_name)

        # Push state or replace state navigation is logged in two entries
        # So, the first entry is saved below until the second entry is
        # parsed.
        self.pending_push_states = {}  # Frame ID --> src_url

        self.pending_handle_event = {} # Frame ID --> target

        # Temporary work-around for tracking window opens
        self.pending_window_open_frame_id = None

        self.pending_unknown_html_node_insert_frame_ids = set()
        self.frames_so_far = set()

        # Temporary work-around for bug related to unexplained compile scripts:
        self.ignore_script_run = None

        # New: Redirection nodes could be:
        # (frame_id, "URL", the_url)
        # (frame_id, "type", event_stuff)  --> type could be event_listener or scheduled_action

        # The redirection nodes could be:
        # EventHandler: (frameID, targetID, event_name)
        # URL
        # ScheduledAction: (frameID, code) # Note: its the same for both kinds of SAs
        # Destination --> (Source, "Reason")
        self.redirections = {}
        self.load_frame_redirections = {}
        self.parent_frames = {}
        self.child_frames = defaultdict(list)
        self.collect_redirects()
        self.process_load_frame_redirects()

    def debug_get_event_listeners(self,):
        ret_stuff = []
        for dest in self.redirections:
            if dest[1] == "event_listener":
                ret_stuff.append(dest)
        return ret_stuff

    def check_any_upstream_url_link(self, url):
        for dest in self.redirections:
            # Excluding cases where src is a about:blank URL
            if dest[1] == "URL" and dest[2] == url and not (
                    self.redirections[dest][0][1] == "URL" and
                    self.redirections[dest][0][2].strip('"') != 'about:blank'):
                return self.redirections[dest]

    def get_root_frame(self, frame_id):
        while frame_id in self.parent_frames:
            if frame_id == self.parent_frames[frame_id]:
                return frame_id
                #ipdb.set_trace()
            frame_id = self.parent_frames[frame_id]
        return frame_id

    # Check if any of the relatives of frame_id are in the frame_set
    # If so, return the matching relative.
    # If not, return None
    def check_frame_relation(self, frame_id):
        root_frame_id = self.get_root_frame(frame_id)
        frame_set = set(self.caller_stack.keys())
        # Frame Tree traversal DFS
        traversal_stack = [root_frame_id]
        while len(traversal_stack) != 0:
            frame_id = traversal_stack.pop()
            if frame_id in frame_set:
                return frame_id
            if frame_id in self.child_frames:
                traversal_stack = traversal_stack + self.child_frames[frame_id]
        return None

    @timeout_decorator.timeout(LOG_PARSER_TIMEOUT)
    def process_load_frame_redirects(self):
        for dest, src in self.load_frame_redirections.items():
            #if dest[2] == debug_url:
            #    ipdb.set_trace()
            if dest not in self.redirections:
                self.redirections[dest] = src

    # Check if the frame or its parent, one of its kids or its siblings has started
    # the current JS execution.
    # If so, return the relevant caller frame ID. If not, return None
    def check_frame_id_call_stack(self, frame_id):
        if frame_id in self.caller_stack:
            return frame_id
        # Check Parent
        if (frame_id in self.parent_frames and
                self.parent_frames[frame_id] in self.caller_stack):
            return self.parent_frames[frame_id]
        # Check kids, get grand-kids
        grand_kids = []
        if frame_id in self.child_frames:
            for child_id in self.child_frames[frame_id]:
                if child_id in self.caller_stack:
                    return child_id
                if child_id in self.child_frames:
                    grand_kids = grand_kids + self.child_frames[child_id]
        # Check siblings
        if frame_id in self.parent_frames:
            parent_id = self.parent_frames[frame_id]
            for sibling_id in self.child_frames[parent_id]:
                if sibling_id in self.caller_stack:
                    return sibling_id
        # Check Grand kids
        for grand_kid_id in grand_kids:
            if grand_kid_id in self.caller_stack:
                return grand_kid_id
        return self.check_frame_relation(frame_id)


    def get_current_runner(self, frame_id, main_frame_id=None):

        if len(self.caller_stack) == 0:
            return None
        
        frame_id = self.check_frame_id_call_stack(frame_id)
        try:
            assert (frame_id or
                main_frame_id in self.caller_stack)
        except:
            #ipdb.set_trace()
            return
        if frame_id is None:
            frame_id = main_frame_id
        assert len(self.caller_stack[frame_id]) > 0
        # Note: If returning the last one gives any problems (i.e. no further redirecting parent...)
        # then, may be we can return one above and so on... until we get to the root.
        # Note: returning 0 is wrong: sometimes, there can be element in the call stack who are not
        # exactly ancestors. For example, a handle event can happen while a scheduled action is running.
        return self.format_runner(self.caller_stack[frame_id][-1])

    # Format runner for storing in redirection chain.
    def format_runner(self, runner):
        if runner[1] == "compiled_script":
            return (runner[0], "URL", runner[3])
        elif runner[1] == "request_animation_frame":
            return runner
        # If runner has 4 elements
        else:
            return (runner[0], runner[1], (runner[2], runner[3]))


    def update_redirections(self,local_frame, frame_id, dst, src, reason, timestamp):
        src = src.replace('"','').replace(' ','')
        src = src.strip('#')
        
        if dst in self.all_urls:
            return True
    
        if src not in self.all_urls:
            self.all_urls.add(src)
            self.ordered_urls.append((timestamp,src))
        self.all_urls.add(dst)
        self.ordered_urls.append((timestamp,dst))        
        
        dst = {'timestamp':timestamp, 'local_frame_id':local_frame, 'target_frame_id':frame_id, 'target_url': dst}
        if src in self.frame_urls:  
            if reason in self.frame_urls[src]:         
                self.frame_urls[src][reason].extend([dst])
            else:
                self.frame_urls[src].update({reason:[dst]})           
        else:
            self.frame_urls[src] = {reason:[dst]}
        
        return True

    # Process entries where frame or frame_root URLs are to be used based
    # on which one might be empty
    def process_frame_based_entries(self, entries, key, reason, timestamp):
        assert 'frame_url' in entries
        if entries['frame_url'].strip('"') != "about:blank":
            frame_id = entries['frame']
            try:
                self.update_redirections(frame_id,frame_id,
                    entries[key], entries['frame_url'], reason, timestamp)
            except:
                pass
                #ipdb.set_trace()
        #elif entries['local_frame_root_url'].strip('"') != "about:blank":
        else:
            frame_id = entries['local_frame_root']
            self.update_redirections(frame_id,
                frame_id, entries[key], entries['local_frame_root_url'], reason, timestamp)
        #self.update_redirections(
        #   entries['frame_url'], entries['local_frame_root_url'], 'Parent Frame')

    def process_server_redirect(self, f, timestamp):
        entries = parse_log_entry(f)
        self.update_redirections(entries['frame'],
            entries['frame'], entries['request_url'], entries['redirect_url'],
            "Server Redirect", timestamp)

    # Frame IDs are the same across URLs.
    def process_meta_refresh(self, f, timestamp):
        entries = parse_log_entry(f)
        self.process_frame_based_entries(entries, 'refresh_url', "Meta Refresh", timestamp)

    # window.location
    # happens with the same FrameID
    def process_js_navigation(self, f, timestamp):
        entries = parse_log_entry(f)
        self.update_redirections(entries['local_frame_root'],
            entries['frame'], entries['url'], entries['local_frame_root_url'],
            'JS Navigation', timestamp)
       

    def process_window_open(self, f, timestamp):
        entries = parse_log_entry(f)
        self.pending_window_open_frame_id = entries['frame']
        #self.redirections[entries['url']] = (self.get_current_runner(entries['frame']),
        #                                      'Window Open')

    def process_load_frame(self, f, timestamp):
        entries = parse_log_entry(f)
        
        # Window Open
        frame_id = entries['frame']

       
        main_frame_id = entries['main_frame']

        if self.load_url is None and entries['load_url'].startswith('http'):
            self.load_url = entries['load_url']

        dest = (frame_id, "URL", entries['load_url'])
        dest_2 = (frame_id, entries['load_url'])

        # Else, its a window open that probably happened because of the current runner
        if (self.pending_window_open_frame_id and
                self.check_frame_id_call_stack(self.pending_window_open_frame_id)):
            runner = self.get_current_runner(self.pending_window_open_frame_id)
            self.redirections[dest] = (
                                runner, 'Window Open')
            self.parent_frames[frame_id] = self.pending_window_open_frame_id
            self.child_frames[self.pending_window_open_frame_id].append(frame_id)
            self.pending_window_open_frame_id = None
            
            return

     

        # Else (if no runner), then its a totally unexplained window open
        # We can atlead log the load frame.
        if entries['frame_url'].strip('"') != "about:blank":
            
            self.load_frame_redirections[(frame_id, "URL", entries['load_url'])] = (
                                    (frame_id, "URL", entries['frame_url']), "Load Frame")           
            self.update_redirections(entries['local_frame_root'],frame_id,entries['load_url'],entries['frame_url'],'Load Frame', timestamp)
        elif entries['local_frame_root_url'].strip('"') != "about:blank":
            self.load_frame_redirections[(frame_id, "URL", entries['load_url'])] = (
                (frame_id, "URL", entries['local_frame_root_url']), "Load Frame")
            self.update_redirections(entries['local_frame_root'],frame_id,entries['load_url'],entries['local_frame_root_url'],'Load Frame', timestamp)
            
        self.process_frame_based_entries(entries, 'load_url', "Load Frame", timestamp)

    def start_script_run(self, f, timestamp):
        # TODO: Add script ID for cross checking
        entries = parse_log_entry(f)
        # Note: There might be an active JS Runner already
        # (Ex: line 2504 in test_delayed_js_nav_sa1.txt)
        frame_id = entries['frame']
        # Script run mapping to frame_url only makes sense when there
        #  is no current runner. If not, it could be due to say, a
        # scheduled action code or eval etc.
        # Its parent_farm or child frame could also be there.
        # Hence calling check_frame_id_call_stack
        related_frame_id = self.check_frame_id_call_stack(frame_id)

        if related_frame_id is None:
            if not entries['url'] and not self.ignore_script_run:
                self.ignore_script_run = entries['frame']
                return

            try:
                assert (entries['url'])
            except Exception:
                #ipdb.set_trace()
                return
            self.caller_stack[frame_id] = []
            dest = (entries['frame'], 'URL', entries['url'])
            dst_2 = (entries['frame'],entries['url'])
            # When a script is dynamically loaded by doc.write or v8setattribute,
            # then, we already set the redirection by this stage. We should make
            # sure not to rewrite it.
            if dest not in self.redirections:
                self.process_frame_based_entries(entries, "url", "Script Load",timestamp)
            related_frame_id = frame_id
        self.caller_stack[related_frame_id].append((frame_id,
            "compiled_script", entries["scriptID"], entries['url']))

    def stop_script_run(self, f, timestamp):
        
        entries = parse_log_entry(f)
        
        frame_id = entries['frame']
        if frame_id == self.ignore_script_run:
            self.ignore_script_run = None
            return
        frame_id = self.check_frame_id_call_stack(frame_id)
        try:
            assert self.caller_stack[frame_id][-1][1] == "compiled_script"
        except:
            return
        del self.caller_stack[frame_id][-1]
        if len(self.caller_stack[frame_id]) == 0:
            del self.caller_stack[frame_id]
     
    def set_child_frame(self, entries):
        frame_id = entries['frame']
        child_frame_id = entries['child_frame']
        self.parent_frames[child_frame_id] = frame_id
        self.child_frames[frame_id].append(child_frame_id)
    
    def process_notification(self, f, timestamp):
        entries = parse_log_entry(f)
        frame_url = entries['frame_url']
        url = entries['push_notification_target_url']
        entries['push_notification_target_url'] = url[url.index('http'):] if 'http' in url else ''
        notification_target_url = entries['push_notification_target_url']
        notification_img_url = entries['push_notification_image']
        notification_icon_url= entries['push_notification_icon'] if 'push_notification_icon' in entries else ''
        notification_body = entries['push_notification_body']
        notification_title = entries['push_notification_title']   
        notification_tag = entries['push_notification_tag'] if 'push_notification_tag' in entries else ''
        entries['timestamp'] = timestamp     
        entries['log_id'] = self.log_id
        self.notification_count +=1
        entries['notification_count'] = self.notification_count
        dbo = db_operations.DBOperator()
        #dbo.insert_notification(entries)
        self.notification_logs.append({'timestamp':timestamp,'message':'Notification from: '+frame_url})
        self.notification_logs.append({'timestamp':timestamp,'message':'Notification shown: '+
        ' && '.join([str(self.notification_count),notification_title,notification_body,frame_url,notification_tag, notification_img_url, notification_target_url,notification_icon_url])})
    
    def process_requests(self, f, timestamp):
        entries = parse_log_entry(f)
        entries['timestamp'] = timestamp     
        entries['log_id'] = self.log_id
        dbo = db_operations.DBOperator()
        dbo.insert_request(entries)


    def process_notification_click(self, f, timestamp):
        entries = parse_log_entry(f)
        url = entries['push_notification_target_url']
        entries['push_notification_target_url'] = url[url.index('http'):] if 'http' in url else ''
        notification_target_url = entries['push_notification_target_url']
        notification_img_url = entries['push_notification_image']
        notification_body = entries['push_notification_body']
        notification_title = entries['push_notification_title']
        notification_icon_url = entries['push_notification_icon'] if 'push_notification_icon' in entries else ''
        notification_tag = entries['push_notification_tag'] if 'push_notification_tag' in entries else ''
        entries['timestamp'] = timestamp
        entries['log_id'] = self.log_id
        self.notification_logs.append({'timestamp':timestamp,'message':'Notification click: '+
        ' && '.join(['',notification_title,notification_body,'',notification_tag, notification_img_url, notification_target_url, notification_icon_url])})
    
    def process_notification_message(self, f, timestamp):
        entries = parse_log_entry(f)
        self.notification_logs.append({'timestamp':timestamp,'message': ' '.join(entries['notification_message'])})

    def process_method_template(self, f, timestamp):
        entries = parse_log_entry(f)
        service_worker_file=None
        if 'args' in entries and 'Service_Worker_Register' in entries['args']:
            service_worker_file = entries['args'].get('Service_Worker_Register')
            self.notification_logs.append({'timestamp':timestamp,'message': 'Service Worker Registered :: '+ service_worker_file})

    @timeout_decorator.timeout(LOG_PARSER_TIMEOUT)
    def collect_redirects(self,):
        if self.log_file:
            line = self.log_file.readline()
            while line:
                try:
                    #if "060217.434604" in line:
                    #    ipdb.set_trace()
                    method= None
                    timestamp = None
                    #print(line)
                    if 'LOG::Forensics' in line and line.count(':')>1:
                        time = line.split(':')[2] 
                        try:
                            timestamp = datetime(2019, int(time[:2]), int(time[2:4]), int(time[5:7]),int(time[7:9]), int(time[9:11]), int(time[12:]))
                        except Exception as e:
                            timestamp = None
                    if "::DidReceiveMainResourceRedirect" in line:
                        method = self.process_server_redirect
                    elif "::DidHandleHttpRefresh" in line:
                        method = self.process_meta_refresh
                    elif "::WillNavigateFrame" in line:
                        method = self.process_js_navigation
                    elif "::WindowOpen" in line:
                        method = self.process_window_open
                    elif "::WillLoadFrame" in line:
                        method = self.process_load_frame
                    elif "::DidCompileScript" in line:
                        method = self.start_script_run
                    elif "::DidCallV8MethodTemplate" in line:
                        method = self.process_method_template
                    elif "::DidRunCompiledScriptEnd" in line:
                        method = self.stop_script_run
                    elif "::WillShowNotification" in line:
                        method = self.process_notification
                    elif "::WillClickNotification" in line:
                        method = self.process_notification_click
                    elif "::WillSendRequest" in line:
                        method = self.process_requests
                    elif "::DebugPrints" in line:
                        method = self.process_notification_message
                    if method:
                        method(self.log_file,str(timestamp))
                except Exception as e:
                    print('collect redirect')
                    print(e)
                line = self.log_file.readline()

    def find_frame_id(self, url):
        found = []
        for key in self.redirections:
            if key[1] == "URL" and key[2] == url:
                found.append(key[0])
        return found

    def key_lookup(self, key):
        if key in self.redirections:
            return self.redirections[key]
        ## For some ads (example: RevenueHits network ads) the event listener set up and
        ## invocation code Frame IDs don't match. Hence we have this quick fix method to
        ## ignore the Frame IDs. The matching of key[2] itself is big evidence that these
        ## 2 are related anyway.
        ## QUICKFIX
        if key[1] == "event_listener":
            for existing_key in self.redirections:
                if (existing_key[1] == "event_listener" and
                    existing_key[2] == key[2]):
                    return self.redirections[existing_key]
        return None

    @timeout_decorator.timeout(LOG_PARSER_TIMEOUT)
    def get_redirect_chain(self, finald):
        #print self.redirections
        redirections = []
        redirection_set = set()
        found = self.find_frame_id(finald)
        #print "Found FrameIDs:", found
        if len(found) == 0:
            print ("Could not find frameID for the given URL", finald)
            return
        key = (found[0], "URL", finald)
        i = 0
        lookup = self.key_lookup(key)
        while lookup is not None:
            i += 1
            #print "*** ", key, self.redirections[key][1]
            if (key, lookup[1]) in redirection_set:
                print ("Loop detected; breaking...")
                break
            redirections.append((key, lookup[1]))
            redirection_set.add((key, lookup[1]))
            key = lookup[0]
            lookup = self.key_lookup(key)
            # End criteria
            if key[1] == "URL" and key[2] == self.load_url:
                break
            if i == REDIRECT_LIMIT:
                break
        redirections.append((key, "FIRST"))
        #print "*** ", key
        #ipdb.set_trace()
        return redirections

    def find_redirect_chain(self, url):
        redirect_reasons = set(['Load Frame','Server Redirect','Meta Refresh','JS Navigation'])
        redirections=[]
        if url  not in self.frame_urls:
            return redirections
        next_urls = self.frame_urls[url] 
        
        if not any(key in redirect_reasons for key in next_urls):
            return redirections        
        landing_url = ''
        
        for reason in redirect_reasons:
            if reason in next_urls:
                redirect_items = next_urls[reason]
                for redirect in redirect_items:
                    if redirect['local_frame_id']== redirect['target_frame_id']:
                        target_url = redirect['target_url']
                        
                        redirect['from_url'] = url
                        '''
                        redirection={}
                        redirection['timestamp'] = redirect['timestamp']
                        redirection['target_url']=target_url
                        redirections.append(redirection)
                        redirections.extend(self.find_redirect_chain(target_url))
                        '''
                        redirections.append(redirect)
                        redirection_chain = self.find_redirect_chain(target_url)
                        if redirection_chain:
                            landing_url=redirection_chain[0]['landing_url']
                        else:
                            landing_url=target_url

                        #redirections = redirections + [target_url] + self.find_redirect_chain(target_url)
                        #self.ordered_urls.append(redirect)
        for redirect in redirections:
            redirect['landing_url'] = landing_url
        self.ordered_urls.extend(redirections)
       
        return redirections
    

    def get_all_redirections(self):      
        redirections = []
        if '' in self.frame_urls:
            start_urls = self.frame_urls['']      
            #print('***************start urls***********************') 
            #pprint.pprint(start_urls)     
            
            for item in start_urls['Load Frame']:
                
                url = item['target_url']
                #url)
                chain =self.find_redirect_chain(url)
                #print(chain)
                if len(chain)>0:
                    item['landing_url'] = chain[0]['landing_url']
                    item['from_url'] = ''
                    self.ordered_urls.append(item)
                    redirections.append({'initial_url':url,'redirection_chain':chain})
                else:
                    item['from_url']=''
                    item['landing_url']=url
                    
                    self.ordered_urls.append(item)
            #pprint.pprint(redirections)
        return redirections
                        

def service_worker_requests_logs(id, log_file):
    sw_logs =[]
    if log_file:
        line = log_file.readline()
        while line:
            if 'Service Worker' in line:
                sw_item = {}
                while line:                    
                    if 'Service Worker' in line:
                        time = line[line.index('@')+1:line.index(']')]
                        time = datetime.strptime(time, ' %Y-%m-%d %H:%M:%S ')
                        sw_item['timestamp']=str(time)
                        sw_item['info'] = line[:line.index('@')].strip('').replace('[','')
                    if 'Origin' in line:
                        sw_item['sw_url'] = line.split('::')[1]
                    if 'URL ::' in line:
                        #print(line)
                        sw_item['target_url'] = line.split('::')[1]
                    if '||' in line or '***' in line:                        
                        if sw_item:
                            if 'sw_url' not in sw_item:
                                sw_item['sw_url']=''
                            sw_item['log_id'] = id
                            sw_logs.append(sw_item)
                            dbo = db_operations.DBOperator()
                            dbo.insert_service_wroker_event(sw_item)
                        break
                    line = log_file.readline()
            line = log_file.readline()
    return sw_logs


def print_events(id,count, log_urls):
    with open('event_logs/'+id+'_'+str(count)+'.log','w') as f:
        f.write('*************************************\n')
        f.write('Events for ID ::'+id+'\n')
        f.write('*************************************\n')
        f.write('\n')
        for item in log_urls:
            f.write('['+ item['timestamp']+']\n')
            if 'info' in item:
                f.write('\tSW EVENT :: ' + item['info']+'\n')
            if 'sw_url' in item:
                f.write('\tSW URL :: ' + item['sw_url']+'\n')
            if 'target_url' in item:
                f.write('\tTarget URL :: ' + item['target_url']+'\n')
            elif 'message' in item:
                f.write('\t NOTIFICATION :: '+item['message']+'\n')

def format_logs_for_db(id, log_urls):
    def get_tag(msg, tag=True, body=False):
        notification_tag=None  
        print(msg)
        if '&&' in msg:
            msgs = msg.split('&&')        
            notification_tag = msgs[4].strip()                   
            title_body = ' '.join([msgs[1].strip(),  msgs[2].strip()])
            notification_tag = title_body if not tag and body else notification_tag if tag else msgs[1].strip()
        elif ' => ' in msg:
            msgs = msg.split(' => ')            
            title = msgs[0].split(':')[1].strip()
            body =  msgs[1].strip() if len(msgs)>1 else ''
            notification_tag = (title + ' ' + body)            
        else:                       
            title = msg.split(':')[1].strip()
            if 'proxy' not in title.lower():               
                notification_tag = title              
        if notification_tag:
            try:
                notification_tag =notification_tag.encode('ascii', 'ignore')
            except:
                notification_tag = notification_tag.decode('ascii', 'ignore')
        return notification_tag


    formatted_logs =[]
    notifications_log = []
    k=0
    next_ind=0
    for ind,item in enumerate(log_urls):
        notification_flag = False
        log = { 'log_id': id,
                'info':'',
                'url':'',
                'target_url':'',
                'landing_url':'',
                'timestamp':None,
                }
        if 'info' in item:
            log['info'] = item['info'].strip()
        if 'sw_url' in item:
            log['url'] = item['sw_url']
        if 'target_url' in item:
            log['target_url'] = item['target_url'].strip()
        if 'landing_url' in item:
            log['info'] ='Redirect'
            log['landing_url']= item['landing_url'].strip()
            log['url'] = item['from_url'].strip()
        if 'timestamp' in item:
            log['timestamp']=item['timestamp']
        if 'message' in item:
            log['info'] = item['message'].strip()
            if 'Notification click' in item['message']:
                print('click')
                k=max(next_ind,ind)+1
                msg = item['message']                
                is_tag = '&&' in msg
                is_body = '=>' in msg
                notification_tag = get_tag(msg, is_tag,is_body)  
                #print(msg)              
                try:
                    #pprint.pprint(log)
                    #print(k,ind,next_ind)
                    try:
                        t1 = datetime.strptime(log['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
                    except:
                        t1 = datetime.strptime(log['timestamp'], '%Y-%m-%d %H:%M:%S')
                    while k<len(log_urls):
                        next_item = log_urls[k]      
                        try:                  
                            t2 = datetime.strptime(next_item['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
                        except:
                            t2 = datetime.strptime(next_item['timestamp'], '%Y-%m-%d %H:%M:%S')
                        
                        if 'message' in next_item and 'OpenWindow' in next_item['message'] and (t2-t1).total_seconds()<120 :
                            #pprint.pprint(next_item)
                            landing_url = next_item['message'].split('  => ')[1]
                            start_url = landing_url.strip()
                            log['landing_url'] = start_url
                            next_ind=k
                            while k<len(log_urls)-1:
                                k += 1
                                next_item = log_urls[k]
                                if 'landing_url' in next_item :                                    
                                    if start_url in  next_item['from_url']:
                                        #print(start_url,next_item['landing_url'])
                                        log['landing_url'] = next_item['landing_url']
                                        log['target_url'] = start_url
                                        #pprint.pprint(log)
                                        break
                            break
                        k += 1                        
                    if notifications_log:
                        notification_log = {}                        
                        for i,n in enumerate(notifications_log):
                            not_tag = get_tag(n['info'], is_tag,is_body)    
                            print(notification_tag, not_tag)                        
                            if not_tag and notification_tag == not_tag:
                                print('matched')
                                notification_log = n
                                notification_log['landing_url']= log['landing_url']
                                notification_log['target_url'] = log['target_url']
                                formatted_logs.append(notification_log)
                                notifications_log.pop(i)                                
                                break
                        '''
                        if not notification_found:
                            notification_log = notifications_log.pop(0)
                            notification_log['landing_url']= log['landing_url']
                            formatted_logs.append(notification_log)
                        '''
                except Exception as e:
                    print('Format logs Exception ',e)

            if 'OpenWindow' in item['message']:
                k=max(next_ind,ind)+1
                landing_url = item['message'].split('  => ')[1]
                start_url = landing_url.strip()
                while k<len(log_urls):                    
                    next_item = log_urls[k]
                    if 'landing_url' in next_item:
                        if start_url in  next_item['from_url']:
                            log['landing_url'] = next_item['landing_url']
                            break                    
                    k += 1           
            if 'Notification shown' in item['message']:
                notification_flag = True
        if  notification_flag:
            notifications_log.append(log)
        else:
            formatted_logs.append(log)
    for itm in notifications_log:
        itm['landing_url']=''
        formatted_logs.append(itm)
        print('extra')
    #pprint.pprint(formatted_logs)
    return formatted_logs

def parse_log(id,count, chrome_log_file, sw_log_file):

    
    try:
        ce = ChainExtractor(chrome_log_file, id)        
        ce.ordered_urls=[]
        ce.get_all_redirections()        
        logs_urls = ce.ordered_urls + ce.notification_logs
        sw_logs = service_worker_requests_logs(id, sw_log_file)       
        logs_urls = logs_urls + sw_logs 
        logs_urls.sort(key=lambda r: r['timestamp'])
        print_events(id,count, logs_urls)
        result =  format_logs_for_db(id,logs_urls)
        return result
    except Exception as e:
        print(e)
        return []
    

    '''
     print('***** Detailed Logs*********')
    pprint.pprint(logs_urls)
   
    
    print('*******Redirection chains************')
    pprint.pprint(redirections)
    print('***** Detailed Logs*********')
    pprint.pprint(logs_urls)
    
    print('***************Frame URLS**********')
    #pprint.pprint(ce.frame_urls)
    
    print('*******Redirection chains************')
    pprint.pprint(redirections)
    #print_events(id, logs_urls)
    '''


