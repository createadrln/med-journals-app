import requests
import json
import os

raw_data_path = '../raw_data'
if not os.path.exists(raw_data_path):
    os.makedirs(raw_data_path)

def fetch_doaj_data(query, page_size=5):
    base_url = f"https://doaj.org/api/search/articles/{query}"
    params = {
        'pageSize': page_size,
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while querying DOAJ: {e}")

with open('/app/raw_data/doaj.json', 'w') as json_file:
    json.dump(fetch_doaj_data("COVID-19", page_size=100), json_file, indent=4)