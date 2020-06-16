from bs4 import BeautifulSoup
import requests
from pprint import pprint
import hashlib
import json

main_link = 'https://spb.hh.ru'
search_link ='/search/vacancy'


# Find next page if exists
def get_next_url(soup):
    try:
        next_url = soup.find('a', attrs={'data-qa': 'pager-next'})['href']
    except TypeError:
        next_url = None
    return next_url


# Get salary min, max, curr
def parse_salary(bs_obj):
    salary_dict = dict.fromkeys(['salary_min', 'salary_max', 'salary_curr'])
    salary = bs_obj.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
    if salary:
        salary = str(salary.contents[0])
        salary_elements = salary.split(' ')
        if '-' in salary_elements[0]:
            minmax = salary_elements[0].split('-')
            salary_dict['salary_min'] = int(minmax[0].replace(u'\xa0', ''))
            salary_dict['salary_max'] = int(minmax[1].replace(u'\xa0', ''))
        if 'от' in salary_elements:
            salary_dict['salary_min'] = salary_elements[1].replace(u'\xa0', '')
        if 'до' in salary_elements:
            salary_dict['salary_max'] = salary_elements[1].replace(u'\xa0', '')
        salary_dict['salary_curr'] = salary_elements[-1]
    else:
        salary_dict = None
    return salary_dict


def fill_vacancies_dict(vacancies):
    result = set()
    for var in vacancies:
        vacancy = dict.fromkeys(['_id', 'name', 'salary_min', 'salary_max', 'salary_curr',
                        'vac_url', 'employer', 'employer_url', 'employer_addr'])
        salary = parse_salary(var)
        title = var.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})
        employer = var.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'})
        employer_addr = var.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-address'})
        metro_station = var.find('span', attrs={'class': 'metro-station'})
        vacancy['name'] = title.contents[0]
        if salary:
            vacancy['salary_min'] = salary['salary_min']
            vacancy['salary_max'] = salary['salary_max']
            vacancy['salary_curr'] = salary['salary_curr']
        vacancy['vac_url'] = title['href']
        if employer:
            vacancy['employer'] = employer.contents[0]
            vacancy['employer_url'] = main_link + employer['href']
        else:
            vacancy['employer'] = var.find('div', attrs={'class': 'vacancy-serp-item__meta-info'}).contents[0].replace(u'\xa0', '')
        if employer_addr:
            if metro_station:
                vacancy['employer_addr'] = employer_addr.contents[0] + metro_station.contents[1]
            else:
                vacancy['employer_addr'] = employer_addr.contents[0]
        str_for_hash = str(result).encode('utf-8')
        vacancy['_id'] = hashlib.md5(str_for_hash).hexdigest()
        result.add(vacancy)
    return result


# Getting request
text = 'Data science'
params = {'area': 2, 'st': 'searchVacancy', 'text': text, 'fromSearch': 'true', 'from': 'suggest_post'}
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}
response = requests.get(main_link + search_link, params=params, headers=headers)
soup = BeautifulSoup(response.text, 'lxml')
next_url = get_next_url(soup)
vacancies = soup.find_all('div', attrs={'class': 'vacancy-serp-item'})

while next_url:
    response = requests.get(main_link + next_url, params=params, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    divs = soup.find_all('div', attrs={'class': 'vacancy-serp-item'})
    for div in divs:
        vacancies.append(div)
    try:
        next_url = get_next_url(soup)
    except TypeError:
        next_url = None

# Put response variables in result dict
result = dict.fromkeys(['_id', 'name', 'salary_min', 'salary_max', 'salary_curr',
                        'vac_url', 'employer', 'employer_url', 'employer_addr'])

result = fill_vacancies_dict(vacancies)
pprint(result)

# Save to JSON
with open('hh.json', 'w') as f:
    json.dump(result[0], f)


