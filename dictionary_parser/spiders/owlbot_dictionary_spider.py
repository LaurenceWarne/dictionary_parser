# -*- coding: utf-8 -*-
import json
import re

import scrapy


class OwlbotDictionarySpider(scrapy.Spider):

    name = 'owlbot_dictionary_spider'
    api_url = "https://owlbot.info/api/v2/dictionary/"
    # slice to obtain the word from the response url
    word_slice = slice(len(api_url), -len("?format=json") - 3)
    allowed_domains = ['owlbot.info']
    # regex to remove tags which are in the text body for some reason.
    regex = re.compile("<.*?>")

    def __init__(self, wordfile=None, verbose=True):

        self.wordfile = wordfile
        if (self.wordfile is None):
            raise ValueError("Input file of words must be passed!")
        self.verbose = verbose

    def start_requests(self):

        with open(self.wordfile, mode="r") as f:
            words = f.readlines()
        for word in words:
            yield scrapy.Request(
                self.api_url + word + "?format=json", self.parse
            )

    def parse(self, response):

        data_dictionary = json.loads(response.text)
        word = response.url[self.word_slice]
        # Iterate over defintions of the word
        if (data_dictionary == []):
            if (self.verbose):
                self.logger.error("No defintions found for: " + word)
            return
        for diff_defintion in data_dictionary:
            # Iterate over information about a particular defintion
            for key, val in diff_defintion.items():
                try:
                    new_val = self.regex.sub("", val)
                except TypeError:  # null, e.g. no example given
                    # We'll log these in the pipeline
                    pass
                else:
                    diff_defintion[key] = new_val
            diff_defintion["word"] = word
            yield diff_defintion
