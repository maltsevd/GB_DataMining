from pymongo import MongoClient
import json

# Connecting to database
client = MongoClient('localhost', 27017)
db = client['datamining']
collection = db.headhunter

# Load json file
vacancies = json
with open('hh.json', 'r') as f:
    vacancies = json.load(f)


# Fill database with json values
def fill_db(json_obj):
    collection.insert_many(json_obj)


# Find salary above some value
def find_salary(value, db_obj):
    cursor = db_obj.find({'salary_min': {'$gt': value}})
    for c in cursor:
        print(f'{c["name"]} с зарплатой от {c["salary_min"]} {c["salary_curr"]} {c["vac_url"]}')
    return cursor


find_salary(30000, collection)
