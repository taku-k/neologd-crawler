neologd-crawler
===============

This crawler collects Japanese word and 仮名 (kana) and
stores to Redis.  
Each executor of this scheduler runs on Apache Mesos,
so we can scale up them. 

## Description

This scheduler consists of two executor, the one is
a crawler that identifies all the hyperlinks in the page and
transimits them to the Redis,
the other one is a extractor that checks the given URL
 for the presence of prepared matching functions (for now,
mathing functions are hard-coded in Python file).  
Redis manages collected words and visited URL.

## Requirement

* Apache Mesos 0.22.0
* Scala 2.11
* sbt 0.13.7
* Python 2.7
    * bs4
    * redis

## Usage

We need to prepare `neologd-crawler/src/main/resources/application.conf`.  
`application.conf` is like as follows.

```
taku_k {
  home = "/home/vagrant/hostfiles/neologd-crawler"
  mesos {
    master = "127.0.1.1:5050"
  }
  redis {
    host = "localhost"
    port = "6379"
  }
}
```

Now we can run a crawler the following command:

```
$ sbt "run http://<seed-URL>"
```

If you don't need to obtain words which already have been recorded
 in the [mecab-ipadic-NEologd](https://github.com/neologd/mecab-ipadic-neologd)
 , you must add words list to redis.  
We prepare utility script.

```
$ ./bin/setup.sh
$ ./python/utils.py
```

## Author

[taku-k](https://github.com/taku-k)