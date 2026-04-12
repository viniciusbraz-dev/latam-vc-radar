"""
scrape_dealroom.py
Coleta deals LATAM via Dealroom portais de ecossistema (dados limitados).
"""
import json, os, re, requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; LATAMVCRadar/1.0)"}
URLS = [
    "https://app.dealroom.co/companies/filter/location/anyof_country_id/brazil",
    "https://ecosistema.lavca.org/",
]
OUTPUT = ".tmp/raw_dealroom.json"

def scrape():
    results = []
    for url in URLS:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code in [403, 429, 503]:
                print(f"[dealroom] bloqueado em {url}: {resp.status_code}")
                continue
            soup = BeautifulSoup(resp.text, 'html.parser')
            cards = soup.select('.company-card, .startup-item, article')
            for card in cards[:10]:
                name_el = card.select_one('h2, h3, .name')
                if not name_el:
                    continue
                name = name_el.get_text(strip=True)
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
                    "source_url": url,
                    "source_name": "Dealroom",
                    "verified": False,
                    "data_quality_note": "Dados limitados — JS não renderizado",
                    "sources_count": 1,
                    "confidence_score": 0.2
                })
        except Exception as e:
            print(f"[dealroom] erro em {url}: {e}")
    os.makedirs(".tmp", exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[dealroom] {len(results)} empresas encontradas")
    return results

if __name__ == "__main__":
    scrape()
