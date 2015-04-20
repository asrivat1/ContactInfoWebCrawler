#!/usr/bin/env python

import lxml.html
from lxml.html import parse
import sys
from urlparse import urlparse

def main():
    url = sys.argv[1]
    html = parse(url).getroot()
    # make the links absolute for those that are local
    html.make_links_absolute(html.base_url, True)
    # remember the domain
    domain = urlparse(html.base_url).netloc

    # print all links on the page
    for element, attribute, link, pos in html.iterlinks():
        # only print if it's a local link and not self-referential
        link_domain = urlparse(link).netloc
        selfReference = (url + "#") in link
        if link_domain == domain and not selfReference:
            print link

if __name__ == "__main__":
    main()
