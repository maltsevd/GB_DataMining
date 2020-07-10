# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from HW_8.instaparser.items import InstaparserItem
import scrapy
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


class InstaPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['user_photo']:
            try:
                yield scrapy.Request(item['user_photo'], meta=item)
            except Exception as e:
                print(e)
        return item

    def file_path(self, request, response=None, info=None):
            item = request.meta
            name = request.url.split('/')
            path = f'./{item.get("source")}/{item.get("type")}/{item.get("user_name")}.jpg'
            return path
    def item_completed(self, results, item, info):
        if results:
            return item
