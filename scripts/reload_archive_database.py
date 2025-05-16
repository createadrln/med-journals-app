from datetime import date
import json
import sqlite3
from datetime import datetime
import os

# Load to Database

conn = sqlite3.connect('/app/databases/CovidData.db')
cursor = conn.cursor()

list_delimiter = ', '

for filename in os.listdir('/app/raw_data/archive'):
    if filename.endswith('.json') and 'combined' in filename:
        with open(os.path.join('/app/raw_data/archive', filename), 'r') as json_file:

            data = json.load(json_file)
            for item in data:
                if item['source'] == 'Europe PMC':
                    datetime_object = datetime.strptime(
                        item['date'], '%Y-%m-%d')
                    datetime_timestamp = datetime.timestamp(datetime_object)

                    cursor.execute("INSERT OR IGNORE INTO covid_research VALUES(?,?,?,?,?,?,?,?,?)", (
                        item['id'],
                        item['source'],
                        str(datetime_object),
                        str(datetime_timestamp),
                        item['title'],
                        item['link'],
                        item['authors'],
                        None,
                        None,
                    ))

                if item['source'] == 'Doaj':
                    datetime_object = datetime.strptime(
                        item['date'], '%Y-%m-%dT%H:%M:%SZ')
                    datetime_timestamp = datetime.timestamp(datetime_object)

                    authors_list = []
                    author_affiliations_list = []
                    for author in item['authors']:
                        authors_list.append(author.get('name', ""))
                        author_affiliations_list.append(author.get('affiliation', ""))

                    keywords_list = []
                    for keyword in item['keywords']:
                        keywords_list.append(keyword)
                        cursor.execute(
                            "INSERT OR IGNORE INTO covid_research_keywords VALUES(?,?)", (item['id'], keyword))

                    cursor.execute("INSERT OR IGNORE INTO covid_research VALUES(?,?,?,?,?,?,?,?,?)", (
                        item['id'],
                        item['source'],
                        str(datetime_object),
                        str(datetime_timestamp),
                        item['title'],
                        list_delimiter.join([link['url'] for link in item['link']]),
                        list_delimiter.join(authors_list),
                        list_delimiter.join(author_affiliations_list),
                        list_delimiter.join(keywords_list),
                    ))

                    cursor.execute("INSERT OR IGNORE INTO covid_research_abstracts VALUES(?,?)", (
                        item['id'],
                        item['abstract'],
                    ))

                if item['source'] == 'Springer':
                    datetime_object = datetime.strptime(
                        item['date'], '%Y-%m-%d')
                    datetime_timestamp = datetime.timestamp(datetime_object)

                    keywords_list = []
                    for keyword in item.get('keywords', []):
                        keywords_list.append(keyword)
                    for keyword in keywords_list:
                        cursor.execute(
                            "INSERT OR IGNORE INTO covid_research_keywords VALUES(?,?)", (item['id'], keyword))

                    authors_list = []
                    for author in item['authors']:
                        authors_list.append(author.get('creator', ""))

                    cursor.execute("INSERT OR IGNORE INTO covid_research VALUES(?,?,?,?,?,?,?,?,?)", (
                        item['id'],
                        item['source'],
                        str(datetime_object),
                        str(datetime_timestamp),
                        item['title'],
                        item['link']['value'],
                        list_delimiter.join(authors_list),
                        None,
                        list_delimiter.join(item['keywords']),
                    ))

                    cursor.execute("INSERT OR IGNORE INTO covid_research_abstracts VALUES(?,?)", (
                        item['id'],
                        item['abstract']['p'][0] if isinstance(
                            item['abstract']['p'], list) else item['abstract']['p']
                    ))

conn.commit()
conn.close()
