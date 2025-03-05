import requests
import json
from bs4 import BeautifulSoup
import xmltodict
import os

raw_data_path = '../raw_data'
if not os.path.exists(raw_data_path):
    os.makedirs(raw_data_path)

def fetch_pubmed_data(term, type='full'):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        'db': 'pubmed',
        'term': term,
        'sort': 'most_recent',
        'datetype': 'edat',
        'reldate': 2,
        # 'retmax': 9999,
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
