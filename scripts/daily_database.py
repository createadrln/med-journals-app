from datetime import date
import json
import sqlite3
from datetime import datetime
import os

# Combine data files

# Open DOAJ JSON data file
if os.path.exists('/app/raw_data/doaj.json'):
    with open('/app/raw_data/doaj.json', 'r') as json_file:
        doaj_full_data = json.load(json_file)

# Open Europe PMC JSON data file
if os.path.exists('/app/raw_data/europe_pmc.json'):
    with open('/app/raw_data/europe_pmc.json', 'r') as json_file:
        europe_pmc_full_data = json.load(json_file)

# Open Springer JSON data file
if os.path.exists('/app/raw_data/springer.json'):
    with open('/app/raw_data/springer.json', 'r') as json_file:
        springer_full_data = json.load(json_file)

final_doaj_data = []
if os.path.exists('/app/raw_data/doaj.json'):
    for article in doaj_full_data['results']:
        final_data_row = {
            'id': article['id'],
            'source': 'Doaj',
            'date': article['last_updated'],
            'title': article['bibjson']['title'],
            'link': article['bibjson']['link'],
            'authors': article['bibjson']['author'],
            'keywords': article['bibjson'].get('keywords', []),
            'abstract': article['bibjson'].get('abstract', '')
        }
        final_doaj_data.append(final_data_row)

final_europe_pmc_data = []
if os.path.exists('/app/raw_data/europe_pmc.json'):
    for article in europe_pmc_full_data:
        final_data_row = {
            'id': article['id'],
            'source': 'Europe PMC',
            'date': article['firstIndexDate'],
            'title': article['title'],
            'link': f'https://europepmc.org/article/{article["source"]}/{article["id"]}/',
            'authors': article.get('authorString', ''),
            'keywords': None,
            'abstract': None
        }
        final_europe_pmc_data.append(final_data_row)

final_springer_full_data = []
if os.path.exists('/app/raw_data/springer.json'):
    for article in springer_full_data.get('records', []):
        final_data_row = {
            'id': article['identifier'],
            'source': 'Springer',
            'date': article['onlineDate'],
            'title': article['title'],
            'link': article['url'][0],
            'authors': article['creators'],
            'keywords': article['subjects'],
            'abstract': article['abstract']
        }
        final_springer_full_data.append(final_data_row)

today = date.today()

final_all = final_doaj_data + \
    final_europe_pmc_data + final_springer_full_data
with open('/app/raw_data/combined_sources.json', 'w') as json_file:
    json.dump(final_all, json_file, indent=4)

with open(f'/app/raw_data/combined_sources_{today}.json', 'w') as json_file:
    json.dump(final_all, json_file, indent=4)

# Load to Database

conn = sqlite3.connect('/app/databases/CovidData.db')
cursor = conn.cursor()

create_research_table_sql = """
    CREATE TABLE IF NOT EXISTS covid_research (
        id TEXT PRIMARY KEY,
        source TEXT,
        pub_date TEXT,
        pub_timestamp TEXT,
        title TEXT,
        link TEXT,
        authors TEXT,
        authors_affiliations TEXT,
        keywords TEXT
    )
"""

create_keywords_table_sql = """
    CREATE TABLE IF NOT EXISTS covid_research_keywords (
        id TEXT PRIMARY KEY,
        keyword TEXT
    )
"""

create_abstracts_table_sql = """
    CREATE TABLE IF NOT EXISTS covid_research_abstracts (
        id TEXT PRIMARY KEY,
        abstract TEXT
    )
"""

cursor.execute(create_research_table_sql)
cursor.execute(create_keywords_table_sql)
cursor.execute(create_abstracts_table_sql)

list_delimiter = ', '

with open('/app/raw_data/combined_sources.json', 'r') as json_file:
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

cursor.execute(
    """DELETE FROM covid_research_keywords WHERE keyword IN ('Pandemic', 'pandemic', 'COVID-19', 'SARS-CoV-2', 'covid-19', 'Pandemics', '“COVID-19”', 'covid‐19', 'COVID‐19', 'SARS‐CoV‐2', 'SARS-CoV-2 pandemic', 'COVID-19 or SARS-CoV-2', 'pandemie', 'Coronavirus', 'Covid-19', 'Coronavirus disease 2019 (COVID-19)', 'COVID', 'COVID-19 Pandemic', '2021', '2022', ' ', '2019 Coronavirus disease', '2019 novel coronavirus', '2019 novel coronavirus disease', '2019-nCoV', '2019-nCoV disease', '2019nCoV', '2019-nCoV infection', '2019-nCoV disease', 'COVID-19 pandemic', 'COVID-19 disease', 'COVID-19 virus', 'COVID-19 virus infection', 'COVID-19 virus disease', 'COVID-19 virus disease 2019', 'COVID-19 virus infection 2019', '2019 rok', '2023-2024 COVID-19 vaccine', 'COVID-19 pandemic')""")

cursor.execute("DELETE FROM covid_research_abstracts WHERE abstract IS NULL OR TRIM(abstract) = ''")

conn.commit()
conn.close()
