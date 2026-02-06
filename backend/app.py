import os
import json
import re
import sqlite3
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timezone
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from googleapiclient.discovery import build

load_dotenv()

app = Flask(__name__)

cors_origins = os.getenv('FRONTEND_ORIGINS', 'http://localhost:5173')
cors_allowed = [origin.strip() for origin in cors_origins.split(',') if origin.strip()]

CORS(
    app,
    resources={r"/*": {"origins": cors_allowed}},
    supports_credentials=False
)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per day", "10 per minute"]
)

API_KEY = os.getenv('GOOGLE_API_KEY')
CSE_ID = os.getenv('GOOGLE_CSE_ID')
KEYWORDS = ["gacor", "slot777", "slot888", "togel", "casino", "poker", "maxwin", "zeus"]
DB_PATH = os.getenv('DB_PATH', 'data.sqlite3')

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                visitor_ip TEXT NOT NULL,
                domain TEXT NOT NULL,
                is_affected INTEGER NOT NULL,
                results TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

def _get_client_ip():
    forwarded = request.headers.get('X-Forwarded-For', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr or ''

def save_search(visitor_ip, domain, is_affected, results):
    created_at = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO searches (visitor_ip, domain, is_affected, results, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (visitor_ip, domain, 1 if is_affected else 0, json.dumps(results), created_at)
        )

def is_valid_domain(domain):
    pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    return re.match(pattern, domain) is not None

def search(domain, num=10):
    # Use OR operator for keywords to find any occurrence
    keywords_query = ' OR '.join([f'"{kw}"' for kw in KEYWORDS])
    query = f'site:{domain} ({keywords_query})'
    
    try:
        service = build("customsearch", "v1", developerKey=API_KEY)
        result = service.cse().list(q=query, cx=CSE_ID, num=num).execute()
        
        items = result.get('items', [])
        filtered_results = []
        
        for item in items:
            title = item.get('title', '').lower()
            snippet = item.get('snippet', '').lower()
            link = item.get('link', '').lower()
            
            # Check if any keyword matches strictly in title, snippet, or even the link
            if any(kw.lower() in title or kw.lower() in snippet or kw.lower() in link for kw in KEYWORDS):
                filtered_results.append({
                    'title': item['title'],
                    'link': item['link'],
                    'snippet': item.get('snippet', '')
                })
                
        return filtered_results
    except Exception as e:
        print(f"Search API Error: {e}")
        raise e

def calculate_reputation_score(results):
    count = len(results)
    # Deduct 15 points per finding, min 0
    score = max(0, 100 - (count * 15))
    
    # Determine Grade
    if score >= 95: grade = 'A+'
    elif score >= 90: grade = 'A'
    elif score >= 80: grade = 'B'
    elif score >= 60: grade = 'C'
    elif score >= 40: grade = 'D'
    else: grade = 'F'
    
    # Analyze keywords found for report
    found_keywords = set()
    for item in results:
        text = (item['title'] + " " + item['snippet']).lower()
        for kw in KEYWORDS:
            if kw in text:
                found_keywords.add(kw)
    
    checks = {}
    
    # Check 1: Page Cleanness
    checks['Content Integrity'] = {
        'passed': count == 0,
        'value': "No compromised pages found" if count == 0 else f"{count} suspicious pages detected"
    }
    
    # Check 2: Keyword Traces
    checks['Keyword Scanning'] = {
        'passed': len(found_keywords) == 0,
        'value': "Clean" if len(found_keywords) == 0 else f"Detected: {', '.join(list(found_keywords)[:3])}" + ("..." if len(found_keywords) > 3 else "")
    }
    
    # Check 3: Risk Level
    if score >= 90:
        risk_val = "Safe"
        risk_passed = True
    elif score >= 60:
        risk_val = "Moderate Risk"
        risk_passed = True # Still "green-ish" or warning? Let's make it passed=False if <80 effectively
        if score < 80: risk_passed = False
    else:
        risk_val = "Critical Risk"
        risk_passed = False
        
    checks['Risk Assessment'] = {
        'passed': risk_passed,
        'value': risk_val
    }
    
    return {
        'grade': grade,
        'score': score,
        'checks': checks
    }

init_db()

@app.route('/search', methods=['POST'])
@limiter.limit("10 per minute")
def search_api():
    data = request.get_json()
    
    if not data or 'domain' not in data:
        return jsonify({'error': 'domain wajib diisi'}), 400

    # Captcha Verification
    enable_captcha = os.getenv('ENABLE_CAPTCHA', 'true').lower() == 'true'
    
    if enable_captcha:
        captcha_token = data.get('captchaToken')
        if not captcha_token:
             return jsonify({'error': 'Verifikasi keamanan diperlukan'}), 400

        try:
            secret = os.getenv('RECAPTCHA_SECRET_KEY')

            if not secret:
                print("Configuration Error: RECAPTCHA_SECRET_KEY not set")
                return jsonify({'error': 'Server misconfiguration'}), 500

            verify_url = "https://www.google.com/recaptcha/api/siteverify"
            verify_payload = urllib.parse.urlencode({
                "secret": secret,
                "response": captcha_token,
                "remoteip": request.remote_addr
            }).encode('utf-8')

            req = urllib.request.Request(
                verify_url,
                data=verify_payload,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            with urllib.request.urlopen(req) as response:
                verify_response = json.loads(response.read().decode('utf-8'))
                
                if not verify_response.get('success'):
                    return jsonify({'error': 'Verifikasi keamanan gagal'}), 400
                    
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"Captcha HTTP Error {e.code}: {error_body}")
            return jsonify({'error': f'Gagal memverifikasi captcha: Server responded with {e.code}'}), 500
        except urllib.error.URLError as e:
            print(f"Captcha Connection Error: {e.reason}")
            return jsonify({'error': 'Gagal memverifikasi captcha: Tidak dapat terhubung ke server verifikasi'}), 500
        except Exception as e:
            print(f"Captcha Error: {str(e)}")
            return jsonify({'error': f'Gagal memverifikasi captcha: {str(e)}'}), 500
    
    domain = data['domain']

    # Clean domain: remove protocol (http://, https://) and path/trailing slash
    domain = re.sub(r'https?://', '', domain)
    domain = domain.split('/')[0]
    
    if not is_valid_domain(domain):
        return jsonify({'error': 'format domain tidak valid'}), 400
    
    try:
        results = search(domain)
        
        # Calculate reputation based on findings
        reputation_report = calculate_reputation_score(results)

        visitor_ip = _get_client_ip()
        is_affected = len(results) > 0
        save_search(visitor_ip, domain, is_affected, results)
        
        return jsonify({
            'results': results,
            'security': reputation_report
        })
    except Exception as e:
        print(f"Error: {str(e)}")  # Log error
        return jsonify({'error': f'Pencarian gagal: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', '5151'))
    app.run(host='0.0.0.0', port=port, debug=False)
