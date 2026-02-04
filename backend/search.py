import os
import json
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

API_KEY = os.getenv('GOOGLE_API_KEY')
CSE_ID = os.getenv('GOOGLE_CSE_ID')

KEYWORDS = ["slot", "gacor", "maxwin"]

def search(domain, num=10):
    keywords = ' '.join([f'"{kw}"' for kw in KEYWORDS])
    query = f'site:{domain} {keywords}'
    
    service = build("customsearch", "v1", developerKey=API_KEY)
    result = service.cse().list(q=query, cx=CSE_ID, num=num).execute()
    
    items = result.get('items', [])
    return [{'title': item['title'], 'link': item['link'], 'snippet': item.get('snippet', '')} for item in items]

if __name__ == '__main__':
    results = search("ejurnal.iainpare.ac.id")
    print(json.dumps(results, indent=2))
