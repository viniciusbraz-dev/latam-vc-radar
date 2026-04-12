"""
scrape_bloomberg_linea.py
Scraper para Bloomberg Línea BR — roundups semanais de deals.
"""
import json, os, re, requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; LATAMVCRadar/1.0)"}
URL = "https://bloomberglinea.com.br/busca/?q=rodada+investimento+startup"
OUTPUT = ".tmp/raw_bloomberg_linea.json"

ROUND_TYPES = ['seed', 'series a', 'série a', 'series b', 'série b', 'series c', 'série c',
               'series d', 'série d', 'pre-seed', 'pré-seed', 'growth', 'ipo', 'follow-on']

def detect_round(text):
    t = text.lower()
    for r in ROUND_TYPES:
        if r in t:
            return r.title()
    return None

def parse_amount(text):
    m = re.search(r'R\$\s*([\d,.]+)\s*(M|mi|B|bi)?', text, re.IGNORECASE)
    if m:
        val = float(m.group(1).replace('.', '').replace(',', '.'))
        s = (m.group(2) or '').lower()
        if s.startswith('b'): val *= 1_000_000_000
        elif s.startswith('m'): val *= 1_000_000
        return round(val / 5.5), f"R$ {m.group(1)}{m.group(2) or ''}"
    m = re.search(r'US?\$?\s*([\d,.]+)\s*(M|B)?', text, re.IGNORECASE)
    if m:
        val = float(m.group(1).replace(',', ''))
        s = (m.group(2) or '').upper()
        if s == 'B': val *= 1_000_000_000
        elif s == 'M': val *= 1_000_000
        return round(val), f"USD {m.group(1)}{m.group(2) or ''}"
    return 0, None

def scrape():
    results = []
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        articles = soup.select('article, .search-result, .card-article, .post')
        for art in articles[:15]:
            title_el = art.select_one('h2 a, h3 a, a.title, .headline a')
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            url = title_el.get('href', '')
            if not url.startswith('http'):
                url = 'https://bloomberglinea.com.br' + url
            if not any(k in title.lower() for k in ['rodada', 'investimento', 'captou', 'captação', 'startup']):
                continue
            company = re.sub(r'\s*(capta|levanta|anuncia|fecha|recebe)\s.*', '', title, flags=re.IGNORECASE).strip()
            amount_usd, amount_orig = parse_amount(title)
            round_type = detect_round(title)
            date_el = art.select_one('time')
            date_str = date_el.get('datetime') if date_el else None
            results.append({
                "company_name": company,
                "description": None,
                "sector": None,
                "headquarters": None,
                "country": "Brasil",
                "founded_year": None,
                "round_type": round_type,
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
                "source_name": "Bloomberg Línea BR",
                "verified": False,
                "data_quality_note": None,
                "sources_count": 1,
                "confidence_score": 0.5
            })
    except Exception as e:
        print(f"[bloomberg_linea] erro: {e}")
    os.makedirs(".tmp", exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[bloomberg_linea] {len(results)} deals encontrados")
    return results

if __name__ == "__main__":
    scrape()
