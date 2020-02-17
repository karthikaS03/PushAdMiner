

# We might need to add more. For example: line 2471 of test_delayed_js_nav_sa1.txt
multi_line_fields = ['code']
LOG_LINE_PREFIX = "  -*#$"
LOG_LAST_LINE = "---***###$$$"
IGNORE_URL_ENTRIES = ['chrome-extension', 'about:blank', '"about:blank"']


def ignore_entry_url(url):
    if not url:
        return True
    for ignore_url in IGNORE_URL_ENTRIES:
        if url.startswith(ignore_url):
            return True
    return False



def parse_line(line, entries):
    if "=" not in line:
        return
    try:
        key, value = (x.strip() for x in line.split("=", 1))
    except Exception as e:
        print (e)
        #ipdb.set_trace()
    entries[key] = value
    return key


def parse_multi_line_field(line, f):
    key, value = (x.strip() for x in line.split("=", 1))
    pos = f.tell()
    line = f.readline()
    while not (line.startswith(LOG_LAST_LINE) or
            line.startswith(LOG_LINE_PREFIX)):
        value = value + line
        pos = f.tell()
        line = f.readline()
    f.seek(pos)
    #print "parse_multi_line_field:", key, value
    return key, value


def parse_log_entry(f):
    # args exist in "DidCallV8MethodTemplate"
    args = {}
    pending_args_key = None
    attrs = {}
    pending_attr_key = None
    entries = {}
    line = f.readline()
    sw_register =False
    while line and  not line.startswith(LOG_LAST_LINE):
        try:
            #assert LOG_LINE_PREFIX in line
            line = line[len(LOG_LINE_PREFIX):]
            line = line.strip()
            if not line:
                line = f.readline()
                continue
            if line.startswith('arg_name'):
                pending_args_key = line.split("=", 1)[1].strip()
                if sw_register:
                    if 'url' in pending_args_key:
                        pending_args_key = 'Service_Worker_Register'
            if line.startswith('interface') and 'ServiceWorkerContainer' in line:
                sw_register=True
            elif line.startswith('arg_value'):
                args_value = line.split("=", 1)[1].strip()
                if sw_register :
                    args_value = args_value.replace('::JSON::','').replace('STRING!==','') if '::JSON::' in args_value and 'STRING!==' in args_value else args_value
                    sw_register=False 
                args[pending_args_key] = args_value
            elif line.startswith('attr_name'):
                pending_attr_key = line.split("=", 1)[1].strip().strip('"')
            elif line.startswith('attr_value'):
                attrs[pending_attr_key] = line.split("=", 1)[1].strip().strip('"')
            elif 'notification_message' in entries:
                entries['notification_message'].append(line)
            elif 'MalNotifications' in line:
                entries['notification_message'] = [' => '.join(line.split(':: ')[1:])] 
            else:
                try:
                    key = parse_line(line, entries)
                    if key in multi_line_fields:
                        key, value = parse_multi_line_field(line, f)
                        entries[key] = value
                except Exception as e:
                    print ("Exception: parse_log_entry()", e)
                    #ipdb.set_trace()   
            
            if not entries:
                entries['notification_message'] = [line.split(':: ')[1]] 
        except Exception as e:
            line = f.readline()
            continue   
        line = f.readline()
    # The extra line that was read is '---'; so, we can ignore that
    if args:
        entries['args'] = args
    if attrs:
        entries['attrs'] = attrs
    return entries
    # print entries


def peek_next_line(f):
    pos = f.tell()
    line = f.readline()
    f.seek(pos)
    return line


# Returns first line and rest of the entry as a dict
def peek_next_entry(f):
    pos = f.tell()
    line = f.readline()
    entry_dict = parse_log_entry(f)
    f.seek(pos)
    return line, entry_dict


# Read all lines till end of the entry and return as a string
def read_off_entry(f):
    lines = ""
    line = f.readline()
    while not line.startswith(LOG_LAST_LINE):
        lines += line
        line = f.readline()
    lines += line
    return lines


# Returns: line string if not log start and other log.
#          -1 if EOF
#           else None if log start
def not_log_start(f):
    pos = f.tell()
    line = f.readline()
    if not line:
        return -1
    if not line.startswith("LOG::"):
        return line
    else:
        f.seek(pos)



# Some log entries are single line (example: :DidCallV8MethodCallback)
# For these, we use this function to get the frame ID
def get_frame_id(line):
    frame_id = line.split('=')[1].split()[0]
    return frame_id
