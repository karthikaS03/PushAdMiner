#!/usr/bin/env python

"""Keeps local Google Safe Browsing cache in sync.

Accessing Google Safe Browsing API requires API key, you can find
more info on getting it here:
https://developers.google.com/safe-browsing/lookup_guide#GettingStarted

Code by Phani. Modified by Karthika
"""

import sys
import time
from datetime import datetime

from gglsbl import SafeBrowsingList
import config
import db_operations


def run_sync(sbl):
    try:
        sbl.update_hash_prefix_cache()
    except (KeyboardInterrupt, SystemExit):
        print ("Exiting")
        sys.exit(0)
    except Exception as e:
        print ("Error in syncing")
        print(e)
        time.sleep(30)


def main():
    sbl = SafeBrowsingList(config.gsb_key, db_path=config.gsb_db_path)
    #result = sbl.lookup_url('http://www.amazon.esp.bravaidea.com/AWS/mobil/signin.php?https://www.amazon.com/gp/product/B00DBYBNEE/ref=nav_prime_try_btn')
    #print(result)
    dbo = db_operations.DBOperator()
    while True:
        slds = dbo.get_gsb_queryable_slds()
        urls = dbo.get_gsb_queryable_urls()
        domain_urls = slds+urls
        print(len(domain_urls))
        query_time = datetime.now()
        print ("GSB Update time:", str(query_time))
        run_sync(sbl)
        print ("Got updated GSB list. Now looking up %s domains: %s" % (
                    len(domain_urls), str(datetime.now())))
        for d in domain_urls:
            print(d)
            try:
                result = sbl.lookup_url(d)
                print(result)
                result = "%s" % (result,)
                dbo.update_gsb_table(d, result, query_time)
            except Exception as e:
                print ("Exception. Skipping this domain: ", d, e)
            #print result
        print ("Done inserting into DB. Will update GSB list again", str(datetime.now()))
        time.sleep(3600)

if __name__ == '__main__':
    main()
