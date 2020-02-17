import psycopg2
from datetime import datetime

from config import *
import utils
import sys


class DBOperator:
    def __init__(self,):
        # Connect to database
        try:
            self.conn = psycopg2.connect("dbname=%s host=%s user=%s password=%s"
                                         % (db_name, db_host, db_user, db_password))
        except:
            print ("Unable to connect to database: " + db_name)
            sys.exit()
        self.cursor = self.conn.cursor()
        self.conn.set_session(autocommit=True)

    def get_gsb_queryable_slds(self,):
        self.cursor.execute("""
            SELECT distinct sld FROM slds WHERE sld NOT IN
                (SELECT domain FROM gsb WHERE last_flag IS TRUE)
            """)
        return [x[0] for x in self.cursor.fetchall()]

    def get_seed_urls(self,):
        self.cursor.execute("""
            SELECT seed_url_id,seed_url FROM seed_urls_top WHERE is_analyzed_desktop=true and visit_status=111
            """)
        return [x for x in self.cursor.fetchall()]

    def get_seed_urls2(self,):
        self.cursor.execute("""
            SELECT seed_url_id,seed_url FROM seed_urls_top WHERE has_permission_request=true and visit_status=1
            """)
        return [x for x in self.cursor.fetchall()]


    def get_gsb_queryable_urls(self,):
        self.cursor.execute("""
            SELECT distinct url FROM urls WHERE url NOT IN
                (SELECT domain FROM gsb WHERE last_flag IS TRUE)
            """)
        return [x[0] for x in self.cursor.fetchall()]

    def get_vt_scan_urls(self,):
        self.cursor.execute("""
            SELECT distinct url FROM urls WHERE url NOT IN
                (SELECT url FROM vt_results)
            """)
        return [x[0] for x in self.cursor.fetchall()]

    def get_vt_check_urls(self,):
        self.cursor.execute("""
            SELECT distinct url FROM urls WHERE url NOT IN
                (SELECT url FROM vt_results WHERE last_flag IS TRUE)
            """)
        return [x[0] for x in self.cursor.fetchall()]
    
    def update_gsb_table(self, sld, result, query_time):
        flag = (result != "None")
        se_flag = flag and ("SOCIAL_ENGINEERING" in result)
        text = result if flag else ""
        self.cursor.execute("""
            SELECT * FROM gsb WHERE domain = %s""", (sld,))
        if self.cursor.rowcount == 0:
            self.cursor.execute(""" INSERT INTO gsb (first_query_time, first_flag,
                                first_se_flag, first_result, domain) VALUES
                                (%s, %s, %s, %s, %s)""",
                                (query_time, flag, se_flag, text, sld))
        self.cursor.execute(""" UPDATE gsb SET last_query_time = %s,
                            last_flag = %s,
                            last_se_flag = %s,
                            last_result = %s WHERE domain = %s""",
                            (query_time, flag, se_flag, text, sld))


    def update_vt_table(self, result, query_time):
        flag = result['positive']>0
        se_flag = result['positive']>0
        
        self.cursor.execute("""
            SELECT * FROM vt_results WHERE url = %s""", (result['url'],))
        if self.cursor.rowcount == 0:
            self.cursor.execute(""" INSERT INTO vt_results (first_query_time, first_flag,
                                 first_result, url, vt_link,positive,total,status) VALUES
                                (%s, %s, %s, %s, %s, %s, %s, %s)""",
                                (query_time, flag, result['text'], result['url'], result['vt_link'], result['positive'],result['total'], result['status'] ))
        self.cursor.execute(""" UPDATE vt_results SET last_query_time = %s,
                            last_flag = %s,
                            last_result = %s ,
                            positive = %s, 
                            total = %s 
                            WHERE url = %s""",
                            (query_time, se_flag, result['text'],result['positive'],result['total'],result['url']))

    def bye(self,):
        self.cursor.close()
        self.conn.close()

    def update_urls_table(self, id, url, campaign, url_type, domain, url_path):
        self.cursor.execute("""
            SELECT count FROM urls WHERE domain = %s
            AND url_path = %s AND campaign = %s""", (domain, url_path, campaign))
        if self.cursor.rowcount == 0:
            self.cursor.execute(
                """
                INSERT INTO urls (site_id, url, domain, url_path, class,
                                  campaign, count)
                VALUES (%s, %s, %s, %s, %s, %s, 1)""",
                (id, url, domain, url_path, url_type, campaign))
        else:
            self.cursor.execute("""
                UPDATE urls SET url = %s, count = count + 1
                WHERE domain = %s AND url_path = %s AND
                campaign = %s
                """, (url, domain, url_path, campaign))

    def update_domains_seen_table(self, campaign, domain, time_seen):
        self.cursor.execute("""
            SELECT * FROM domains_seen WHERE domain = %s AND
            campaign = %s
            """, (domain, campaign))
        if self.cursor.rowcount == 0:
            self.cursor.execute(
                """
                INSERT INTO domains_seen (domain, campaign,
                                  first_seen, last_seen)
                VALUES (%s, %s, %s, %s)""",
                (domain, campaign, time_seen, time_seen))
        else:
            self.cursor.execute("""
                UPDATE domains_seen SET last_seen = %s
                WHERE domain = %s AND campaign = %s
                """, (time_seen, domain, campaign))

    def update_slds_table(self, domain):
        self.cursor.execute("""
            SELECT domain FROM slds WHERE domain = %s
            """, (domain,))
        if self.cursor.rowcount == 0:
            sld = utils.get_sld(domain)
            self.cursor.execute(
                """
                INSERT INTO slds (sld, domain)
                VALUES (%s, %s)""",
                (sld, domain))

    def update_campaigns_table(self, campaign, last_seen):
        self.cursor.execute("""
            SELECT * FROM campaigns WHERE campaign = %s
            """, (campaign,))
        if self.cursor.rowcount == 0:
            self.cursor.execute(
                """
                INSERT INTO campaigns (campaign, last_seen)
                VALUES (%s, %s)""",
                (campaign, last_seen))
        else:
            self.cursor.execute(
                """
                UPDATE campaigns SET last_seen = %s
                WHERE campaign = %s
                """, (last_seen, campaign))

    # Note we only insert a new url if it has a different
    # domain or url path. If both are same, we just update
    # an old entry even if the whole URL is different from the
    # stored one.
    def insert_url(self,id, url, campaign, url_type):
        domain, url_path = utils.split_url(url)
        time_seen = datetime.now()
        self.update_urls_table(id, url, campaign, url_type, domain, url_path)
        self.update_domains_seen_table(campaign, domain, time_seen)
        self.update_slds_table(domain)
        self.update_campaigns_table(campaign, time_seen)


    def insert_notification(self, notification_obj):
        try:
            self.cursor.execute(
                    """
                    INSERT INTO notification_details_latest (sw_url_id,notification_title, notification_body,notification_count, target_url, image_url, sw_url, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (notification_obj['log_id'],
                    notification_obj['push_notification_title'] , 
                    notification_obj['push_notification_body'] , 
                    notification_obj['notification_count'] , 
                    notification_obj['push_notification_target_url'] , 
                    notification_obj['push_notification_image'] , 
                    notification_obj['frame_url'],
                    notification_obj['timestamp'] ))
            if self.cursor.rowcount == 1:
                return True
        except Exception as e:
            print(e)
            return False
        return False


    def insert_request(self, req_obj):
        try:
            self.cursor.execute(
                    """
                    INSERT INTO page_requests(sw_url_id,frame_url,local_url,request_url,timestamp)
                    VALUES (%s, %s, %s, %s,%s)""",
                    (req_obj['log_id'],
                    req_obj['frame_url'], 
                    req_obj['local_frame_root_url'], 
                    req_obj['url'],                     
                    req_obj['timestamp'] ))
            if self.cursor.rowcount == 1:
                return True
        except Exception as e:
            print(e)
            return False
        return False


    def insert_logs(self,iteration, logs_obj):
        try:
            self.cursor.execute(
                    """
                    INSERT INTO desktop_detailed_logs_adguard (url_id, iteration, info, url, target_url, landing_url, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (logs_obj['log_id'],
                    iteration,
                    logs_obj['info'] , 
                    logs_obj['url'] , 
                    logs_obj['target_url'] , 
                    logs_obj['landing_url'] , 
                    logs_obj['timestamp'] ))
            if self.cursor.rowcount == 1:
                return True
        except Exception as e:
            print(e)
            return False
        return False 

    def insert_mobile_logs(self, logs_obj):
        try:
            self.cursor.execute(
                    """
                    INSERT INTO detailed_logs (pid, info, url, target_url, landing_url, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                    (logs_obj['pid'],
                    logs_obj['info'] , 
                    logs_obj['url'] , 
                    logs_obj['target_url'] , 
                    logs_obj['landing_url'] , 
                    logs_obj['timestamp'] ))
            if self.cursor.rowcount == 1:
                return True
        except Exception as e:
            print(e)
            return False
        return False 

    def insert_resource_info(self, id, iteration, file_name, file_hash, contacted_urls):
        try:
            self.cursor.execute(
                    """
                    INSERT INTO resource_info (url_id, iteration, file_name, file_hash, contacted_urls)
                    VALUES (%s, %s, %s, %s, %s)""",
                    (id,
                    iteration,
                    file_name , 
                    file_hash ,
                    contacted_urls))
            if self.cursor.rowcount == 1:
                return True
        except Exception as e:
            print(e)
            return False
        return False 

    def insert_service_wroker_event(self, sw_obj):
        try:
            self.cursor.execute(
                    """
                    INSERT INTO service_worker_details (sw_url_id,sw_url, target_url, timestamp, sw_event)
                    VALUES (%s, %s, %s, %s, %s)""",
                    (sw_obj['log_id'],
                    sw_obj['sw_url'] , 
                    sw_obj['target_url'] , 
                    sw_obj['timestamp'] , 
                    sw_obj['info']  ))
            if self.cursor.rowcount == 1:
                return True
        except Exception as e:
            print(e)
            return False
        return False


def test():
    dbo = DBOperator()
    dbo.insert_url('http://www.amazon.esp.bravaidea.com/AWS/mobil/signin.php?https://www.amazon.com/gp/product/B00DBYBNEE/ref=nav_prime_try_btn','','other')
    print (dbo.get_gsb_queryable_slds())


if __name__ == "__main__":
    test()