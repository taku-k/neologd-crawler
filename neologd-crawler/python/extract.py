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


def ff11_wiki_extractor(soup):
    """For wiki.ffo.jp

    :param soup: BeatutifulSoup object
    :return: list of (word, yomi)
    >>> url = 'http://wiki.ffo.jp/html/22326.html'
    >>> soup = BeautifulSoup(urllib.urlopen(url).read())
    >>> ff11_wiki_extractor(soup)
    [(u'\u30a2\u30a4\u30e9\u30d0\u30b0\u30ca\u30a6', u'\u3042\u3044\u3089\u3070\u3050\u306a\u3046')]
    """
    word = soup.find('div', class_='title').text.split('(')[0]
    yomi = soup.find('span', class_='yomi').string[1:-1].split('/')[0]
    return [(word, yomi)]


def aozora_extractor(soup):
    """
    :param soup:
    :return: list of (word, yomi)
    """
    if not soup.find('table', summary='タイトルデータ'):
        word = soup.find('table', summary='作家データ').find_all('td')[1].string
        yomi = soup.find('table', summary='作家データ').find_all('td')[3].string
    else:
        word = soup.find('table', summary='タイトルデータ').find_all('td')[1].string
        yomi = soup.find('table', summary='タイトルデータ').find_all('td')[3].string
    return [(word, yomi)]

def honndana_extractor(soup):
    pass

def myoujijiten_extractor(soup):
    """

    :param soup:
    :return:
    >>> url = 'http://myoujijiten.web.fc2.com/hiroshima.htm'
    >>> soup = BeautifulSoup(urllib.urlopen(url).read())
    >>> myoujijiten_extractor(soup)
    Traceback (most recent call last):
        ...
    ExtractFailedException
    >>> url = "http://myoujijiten.web.fc2.com/a1.html"
    >>> soup = BeautifulSoup(urllib.urlopen(url).read())
    >>> myoujijiten_extractor(soup)

    """
    centers = soup.find_all('center')[2].find_all('tr')
    if len(centers[0].find_all('td')) != 5:
        raise ExtractFailedException()
    return [(tr.find_all('td')[1].string, tr.find_all('td')[0].string) for tr in centers]

# ======= PATTERN IS HERE =======
HOST_PATTERN = {
    "www.what-myhome.net": what_my_home_net_extractor,
    "wiki.ffo.jp": ff11_wiki_extractor,
    "www.aozora.gr.jp": aozora_extractor,
    "ff14.ffo.jp": ff11_wiki_extractor,
    "honndana.sakura.ne.jp": honndana_extractor,
    "myoujijiten.web.fc2.com": myoujijiten_extractor
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
    