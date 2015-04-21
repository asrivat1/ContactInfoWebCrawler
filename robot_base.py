#!/usr/bin/env python

import lxml.html
from lxml.html import parse
import sys
from urlparse import urlparse
import urllib2
from urllib2 import urlopen
from urllib2 import Request

RC_OK = 200
logFile = None
contentFile = None

def main():
    logFile = open(sys.argv[1], "w")
    contentFile = open(sys.argv[2], "w")
    base_url = sys.argv[3]

    search_urls = [base_url]
    wanted_urls = []
    relevance = {}
    pushed = {}

    while search_urls:
        url = search_urls.pop()
        # skip if url is malformed or not http
        if urlparse(url).scheme != "http":
            continue

        # if status not ok or wrong content-type, continue
        req = Request(url)
        url_obj = urlopen(Request)
        logFile.write(url_obj.info())
        if url_obj.getcode() != RC_OK or not wanted_content(info["Content-Type"]):
            continue

        # GET request, same thing
        url_obj = urlopen(url)
        logFile.write(url_obj.info())
        if url_obj.getcode() != RC_OK or "text/html" not in url_obj.info()["Content-Type"]:
            continue

        # links
        extract_content(url_obj.read())
        related_urls = grab_urls(url_obj.read())

        for link in related_urls:
            if url not in pushed.keys():
                search_urls.append(url)
                pushed[url] = 1    

        # reorder the urls based on relevance
        search_urls = sorted(search_urls, key=(lambda a: relevance[a]))

def wanted_content(content):
    return "text/html" in content

def extract_content(content, url):
    email = None
    phone = None

    contentFile.write("(%s EMAIL %s)\n" % (url, email))
    logFile.write("(%s EMAIL %s)\n" % (url, email))

    contentFile.write("(%s PHONE %s)\n" % (url, phone))
    logFile.write("(%s PHONE %s)\n" % (url, phone))

def grab_urls(content):
    urls = {}

if __name__ == "__main__":
    main()
