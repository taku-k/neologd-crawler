# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib, urlparse

class CantReadException(Exception):
    pass

class NotAnyFetchException(Exception):
    pass

def url_crawl(url):
    source = ""
    try:
        source = urllib.urlopen(url).read()
    except:
        raise CantReadException()

    soup = BeautifulSoup(source)

    links = []
    try:
        for item in soup.find_all('a'):
            try:
                links.append(urlparse.urljoin(url, urllib.quote(item.get('href'))))
            except:
                pass # Not a valid link
    except:
        raise NotAnyFetchException()

    return links


if __name__ == '__main__':
    # Do test
    pass