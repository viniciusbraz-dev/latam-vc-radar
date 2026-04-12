"""
scrape_lavca.py
Scraper para LAVCA (Latin America Private Capital Association) — deal announcements.
"""
import json, os, re, requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; LATAMVCRadar/1.0)"}
URL = "https://lavca.org/category/news/"
OUTPUT = ".tmp/raw_lavca.json"

COUNTRY_MAP = {
    'brazil': 'Brasil', 'brasil': 'Brasil',
    'mexico': 'México', 'méxico': 'México',
    'argentina': 'Argentina',
    'colombia': 'Colômbia', 'colômbia': 'Colômbia',
    'chile': 'Chile',
    'peru': 'Peru',
    'ecuador': 'Equador',
    'uruguay': 'Uruguai',
    'costa rica': 'Costa Rica',
    'panama': 'Panamá',
}

def detect_country(text):
    t = text.lower()
    for k, v in COUNTRY_MAP.items():
        if k in t:
            return v
    return None

def parse_amount(text):
    m = re.search(r'\$\s*([\d,.]+)\s*(M|B|million|billion)?', text, re.IGNORECASE)
    if m:
        val = float(m.group(1).replace(',', ''))
        s = (m.group(2) or '').lower()
        if 'b' in s: val *= 1_000_000_000
        elif 'm' in s: val *= 1_000_000
        return round(val), f"USD {m.group(1)}{m.group(2) or ''}"
    return 0, None

def scrape():
    results = []
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        articles = soup.select('article, .post, .entry-item')
        for art in articles[:20]:
            title_el = art.select_one('h2 a, h3 a, .entry-title a')
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            url = title_el.get('href', '')
            if not any(k in title.lower() for k in ['investment', 'funding', 'raises', 'round', 'venture', 'capital']):
                continue
            excerpt_el = art.select_one('p, .excerpt, .entry-summary')
            excerpt = excerpt_el.get_text(strip=True) if excerpt_el else ''
            full = title + ' ' + excerpt
            company = re.sub(r'\s+(raises|secures|closes|announces|receives)\s.*', '', title, flags=re.IGNORECASE).strip()
            amount_usd, amount_orig = parse_amount(full)
            country = detect_country(full)
            date_el = art.select_one('time')
            date_str = date_el.get('datetime') if date_el else None
            results.append({
                "company_name": company,
                "description": excerpt[:300] if excerpt else None,
                "sector": None,
                "headquarters": None,
                "country": country,
                "founded_year": None,
                "round_type": None,
                "round_amount_usd": amount_usd,
                "round_amount_original": amount_orig,
                "lead_investors": [],
                "other_investors": [],
                "founders": [],
                "founder_linkedin_urls": [],
                "date": date_str,
                "linkedin_url": None,
                "website_url": None,
                "twitter_url": None,
                "logo_url": None,
                "source_url": url,
                "source_name": "LAVCA",
                "verified": False,
                "data_quality_note": None,
                "sources_count": 1,
                "confidence_score": 0.55
            })
    except Exception as e:
        print(f"[lavca] erro: {e}")
    os.makedirs(".tmp", exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[lavca] {len(results)} deals encontrados")
    return results

if __name__ == "__main__":
    scrape()
