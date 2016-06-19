# -*- coding: utf-8 -*-
import json

class Result(object):
    def __repr__(self):
        return json.dumps(self.__dict__, sort_keys=True)


class UrlCrawlResult(Result):
    """The result of mining a resource for links

    UrlCrawlResult must serialize to JSON as its default representation:

    >>> res = UrlCrawlResult(
    ...     "1234",
    ...     "http://example.com",
    ...     ["http://example.com/a", "http://example.com/b"]
    ... )
    >>> repr(res)
    '{"links": ["http://example.com/a", "http://example.com/b"], "taskId": "1234", "url": "http://example.com"}'
    """
    def __init__(self, taskId, url, links):
        self.taskId = taskId
        self.url = url
        self.links = links


class ExtractResult(Result):
    u"""The result of extracting from URL

    ExtractResult must serialize to JSON as its default representation:

    >>> res = ExtractResult(
    ...     "1234",
    ...     "http://example.com",
    ...     [{"word": '債権者集会',
    ...       "yomi": 'さいけんしゃしゅうかい'}]
    ... )
    >>> repr(res)
    '{"new_words": [{"word": "\\\\u50b5\\\\u6a29\\\\u8005\\\\u96c6\\\\u4f1a", "yomi": "\\\\u3055\\\\u3044\\\\u3051\\\\u3093\\\\u3057\\\\u3083\\\\u3057\\\\u3085\\\\u3046\\\\u304b\\\\u3044"}], "taskId": "1234", "url": "http://example.com"}'
    """
    def __init__(self, taskId, url, new_words):
        self.taskId = taskId
        self.url = url
        self.new_words = new_words

if __name__ == '__main__':
    import doctest
    doctest.testmod()
