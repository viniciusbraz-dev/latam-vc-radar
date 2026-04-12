"""
scrape_tracxn.py
Coleta deals LATAM via Tracxn (requer JS — coleta parcial).
"""
import json, os, requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; LATAMVCRadar/1.0)"}
URL = "https://tracxn.com/d/trending-themes/startups-in-latin-america"
OUTPUT = ".tmp/raw_tracxn.json"

def scrape():
    results = []
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=15)
        if resp.status_code in [403, 429]:
            print(f"[tracxn] bloqueado: {resp.status_code}")
        elif resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            rows = soup.select('tr, .company-row, .startup-row')
            for row in rows[:20]:
                name_el = row.select_one('td:first-child, .company-name, h3')
                if not name_el:
                    continue
                name = name_el.get_text(strip=True)
                if not name or len(name) < 2:
                    continue
                results.append({
                    "company_name": name,
                    "description": None,
                    "sector": None,
                    "headquarters": None,
                    "country": None,
                    "founded_year": None,
                    "round_type": None,
                    "round_amount_usd": 0,
                    "round_amount_original": None,
                    "lead_investors": [],
                    "other_investors": [],
                    "founders": [],
                    "founder_linkedin_urls": [],
                    "date": None,
                    "linkedin_url": None,
                    "website_url": None,
                    "twitter_url": None,
                    "logo_url": None,
                    "source_url": URL,
                    "source_name": "Tracxn",
                    "verified": False,
                    "data_quality_note": "JS não renderizado — dados incompletos",
                    "sources_count": 1,
                    "confidence_score": 0.2
                })
    except Exception as e:
        print(f"[tracxn] erro: {e}")
    os.makedirs(".tmp", exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[tracxn] {len(results)} empresas encontradas")
    return results

if __name__ == "__main__":
    scrape()
