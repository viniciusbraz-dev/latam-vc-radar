"""
scrape_distrito.py
Scraper para Distrito — ecossistema de startups BR.
"""
import json, os, re, requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; LATAMVCRadar/1.0)"}
URL = "https://distrito.me/radar/?category=funding"
OUTPUT = ".tmp/raw_distrito.json"

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
        cards = soup.select('.radar-item, .funding-card, article.post, .card')
        for card in cards[:20]:
            name_el = card.select_one('h2, h3, .company-name, .title')
            if not name_el:
                continue
            name = name_el.get_text(strip=True)
            link_el = card.select_one('a')
            url = link_el.get('href', '') if link_el else ''
            if url and not url.startswith('http'):
                url = 'https://distrito.me' + url
            desc_el = card.select_one('p, .description, .excerpt')
            desc = desc_el.get_text(strip=True) if desc_el else None
            amount_text = card.get_text()
            amount_usd, amount_orig = parse_amount(amount_text)
            date_el = card.select_one('time, .date')
            date_str = date_el.get('datetime', date_el.get_text(strip=True)) if date_el else None
            results.append({
                "company_name": name,
                "description": desc[:300] if desc else None,
                "sector": None,
                "headquarters": None,
                "country": "Brasil",
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
                "source_name": "Distrito",
                "verified": False,
                "data_quality_note": None,
                "sources_count": 1,
                "confidence_score": 0.45
            })
    except Exception as e:
        print(f"[distrito] erro: {e}")
    os.makedirs(".tmp", exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[distrito] {len(results)} deals encontrados")
    return results

if __name__ == "__main__":
    scrape()
