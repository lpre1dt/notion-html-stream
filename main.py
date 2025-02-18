import requests
from datetime import datetime, timezone

NOTION_TOKEN = "secret_oIlS8Ss0JfsEfUp0AfVpNpmN1rj41AcsPbIFGwokBhm"
DATABASE_ID = "1732268253ab80cd8829ceb924798f0e"

headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application-json",
    "Notion-Version": "2022-06-28"
}

def get_pages():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {"page_size": 100}
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()
    import json
    with open('db.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    return data

print(get_pages())