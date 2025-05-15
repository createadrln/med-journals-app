import os
import json
import springernature_api_client.openaccess as openaccess
from dotenv import load_dotenv

load_dotenv()


def fetch_springer_data():
    API_KEY = os.getenv("SPRINGER_API_KEY")
    openaccess_client = openaccess.OpenAccessAPI(API_KEY)
    try:
        response = openaccess_client.search(
            q="COVID-19", p=20, s=1, fetch_all=False, is_premium=False)
        return response
    except Exception as e:
        print(f"An error occurred while querying Springer Data: {e}")


with open("/app/raw_data/springer.json", "w", encoding="utf-8") as json_file:
    json.dump(fetch_springer_data(), json_file, indent=4)
