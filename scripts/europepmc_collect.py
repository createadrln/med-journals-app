import requests
import json
from datetime import date


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
