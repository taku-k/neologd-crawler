# -*- coding: utf-8 -*-

import redis
import sys

NEW_WORD_KEY = "NEologd-NE:new-dict"

def dump(host):
    r = redis.StrictRedis(host=host)
    with open("dumps", "w") as f:
        for k, v in r.hgetall(NEW_WORD_KEY).items():
            f.write(k + "," + v + "\n")

if __name__ == '__main__':
    dump(sys.argv[1])