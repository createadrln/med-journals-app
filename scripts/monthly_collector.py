import requests
import json
from datetime import date
import springernature_api_client.openaccess as openaccess


def fetch_europepmc_data():
    BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

    all_results = []
    cursor_mark = "*"
    page_count = 0
    today = date.today()

    while page_count < 5:
        params = {
            "query": "COVID-19",
            "format": "json",
            "pageSize": "50",
            "cursorMark": cursor_mark
        }

        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            articles = data.get("resultList", {}).get("result", [])
            next_cursor = data.get("nextCursorMark", None)

            if not articles:
                print("No more articles found.")
                break

            all_results.extend(articles)

            if not next_cursor or next_cursor == cursor_mark:
                break

            cursor_mark = next_cursor
            page_count += 1

            return all_results

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while querying Europe PMC: {e}")
            break


with open("/app/raw_data/europe_pmc.json", "w", encoding="utf-8") as file:
    json.dump(fetch_europepmc_data(), file, indent=4)


def fetch_springer_data():
    API_KEY = "4469bb1a301391b47d98e28d86d95115"
    openaccess_client = openaccess.OpenAccessAPI(API_KEY)

    try:
        response = openaccess_client.search(
            q="COVID-19", p=20, s=1, fetch_all=True, is_premium=False)
        return response
    except Exception as e:
        print(f"An error occurred while querying Springer Data: {e}")

with open("/app/raw_data/springer.json", "w", encoding="utf-8") as json_file:
    json.dump(fetch_springer_data(), json_file, indent=4)
