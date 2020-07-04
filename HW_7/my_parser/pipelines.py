# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient


class MongoPipeline:
    def __init__(self):
        self.mongo_uri = 'localhost'
        self.mongo_db = 'datamining'

    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_uri, 27017)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[spider.name].insert_one(item)
        return item


class LeroyPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
               try:
                   yield scrapy.Request(img, meta=item)
               except Exception as e:
                   print(e)
        return item

    def file_path(self, request, response=None, info=None):
        item = request.meta
        name = request.url.split('/')
        path = f'./{item.get("name")}/{name[-1]}'
        return path

    def item_completed(self, results, item, info):
        if results:
            return item




