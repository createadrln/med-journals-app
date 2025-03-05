import json
import csv
import sqlite3
from datetime import datetime
import os

# Combine data files

# Open Pubmed JSON data file
if os.path.exists('../raw_data/pubmed_full.json'):
    with open('../raw_data/pubmed_full.json', 'r') as json_file:
        pubmed_full_data = json.load(json_file)

# Open DOAJ JSON data file
if os.path.exists('../raw_data/doaj.json'):
    with open('../raw_data/doaj.json', 'r') as json_file:
        doaj_full_data = json.load(json_file)

# Open Europe PMC JSON data file
if os.path.exists('../raw_data/europe_pmc.json'):
    with open('../raw_data/europe_pmc.json', 'r') as json_file:
        europe_pmc_full_data = json.load(json_file)

final_pubmed_data = []
if os.path.exists('../raw_data/pubmed_full.json'):
    for article in pubmed_full_data['PubmedArticleSet']['PubmedArticle']:
        final_data_row = {
            'id': article['MedlineCitation']['PMID']['#text'],
            'source': 'PubMed',
            'date': article['MedlineCitation']['DateRevised'],
            'title': article['MedlineCitation']['Article']['ArticleTitle'],
            'link': f'https://pubmed.ncbi.nlm.nih.gov/{article["MedlineCitation"]["PMID"]["#text"]}/',
            'authors': article['MedlineCitation']['Article'].get('AuthorList', {}).get('Author', []),
            'keywords': article['MedlineCitation'].get('KeywordList', {}).get('Keyword', []),
            'abstract': article['MedlineCitation'].get('Abstract', {}).get('AbstractText', [])
        }
        final_pubmed_data.append(final_data_row)

final_doaj_data = []
if os.path.exists('../raw_data/doaj.json'):
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
if os.path.exists('../raw_data/europe_pmc.json'):
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

from datetime import date
today = date.today()

final_all = final_doaj_data + final_pubmed_data + final_europe_pmc_data
with open('../raw_data/combined_sources.json', 'w') as json_file:
    json.dump(final_all, json_file, indent=4)

with open(f'../raw_data/combined_sources_{today}.json', 'w') as json_file:
    json.dump(final_all, json_file, indent=4)

# Load to Database

conn = sqlite3.connect('./databases/CovidData.db')
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

with open('../raw_data/combined_sources.json', 'r') as json_file:
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

        if item['source'] == 'PubMed':
            formatted_date_str = f"{item['date']['Year']}-{item['date']['Month']}-{item['date']['Day']}"
            datetime_object = datetime.strptime(formatted_date_str, '%Y-%m-%d')
            datetime_timestamp = datetime.timestamp(datetime_object)

            authors_list = []
            affiliations = []
            if isinstance(item['authors'], list):
                for author in item['authors']:
                    if author.get('AffiliationInfo'):
                        if isinstance(author['AffiliationInfo'], list):
                            for affiliation in author.get('AffiliationInfo', []):
                                affiliations.append(
                                    affiliation.get('Affiliation', ''))
                        elif isinstance(author['AffiliationInfo'], dict):
                            affiliations.append(author.get(
                                'AffiliationInfo', {}).get('Affiliation', ''))
                    authors_list.append(
                        f"{author.get('ForeName', '')} {author.get('LastName', '')}")

            keywords_list = []
            if isinstance(item['keywords'], dict):
                keywords_list.append(item['keywords']['#text'])
            else:
                for keyword in item.get('keywords', []):
                    keywords_list.append(keyword['#text'])

            for keyword in keywords_list:
                cursor.execute(
                    "INSERT OR IGNORE INTO covid_research_keywords VALUES(?,?)", (item['id'], keyword))

            title = item['title']
            if isinstance(item['title'], dict):
                title = item['title']['#text']

            cursor.execute("INSERT OR IGNORE INTO covid_research VALUES(?,?,?,?,?,?,?,?,?)", (
                item['id'],
                item['source'],
                str(datetime_object),
                str(datetime_timestamp),
                title,
                item['link'],
                list_delimiter.join(authors_list),
                list_delimiter.join(affiliations),
                list_delimiter.join(keywords_list),
            ))

            cursor.execute("INSERT OR IGNORE INTO covid_research_abstracts VALUES(?,?)", (
                item['id'],
                list_delimiter.join(item['abstract']),
            ))

cursor.execute(
    """DELETE FROM covid_research_keywords WHERE keyword IN ('Pandemic', 'pandemic', 'COVID-19', 'SARS-CoV-2', 'covid-19', 'Pandemics', '“COVID-19”', 'covid‐19', 'COVID‐19', 'SARS‐CoV‐2', 'SARS-CoV-2 pandemic', 'COVID-19 or SARS-CoV-2', 'pandemie', 'Coronavirus')""")

conn.commit()
conn.close()