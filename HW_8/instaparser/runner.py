from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from HW_8.instaparser import settings
from HW_8.instaparser.spiders.insta import InstaSpider
from pymongo import MongoClient

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstaSpider)

    process.start()

# Запросы на поиск подписок и подписчиков
    client = MongoClient('localhost', 27017)
    db = client['datamining']
    collection = db['insta']
    followers_query = {'type': 'follower', 'source': 'eidos_wed'}
    following_query = {'type': 'following', 'source': 'eidos_wed'}
    followers = collection.find(followers_query)
    following = collection.find(following_query)
    for f in followers[:5]:
        print(f)
    print(followers.count())
    for f in following[:5]:
        print(f)
    print(following.count())
    client.close()

