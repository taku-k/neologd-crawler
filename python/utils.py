import csv
import sys
import os
import glob
import codecs
from IPython import embed
import redis


SEED_FILES = glob.glob(os.path.dirname(os.path.abspath(__file__)) + '/../mecab-ipadic-neologd/seed/*.csv')
HASH_KEY = "NEologd-NE:dict"

def ipa_iter():
    """
    Generator of words which are included in NEologd.
    :return: yield word
    """
    for csvfile_path in SEED_FILES:
        # print("Start csv file: {path}".format(path=csvfile_path))
        with codecs.open(csvfile_path, 'rU', 'utf-8') as csvfile:
            for words in csvfile:
                splited = words.strip().split(",")
                yield (splited[0], splited[-1])

def get_ipa_dict():
    dic = dict()
    for w in ipa_iter():
        dic[w[0]] = w[1]
    return dic

def store_to_redis():
    r = redis.StrictRedis(host='localhost', port=6379)
    for item in ipa_iter():
        r.hset(HASH_KEY, item[0], item[1])
    print("Added {} items".format(r.hlen(HASH_KEY)))

if __name__ == '__main__':
    # words = get_ipa_dict()
    store_to_redis()
    embed()
