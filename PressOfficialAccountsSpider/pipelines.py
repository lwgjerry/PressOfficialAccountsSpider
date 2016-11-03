# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json

class PressPipeline(object):
    # def process_item(self, item, spider):
    #     return item

    def __init__(self):
        self.file = codecs.open('D:/pyCharm/press_spider.json', 'w', encoding='utf-8')

    def process_item(self, items, spider):
        line = json.dumps(dict(items), ensure_ascii=False) + "\n"
        self.file.write(line)
        return items

    def spider_closed(self, spider):
        self.file.close()