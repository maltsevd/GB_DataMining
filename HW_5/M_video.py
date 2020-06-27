from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import json
from pymongo import MongoClient
import pymongo

chrome_options = Options()
chrome_options.add_argument("--start-maximized")
# chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)
driver.get('https://www.mvideo.ru/')

# Wait for element
WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="carousel-paging"]/a')))
elements = driver.find_elements_by_xpath('//div[@data-init="ajax-category-carousel"]')
# Select hits carousel
hits = elements[1]
carousel = hits.find_element_by_class_name('carousel-paging')
# Search carousel buttons
btns = carousel.find_elements_by_tag_name('a')

# click() wont work, executing script
driver.execute_script("$(arguments[0]).click();", btns[-1])

# Waiting for elements to be loaded
# commented code below works from time to time, very unstable :(
# WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.XPATH, './/li[@rel="15"]')))
time.sleep(5)
items = hits.find_elements_by_xpath('.//li[@class="gallery-list-item height-ready"]')

# Parsing items
result = []
for i in items:
    product = dict.fromkeys(['name', 'prod_id', 'category', 'vendor', 'price', 'url'])
    a = i.find_element_by_tag_name('a')
    a_dict = json.loads(a.get_attribute('data-product-info'))
    product['url'] = a.get_attribute('href')
    product['name'] = a_dict.get('productName')
    product['prod_id'] = int(a_dict.get('productId'))
    product['category'] = a_dict.get('productCategoryName')
    product['vendor'] = a_dict.get('productVendorName')
    product['price'] = float(a_dict.get("productPriceLocal"))
    result.append(product)

driver.close()

# Filling database
client = MongoClient('localhost', 27017)
db = client['datamining']
collection = db.mvideo
collection.drop()
res = collection.insert_many(result)
print(f'Добавлено {len(res.inserted_ids)} товаров')
client.close()
