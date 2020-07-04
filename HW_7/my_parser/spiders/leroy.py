import scrapy
from scrapy.http import HtmlResponse
from HW_7.my_parser.items import LeroyItem
from scrapy.loader import ItemLoader


class LeroySpider(scrapy.Spider):
    name = 'leroy'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search):
        self.start_urls = [f'https://spb.leroymerlin.ru/search/?q={search[0]}']

    def parse(self, response):
        next_page = response.xpath('//div[@class="service-panel clearfix"]//a[@class="paginator-button next-paginator-button"]/@href').extract_first()
        goods_links = response.xpath('//div[@class="product-name"]/a')
        for link in goods_links:
            yield response.follow(link, callback=self.parse_goods)
        yield response.follow(next_page, callback=self.parse)

    def parse_goods(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroyItem(), response=response)
        loader.add_xpath('name', '//h1[@class="header-2"]/text()')
        loader.add_xpath('photos', '//uc-pdp-media-carousel//img[@slot="thumbs"]/@src')
        loader.add_xpath('params', '//dl[@class="def-list"]/div')
        loader.add_value('url', response.url)
        loader.add_xpath('price', '//span[@slot="price"]/text()')
        yield loader.load_item()
