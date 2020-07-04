from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from HW_7.my_parser import settings
from HW_7.my_parser.spiders.leroy import LeroySpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroySpider, search=['краска'])

    process.start()
