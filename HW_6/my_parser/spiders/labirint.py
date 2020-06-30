import scrapy
from HW_6.my_parser.items import MyParserItem
from scrapy.http import HtmlResponse


class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/search/%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5/?stype=0']

    def parse(self, response: HtmlResponse):
        next_page = response.css('a.pagination-next__text::attr(href)').extract_first()
        book_links = response.css('a.product-title-link::attr(href)').extract()

        for link in book_links:
            yield response.follow(link, callback=self.book_parse)

        yield response.follow(next_page, callback=self.parse)

    def book_parse(self, response: HtmlResponse):
        book_url = response.url
        book_name = response.xpath('//div[@id="product-info"]/@data-name').extract_first()
        book_authors = response.xpath('//a[@data-event-label="author"]/text()').extract()
        book_price = response.xpath('//div[@id="product-info"]/@data-price').extract_first()
        book_disc_price = response.xpath('//div[@id="product-info"]/@data-discount-price').extract_first()
        book_rating = response.xpath('//div[@id="rate"]/text()').extract_first()
        yield MyParserItem(url=book_url, name=book_name, authors=book_authors, price=book_price,
                           discount_price=book_disc_price, rating=book_rating)

