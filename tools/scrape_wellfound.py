"""
scrape_wellfound.py
Coleta startups LATAM via Wellfound/AngelList (páginas públicas).
"""
import json, os, re, requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; LATAMVCRadar/1.0)"}
URL = "https://wellfound.com/startups/location/latin-america"
OUTPUT = ".tmp/raw_wellfound.json"

def scrape():
    results = []
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=15)
        if resp.status_code in [403, 429]:
            print(f"[wellfound] bloqueado: {resp.status_code}")
        elif resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            cards = soup.select('.startup-link, [data-testid="company-card"], .styles_component__')
            for card in cards[:20]:
                name_el = card.select_one('h2, h3, .name, [data-testid="company-name"]')
                if not name_el:
                    continue
                name = name_el.get_text(strip=True)
                desc_el = card.select_one('p, .pitch, .description')
                desc = desc_el.get_text(strip=True) if desc_el else None
                link_el = card.select_one('a')
                url = link_el.get('href', '') if link_el else ''
                if url and not url.startswith('http'):
                    url = 'https://wellfound.com' + url
                results.append({
                    "company_name": name,
                    "description": desc[:300] if desc else None,
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
                    "source_name": "Wellfound",
                    "verified": False,
                    "data_quality_note": "Sem valor de rodada confirmado",
                    "sources_count": 1,
                    "confidence_score": 0.25
                })
    except Exception as e:
        print(f"[wellfound] erro: {e}")
    os.makedirs(".tmp", exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[wellfound] {len(results)} empresas encontradas")
    return results

if __name__ == "__main__":
    scrape()
