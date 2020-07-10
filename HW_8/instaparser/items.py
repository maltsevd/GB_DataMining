# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst


class InstaparserItem(scrapy.Item):
    _id = scrapy.Field()
    user_id = scrapy.Field(output_processor=TakeFirst())
    user_name = scrapy.Field(output_processor=TakeFirst())
    full_name = scrapy.Field(output_processor=TakeFirst())
    user_photo = scrapy.Field(output_processor=TakeFirst())
    source = scrapy.Field(output_processor=TakeFirst())
    type = scrapy.Field(output_processor=TakeFirst())
