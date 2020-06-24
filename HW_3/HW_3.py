from pymongo import MongoClient
import json
from hh_parser.hh_parser import get_vacancies

"""
Код парсера с hh взял из предыдущего ДЗ.
Поскольку _id я генерировал из хэша всех полей, кроме даты обновления,
то уникальность вакансии достаточно проверить только по этому полю.

Для 3го задания использовал следующий метод:
-составил списки всех id из базы и с сайта (результат функции get_vacancies)
-сравнил их и положил в новый список разницу
-на основе новых id создал полноценный список для массового добавления в колекцию
"""

# Connecting to database
client = MongoClient('localhost', 27017)
db = client['datamining']
collection = db.headhunter

# Load json file
vacancies = json
with open('hh.json', 'r') as f:
    vacancies = json.load(f)


# Fill database with json values
def fill_db_json(json_obj, db_obj):
    res = db_obj.insert_many(json_obj)
    print(f'Добавлено {len(res.inserted_ids)} документов')


# Fill database with values from site
def fill_db_site(search_text, db_obj):
    res = db_obj.drop()
    vacancies = get_vacancies(search_text)
    res = db_obj.insert_many(vacancies)
    print(f'Добавлено {len(res.inserted_ids)} документов')


# Find salary above some value, return result as cursor for further manipulations
def find_salary(value, db_obj):
    cursor = db_obj.find({'salary_min': {'$gt': value}})
    for c in cursor:
        print(f'{c["name"]} с зарплатой от {c["salary_min"]} {c["salary_curr"]} {c["vac_url"]}')
    return cursor


# Add new values to database
def update_db(search_text, db_obj):
    vacancies = get_vacancies(search_text)
    vacancy_ids = set([i['_id'] for i in vacancies])
    # Getting ids from database
    find_res = db_obj.find({}, {'_id': 1})
    db_ids = set([i['_id'] for i in find_res])
    # Find difference and add new ids
    ids_to_insert = vacancy_ids.difference(db_ids)
    list_to_insert = []
    if ids_to_insert:
        for item in ids_to_insert:
            list_to_insert.append([i for i in vacancies if i['_id'] == item][0])
        res = db_obj.insert_many(list_to_insert)
        print(f'Добавлено {len(res.inserted_ids)}')
        print(f'id добавленных: {res.inserted_ids}')
    else:
        print('No items to add')


# Testing
list_to_delete = list(collection.aggregate([{'$sample': {'size': 1}}, {'$project': {'_id': 1}}]))
print(f'Будет удален {(list_to_delete[0].get("_id"))}')
results = collection.delete_one({'_id': {'$eq': list_to_delete[0].get('_id')}})
print(f'Удалено элементов {results.deleted_count}')
update_db('Data science', collection)
