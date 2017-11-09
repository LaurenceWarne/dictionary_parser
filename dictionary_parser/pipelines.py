# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import sqlite3

from scrapy.exceptions import DropItem


class OwlbotDictionaryJlinesPipeline():

    def open_spider(self, spider):

        self.file = open("dict.jl", "w")

    def close_spider(self, spider):

        self.file.close()

    def process_item(self, item, spider):

        line = json.dumps(item) + "\n"
        self.file.write(line)
        return item


class OwlbotDictionaryDatabasePipeline(object):

    def __init__(self, database_name="owlbot_dictionary.db"):

        self.conn = None
        self.cursor = None
        self.database_name = database_name

    def open_spider(self, spider):

        self.conn = sqlite3.connect(self.database_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
        CREATE TABLE words(
        word text PRIMARY KEY
        )''')
        self.cursor.execute('''
        CREATE TABLE definitions(
        word text,
        type text,
        definition text,
        PRIMARY KEY(word, definition),
        FOREIGN KEY(word) REFERENCES words(word)
        )''')
        self.cursor.execute('''
        CREATE TABLE examples(
        word text,
        definition text,
        example text,
        PRIMARY KEY(word, definition, example),
        FOREIGN KEY(word) REFERENCES words(word),
        FOREIGN KEY(definition) REFERENCES definitions(definition)
        )''')

    def close_spider(self, spider):

        self.conn.commit()
        self.conn.close()

    def process_item(self, item, spider):

        if (item['word'] is None):
            raise DropItem('Dictionary entry missing name')
        elif (item['definition'] is None):
            raise DropItem(
                'Dictionary entry ' + item['word'] + ' is missing a definition'
            )
        elif (item['type'] is None):
            raise DropItem(
                'Dictionary entry ' + item['word'] + ' is missing a word-type'
            )

        
        self.cursor.execute(
            'SELECT word FROM words WHERE word=?', (item['word'],)
        )
        if (self.cursor.fetchall() == []):
            self.cursor.execute(
                '''INSERT INTO words VALUES(?)''', (item["word"],)
            )

        
        self.cursor.execute(
            '''INSERT INTO definitions VALUES(?, ?, ?)''',
            (item['word'], item['type'], item['definition'])
        )
        if (not item['example'] is None):
            self.cursor.execute(
                '''INSERT INTO examples VALUES(?, ?, ?)''',
                (item['word'], item['definition'], item['example'])
            )
        return item
