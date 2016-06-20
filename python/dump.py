# -*- coding: utf-8 -*-

import redis
import sys

NEW_WORD_KEY = "NEologd-NE:new-dict"

def dump(host):
    r = redis.StrictRedis(host=host)
    with open("result/dumps.txt", "w") as fd:
        with open('result/dumps_with_link.txt', 'w') as fl:
            for k, v in r.hgetall(NEW_WORD_KEY).items():
                fd.write(k + "\t" + v.split(',')[0] + "\n")
                fl.write(k + "\t" + "\t".join(v.split(',')) + "\n")

if __name__ == '__main__':
    dump(sys.argv[1])