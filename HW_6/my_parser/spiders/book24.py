import scrapy
from scrapy.http import HtmlResponse
from HW_6.my_parser.items import MyParserItem


class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/search/?q=%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//a[@class="catalog-pagination__item _text js-pagination-catalog-item"]/@href').extract()
        if len(next_page) > 1:
            next_page = next_page[-1]
        else:
            next_page = next_page[0]
        book_links = response.xpath('//a[@class="book__title-link js-item-element ddl_product_link "]/@href').extract()

        for link in book_links:
            yield response.follow(link, callback=self.book_parse)

        yield response.follow(next_page, callback=self.parse)

    def book_parse(self, response: HtmlResponse):
        book_url = response.url
        book_name = response.xpath('//h1[@class="item-detail__title"]/text()').extract_first()
        book_authors = response.xpath('///a[@class="item-tab__chars-link js-data-link"]/text()').extract()
        book_prices = response.xpath('//div[@class="item-actions__prices"]/div/@class').extract()
        if 'item-actions__price-old' in book_prices:
            book_price = response.xpath('//div[@class="item-actions__price-old"]/text()').extract_first()
            book_disc_price = response.xpath('//div[@class="item-actions__price"]/b/text()').extract_first()
        else:
            book_price = response.xpath('//div[@class="item-actions__price"]/b/text()').extract_first()
            book_disc_price = 'None'
        book_ratings = response.xpath('//div[@class="item-detail__informations"]//span[contains(@class, "rate-value")]/text()').extract()
        yield MyParserItem(url=book_url, name=book_name, authors=book_authors, price=book_price,
                           discount_price=book_disc_price, rating=book_ratings)
