# -*- coding: utf-8 -*-
from urlparse import urlparse
from bs4 import BeautifulSoup
import urllib
from crawl import CantReadException

class ExtractFailedException(Exception):
    pass

def what_my_home_net_extractor(soup):
    """For www.what-myhome.net

    :param soup: BeautifulSoup object
    :return: (word, yomi)
    >>> url = "http://www.what-myhome.net/01a/konsento_a.htm"
    >>> soup = BeautifulSoup(urllib.urlopen(url).read())
    >>> what_my_home_net_extractor(soup)
    (u'\u30a2\u30fc\u30b9\u4ed8\u304d\u30b3\u30f3\u30bb\u30f3\u30c8', u'\u30a2\u30fc\u30b9\u3064\u304d\u30b3\u30f3\u30bb\u30f3\u30c8')
    """
    word = soup.find('table', class_='sample1').find_all('tr')[0].find_all('td')[1].string
    yomi = soup.find('table', class_='sample1').find_all('tr')[1].find_all('td')[1].string
    return (word, yomi)


# ======= PATTERN IS HERE =======
HOST_PATTERN = {
    "www.what-myhome.net": what_my_home_net_extractor
}
# ======= PATTERN IS END =======

def selector(url):
    """Select pattern matcher based on specified url

    :param url: str
    :return: (word, yomi)
    >>> selector("http://www.what-myhome.net/01a/konsento_a.htm")
    (u'\u30a2\u30fc\u30b9\u4ed8\u304d\u30b3\u30f3\u30bb\u30f3\u30c8', u'\u30a2\u30fc\u30b9\u3064\u304d\u30b3\u30f3\u30bb\u30f3\u30c8')
    >>> selector("http://example.com")
    Traceback (most recent call last):
        ...
    ExtractFailedException
    """

    try:
        source = urllib.urlopen(url).read()
    except:
        raise CantReadException()
    try:
        host = urlparse(url).hostname
        soup = BeautifulSoup(source)
        for pattern, func in HOST_PATTERN.items():
            if host == pattern:
                return func(soup)
    except:
        raise ExtractFailedException()
    raise ExtractFailedException()

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    