import requests
import json
from bs4 import BeautifulSoup
import xmltodict

def fetch_pubmed_data(term, page = 1, type='full'):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        'db': 'pubmed',
        'term': term,
        'sort': 'most_recent',
        'datetype': 'edat',
        'reldate': 2,
        'retmax': 300,
        'retstart': (page - 1) * 300,
        'retmode': 'json',
        'apikey': None
    }

    try:
        response = requests.get(base_url, params=params)
        id_list = response.json().get('esearchresult', {}).get('idlist', [])

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

PAGES = 50
CURRENT_PAGE = 1

while CURRENT_PAGE + 1 < PAGES:
    data = fetch_pubmed_data('COVID-19', CURRENT_PAGE)
    CURRENT_PAGE += 1

    if data.status_code != 200:
        break

    data_dict = {}
    Bs_data = BeautifulSoup(data.text, 'xml')
    data_dict = json.dumps(xmltodict.parse(Bs_data.prettify()))

    with open(f'/app/raw_data/pubmed/pubmed_full_{CURRENT_PAGE - 1}.json', 'w', encoding="utf-8") as json_file:
        json.dump(json.loads(data_dict), json_file, indent=4)