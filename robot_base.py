#!/usr/bin/env python

import lxml.html
from lxml.html import parse
from lxml.html import document_fromstring
import sys
from urlparse import urlparse
import urllib2
from urllib2 import urlopen
from urllib2 import Request
from collections import defaultdict
import re

RC_OK = 200
logFile = open(sys.argv[1], "w")
contentFile = open(sys.argv[2], "w")
relevance = defaultdict(lambda: 0)
wanted_urls = []

def main():
    base_url = sys.argv[3]

    search_urls = [base_url]
    pushed = {}

    while search_urls:
        url = search_urls.pop()
        logFile.write(url + "\n")
        # skip if url is malformed or not http
        if urlparse(url).scheme != "http":
            continue

        # if status not ok or wrong content-type, continue
        req = Request(url)
        try:
            url_obj = urlopen(req)
        except urllib2.HTTPError:
            continue

        logFile.write(str(url_obj.info()))
        if url_obj.getcode() != RC_OK or not wanted_content(url_obj.info()["Content-Type"], url):
            continue

        # GET request, same thing
        url_obj = urlopen(url)
        logFile.write(str(url_obj.info()))
        if url_obj.getcode() != RC_OK or "text/html" not in url_obj.info()["Content-Type"]:
            continue

        # links
        html = url_obj.read()
        extract_content(html, url)
        related_urls = grab_urls(html, url)

        for link in related_urls:
            if link not in pushed.keys():
                search_urls.append(link)
                pushed[link] = 1

        # reorder the urls based on relevance
        search_urls = sorted(search_urls, key=(lambda a: relevance[a]))

        # print any wanted urls we have found up til this point
        if wanted_urls:
            print "Wanted urls:"
        while wanted_urls:
            print wanted_urls.pop()
        print


def wanted_content(content, url):
    # check if this is something we are looking for
    if "pdf" in content or "postscrpt" in content:
        wanted_urls.append(url)
    return "text/html" in content

def extract_content(content, url):
    emails = []
    phones = []
    cities = []

    # search through document and find emails and phones and addresses
    emails = re.findall(r"[^\s()<>]+@[A-Za-z0-9-]+\.[A-Za-z]+", content)
    phones = re.findall(r"\(?\d{3}\)?-?\d{3}-?\d{4}", content)
    cities = re.findall(r"[A-Za-z]+, [A-Za-z]+ \d{5}", content)

    for email in emails:
        contentFile.write("(%s EMAIL %s)\n" % (url, email))
        logFile.write("(%s EMAIL %s)\n" % (url, email))

    for phone in phones:
        contentFile.write("(%s PHONE %s)\n" % (url, phone))
        logFile.write("(%s PHONE %s)\n" % (url, phone))

    for city in cities:
        contentFile.write("(%s CITY %s)\n" % (url, city))
        logFile.write("(%s CITY %s)\n" % (url, city))

def grab_urls(content, url):
    urls = {}
    domain = urlparse(url).netloc
    html = document_fromstring(content)
    html.make_links_absolute(url, resolve_base_href=True)

    for element, attribute, link, pos in html.iterlinks():
        if attribute != "href":
            continue

        # skip if not on our domain
        if urlparse(link).netloc != domain and urlparse(link).netloc != "www." + domain:
            continue

        # skip if self referential
        if (url.split("//")[1] + "#") in link:
            continue

        text = element.text_content() if len(element) == 0 else element[0].text_content()
        text = text.lstrip() if text is not None else ""
        # compute relevancy here

        relevance[link] = relevancy(link, text, url)
        urls[link] = 1

        if text != "":
            print text
        print link
        print

    return urls.keys()

def relevancy(link, text, url):
    # compute how relevant these are to the original url
    link_words = re.findall(r"[A-Za-z]+", link)
    url_words = re.findall(r"[A-Za-z]+", url)
    text_words = re.findall(r"[A-Za-z]+", text)

    overlap = 0
    for word in link_words:
        if word in url_words:
            overlap += 1
    for word in text_words:
        if word in url_words:
            overlap += 1    

    return overlap

if __name__ == "__main__":
    main()
