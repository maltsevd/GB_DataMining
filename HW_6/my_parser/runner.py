from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from HW_6.my_parser import settings
from HW_6.my_parser.spiders.labirint import LabirintSpider
from HW_6.my_parser.spiders.book24 import Book24Spider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LabirintSpider)
    process.crawl(Book24Spider)

    process.start()
