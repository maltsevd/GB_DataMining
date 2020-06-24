from lxml import html
import requests
import json
import datetime
from pprint import pprint
from pymongo import MongoClient

# Connecting to database
client = MongoClient('localhost', 27017)
db = client['datamining']
collection = db.newsfeed

RU_MONTH_VALUES = {
    'января': 1,
    'февраля': 2,
    'марта': 3,
    'апреля': 4,
    'мая': 5,
    'июня': 6,
    'июля': 7,
    'августа': 8,
    'сентября': 9,
    'октября': 10,
    'ноября': 11,
    'декабря': 12,
}

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}
result = []

# Convert russian month to int
def int_value_from_ru_month(date_str):
    for k, v in RU_MONTH_VALUES.items():
        date_str = date_str.replace(k, str(v))
        date_str = date_str.lstrip()
    return date_str


def get_dom(url):
    page = requests.get(url, headers=headers)
    dom = html.fromstring(page.text)
    return dom


def get_from_mailru(result):
    link = 'https://news.mail.ru'
    dom = get_dom(link)
    pages = dom.xpath('//div[contains(@class, "daynews__item")]/a[@href]')
    for page in pages:
        topic = dict.fromkeys(['Publisher', 'Title', 'URL', 'Published_at'])
        ref = page.attrib['href']
        if ref.startswith('/'):
            url = link + ref
        else:
            url = ref
        page_dom = get_dom(url)
        topic['Publisher'] = page_dom.xpath('//a[@class="link color_gray breadcrumbs__link"]/span')[0].text
        topic['Title'] = page_dom.xpath('//h1[@class="hdr__inner"]')[0].text
        topic['URL'] = url
        dt = page_dom.xpath('//span[@class="note__text breadcrumbs__text js-ago"]')[0].attrib['datetime']
        dt = dt.split('+')[0]
        dt = datetime.datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S')
        topic['Published_at'] = str(dt)
        result.append(topic)
    return result


def get_from_lenta(result):
    link = 'https://lenta.ru'
    dom = get_dom(link)
    pages = dom.xpath('//section[@class="row b-top7-for-main js-top-seven"]//div[contains(@class, "item")]')
    for page in pages:
        topic = dict.fromkeys(['Publisher', 'Title', 'URL', 'Published_at'])
        obj = page.xpath('.//time')[0]
        topic['Publisher'] = 'Lenta.ru'
        topic['Title'] = obj.xpath('../text()')[0].replace(u'\xa0', ' ')
        topic['URL'] = link + obj.xpath('../@href')[0]
        dt = obj.attrib['datetime']
        dt = int_value_from_ru_month(dt)
        dt = datetime.datetime.strptime(dt, '%H:%M, %d %m %Y')
        topic['Published_at'] = str(dt)
        result.append(topic)
    return result


def get_from_yandex(result):
    link = 'https://yandex.ru/news'
    dom = get_dom(link)
    pages = dom.xpath('//div[@class="story__topic"]')
    # Get first 10 news
    for page in pages[:10]:
        topic = dict.fromkeys(['Publisher', 'Title', 'URL', 'Published_at'])
        topic['Title'] = page.xpath('.//h2[@class="story__title"]/a/text()')[0]
        topic['URL'] = link + page.xpath('.//h2[@class="story__title"]/a/@href')[0]
        dt_str = page.xpath('..//div[@class="story__date"]/text()')[0]
        info = dt_str.split()
        date = datetime.date.today()
        time = datetime.datetime.strptime(info[-1], '%H:%M').time()
        src = ' '
        if 'вчера' in info:
            ind = info.index('вчера')
            src = ' '
            src = src.join(info[:ind])
            date = datetime.date.today().replace(day=(datetime.date.today().day-1))
        else:
            src = ' '
            src = src.join(info[:-1])
        topic['Publisher'] = src
        dt = datetime.datetime.combine(date, time)
        topic['Published_at'] = str(dt)
        result.append(topic)
    return result

def fill_db(result, db_obj):
    res = db_obj.insert_many(result)
    print(f'Добавлено {len(res.inserted_ids)} документов')

get_from_lenta(result)
get_from_mailru(result)
get_from_yandex(result)


fill_db(result, collection)



