from datetime import date
import json
import sqlite3
from datetime import datetime
import os

for filename in os.listdir('../raw_data/2023archive'):
    if filename.endswith('.json') and 'pubmed' in filename:
        print(filename)
        with open(os.path.join('../raw_data/2023archive', filename), 'r') as json_file:
            pubmed_data = json.load(json_file)

            final_pubmed_data = []
            for article in pubmed_data['PubmedArticleSet'].get('PubmedArticle', []):
                final_data_row = {
                    'id': article['MedlineCitation']['PMID']['#text'],
                    'source': 'PubMed',
                    'date': article['MedlineCitation']['DateRevised'],
                    'title': article['MedlineCitation']['Article']['ArticleTitle'],
                    'link': f'https://pubmed.ncbi.nlm.nih.gov/{article["MedlineCitation"]["PMID"]["#text"]}/',
                    'authors': article['MedlineCitation']['Article'].get('AuthorList', {}).get('Author', []),
                    'keywords': article['MedlineCitation'].get('KeywordList', {}).get('Keyword', []),
                    'abstract': article['MedlineCitation']['Article'].get('Abstract', {}).get('AbstractText', [])
                }
                final_pubmed_data.append(final_data_row)

            today = date.today()

            final_all = final_pubmed_data

            with open('../raw_data/combined_sources_pubmed.json', 'w') as json_file:
                json.dump(final_all, json_file, indent=4)

            # Load to Database

            conn = sqlite3.connect('../data/CovidData.db')
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

            with open('../raw_data/combined_sources_pubmed.json', 'r') as json_file:
                data = json.load(json_file)

                for item in data:

                    if item['source'] == 'PubMed':
                        formatted_date_str = f"{item['date']['Year']}-{item['date']['Month']}-{item['date']['Day']}"
                        datetime_object = datetime.strptime(
                            formatted_date_str, '%Y-%m-%d')
                        datetime_timestamp = datetime.timestamp(
                            datetime_object)

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
                                keywords_list.append(keyword.get('#text', ''))

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

                        abstracts_list = []
                        if isinstance(item['abstract'], dict):
                            abstracts_list.append(item['abstract'].get('#text', '').strip())
                        elif isinstance(item['abstract'], str):
                            abstracts_list.append(item['abstract'].strip())
                        else:
                            for abstract in item['abstract']:
                                abstracts_list.append(abstract.get('#text', '').strip())

                        cursor.execute("INSERT OR IGNORE INTO covid_research_abstracts VALUES(?,?)", (
                            item['id'],
                            list_delimiter.join(abstracts_list),
                        ))

            cursor.execute("DELETE FROM covid_research_abstracts WHERE abstract IS NULL OR TRIM(abstract) = ''")

            conn.commit()
            conn.close()
