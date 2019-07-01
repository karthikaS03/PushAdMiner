from urlparse import urlparse
import tldextract
import random


def split_url(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc, parsed_url.path


def get_sld(url):
    ext = tldextract.extract(url)
    return ext.registered_domain


def get_sleep_time(time):
    max_time = time * 2
    return random.randint(time, max_time)
