from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import selenium.common.exceptions as ex
import datetime
from pprint import pprint
from pymongo import MongoClient

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


# Convert russian month to int and convert 'mail.ru format' to datetime
def convert_datetime(dt_str):
    # print(dt_str)
    for k, v in RU_MONTH_VALUES.items():
        dt_str = dt_str.replace(k, str(v))

    date = dt_str.split(',')[0]
    date_str = date
    date = date.split(' ')
    time = dt_str.split(',')[1].lstrip()
    time = datetime.datetime.strptime(time, '%H:%M').time()
    if len(date) == 1:
        if 'Вчера' in date:
            date = datetime.date.today().replace(day=(datetime.date.today().day - 1))
        else:
            date = datetime.date.today()
    elif len(date) == 2:
        date = datetime.date(datetime.datetime.today().year, int(date[1]), int(date[0]))
    else:
        date = datetime.datetime.strptime(date_str, '%d %m %Y')
    dt_str = datetime.datetime.combine(date, time)
    # print(dt_str)
    return dt_str


def get_links(links_list):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "js-tooltip-direction_letter-bottom")))
    new_list = driver.find_elements_by_class_name('js-tooltip-direction_letter-bottom')
    for element in new_list:
        href = element.get_attribute('href')
        if href not in links_list:
            links_list.append(href)
    actions = ActionChains(driver)
    actions.move_to_element(new_list[-1])
    actions.perform()
    print(len(links_list))
    return links_list


def parse_message(url):
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[contains(@id, "BODY")]')))
    message = dict.fromkeys(['Subject', 'Sender', 'Sender_addr', 'Body', 'Sent_at'])
    message['Subject'] = driver.find_element_by_class_name('thread__subject').text
    sender = driver.find_element_by_class_name('letter-contact')
    message['Sender'] = sender.text
    message['Sender_addr'] = sender.get_attribute('title')
    message['Body'] = driver.find_element_by_xpath('//div[contains(@id, "BODY")]').text
    dt_str = driver.find_element_by_class_name('letter__date').text
    message['Sent_at'] = convert_datetime(dt_str)
    return message


chrome_options = Options()
# chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)
driver.get('https://mail.ru')

# Log in
driver.find_element_by_id('mailbox:login').send_keys('study.ai_172@mail.ru')
driver.find_element_by_xpath('//input[@class="o-control"]').click()
driver.find_element_by_id('mailbox:password').send_keys('NextPassword172')
driver.find_element_by_xpath('//input[@class="o-control"]').click()

# Waiting for elements to load
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "js-tooltip-direction_letter-bottom")))
links = []

# Getting links to messages
while True:
    links = get_links(links)
    try:
        spinner = driver.find_element_by_class_name('list-letter-spinner')
        links = get_links(links)
        break
    except ex.NoSuchElementException:
        pass

result = []
# For test parse every 50th url
for link in links[::50]:
    result.append(parse_message(link))
    print(len(result))

# Filling database
client = MongoClient('localhost', 27017)
db = client['datamining']
collection = db.emails

res = collection.insert_many(result)
print(f'Добавлено {len(res.inserted_ids)}')
