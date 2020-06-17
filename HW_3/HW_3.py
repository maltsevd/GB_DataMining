from pymongo import MongoClient
import json
from hh_parser.hh_parser import get_vacancies

# Connecting to database
client = MongoClient('localhost', 27017)
db = client['datamining']
collection = db.headhunter

# Load json file
vacancies = json
with open('hh.json', 'r') as f:
    vacancies = json.load(f)


# Fill database with json values
def fill_db_json(json_obj):
    collection.insert_many(json_obj)


# Find salary above some value
def find_salary(value, db_obj):
    cursor = db_obj.find({'salary_min': {'$gt': value}})
    for c in cursor:
        print(f'{c["name"]} с зарплатой от {c["salary_min"]} {c["salary_curr"]} {c["vac_url"]}')
    return cursor


def fill_db_site():
    vacancies = get_vacancies('Data science')
    x = collection.update_many({}, {'$set': vacancies})
    print(x)
# find_salary(30000, collection)


fill_db_site()