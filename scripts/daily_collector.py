import csv
from datetime import datetime
import sqlite3
import requests
import json
from bs4 import BeautifulSoup
import xmltodict


def fetch_pubmed_data(term, type='full'):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        'db': 'pubmed',
        'term': term,
        'sort': 'most_recent',
        'datetype': 'edat',
        'reldate': 2,
        'retmax': 9999,
        'retmode': 'json',
        'apikey': None
    }
    try:
        response = requests.get(base_url, params=params)
        id_list = response.json()['esearchresult']['idlist']

        if type == 'detail':
            detail_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            details_params = {
                'db': 'pubmed',
                'id': ','.join(id_list),
                'retmode': 'json',
                'apikey': None
            }
            detail_response = requests.get(detail_url, params=details_params)
            return detail_response.json()

        full_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        full_params = {
            'db': 'pubmed',
            'id': ','.join(id_list),
            'rettype': 'medline',
            'retmode': 'xml',
            'apikey': None
        }
        full_response = requests.get(full_url, params=full_params)
        return full_response
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while querying PubMed: {e}")


full_data = fetch_pubmed_data('COVID-19')
detail_data = fetch_pubmed_data('COVID-19', 'detail')

full_data_dict = {}
Bs_data = BeautifulSoup(full_data.text, 'xml')
full_data_dict = json.dumps(xmltodict.parse(Bs_data.prettify()))

with open('../raw_data/pubmed_full.json', 'w') as json_file:
    json.dump(json.loads(full_data_dict), json_file, indent=4)

with open('../raw_data/pubmed_detail.json', 'w') as json_file:
    json.dump(detail_data, json_file, indent=4)

# Combine data files

# Open Pubmed JSON data file
with open('../raw_data/pubmed_full.json', 'r') as json_file:
    pubmed_full_data = json.load(json_file)

# Open DOAJ JSON data file
with open('../raw_data/doaj.json', 'r') as json_file:
    doaj_full_data = json.load(json_file)

# Open Europe PMC JSON data file
with open('../raw_data/europe_pmc.json', 'r') as json_file:
    europe_pmc_full_data = json.load(json_file)

final_pubmed_data = []
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

conn = sqlite3.connect('../databases/CovidData.db')
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
        keyword TEXT PRIMARY KEY,
        count INTEGER
    )
"""

create_abstracts_table_sql = """
    CREATE TABLE IF NOT EXISTS covid_research_abstracts (
        id TEXT PRIMARY KEY,
        abstract INTEGER
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
            with open('keyword_stopwords.csv', 'r') as file:
                reader = csv.reader(file, delimiter=',')
                for row in reader:
                    for keyword in item['keywords']:
                        keywords_list.append(keyword)
                        if keyword.strip().lower().replace('-', '') not in row:
                            cursor.execute(
                                "INSERT INTO covid_research_keywords VALUES(?,?) ON CONFLICT(keyword) DO UPDATE SET count=count+1", (keyword, 1))

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
                with open('keyword_stopwords.csv', 'r') as file:
                    reader = csv.reader(file, delimiter=',')
                    for row in reader:
                        if keyword.strip().lower().replace('-', '') not in row:
                            cursor.execute(
                                "INSERT INTO covid_research_keywords VALUES(?,?) ON CONFLICT(keyword) DO UPDATE SET count=count+1", (keyword, 1))

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

cursor.execute(
    """DELETE FROM covid_research_keywords WHERE keyword IN ('Pandemic', 'pandemic', 'COVID-19', 'SARS-CoV-2', 'covid-19', 'Pandemics', '“COVID-19”', 'covid-19', 'COVID-19')""")

conn.commit()
conn.close()
