# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst
from lxml import html


def cleaner_photo(value):
    value = value.split('/')
    value.pop(value.index('upload')+1)
    link = '/'.join(value)
    return link


def get_params(values):
    res = {}
    for val in values:
        dom = html.fromstring(val)
        key = dom.xpath('//dt/text()')[0].replace('\n', '')
        value = dom.xpath('//dd/text()')[0].split('\n')[1].lstrip()
        try:
            value = float(value)
        except:
            pass
        res[key] = value
    return res


def to_float(value):
    if value:
        try:
            value = float(value[0].replace(' ',''))
        except Exception as e:
            print(e)
    return value


class LeroyItem(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(cleaner_photo))
    params = scrapy.Field(input_processor=get_params, output_processor=TakeFirst())
    price = scrapy.Field(input_processor=to_float, output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
