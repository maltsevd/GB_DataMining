# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class MyParserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_db = client.datamining
        self.mongo_db.book24.drop()
        self.mongo_db.labirint.drop()

    def process_item(self, item, spider):
        if spider.name == 'book24':
            item['price'] = float(item.get('price').replace(' ', '').replace('р.', ''))
            if item.get('discount_price') != 'None':
                item['discount_price'] = float(item.get('discount_price').replace(' ', '').replace('р.', ''))
            if item['rating']:
                for r in item['rating']:
                    item['rating'][item['rating'].index(r)] = float(r.replace(',', '.'))

        if spider.name == 'labirint':
            if item['discount_price']:
                item['discount_price'] = float(item['discount_price'])
            item['price'] = float(item['price'])
            if item['rating']:
                item['rating'] = float(item['rating'])
        collection = self.mongo_db[spider.name]
        collection.insert_one(item)
        return item
