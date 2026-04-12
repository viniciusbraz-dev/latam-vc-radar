"""
scrape_latamlist.py
Scraper para LatamList — cobertura ampla de deals LATAM.
"""
import json, os, re, requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; LATAMVCRadar/1.0)"}
URL = "https://www.latamlist.com/category/funding/"
OUTPUT = ".tmp/raw_latamlist.json"

COUNTRY_HINTS = {
    'brasil': 'Brasil', 'brazil': 'Brasil', 'são paulo': 'Brasil', 'rio de janeiro': 'Brasil',
    'méxico': 'México', 'mexico': 'México', 'cdmx': 'México',
    'argentina': 'Argentina', 'buenos aires': 'Argentina',
    'colombia': 'Colômbia', 'colômbia': 'Colômbia', 'bogotá': 'Colômbia',
    'chile': 'Chile', 'santiago': 'Chile',
    'peru': 'Peru', 'lima': 'Peru',
    'equador': 'Equador', 'ecuador': 'Equador', 'quito': 'Equador',
    'uruguay': 'Uruguai', 'uruguai': 'Uruguai', 'montevideo': 'Uruguai',
}

def detect_country(text):
    t = text.lower()
    for k, v in COUNTRY_HINTS.items():
        if k in t:
            return v
    return None

def parse_amount(text):
    if not text:
        return 0, None
    m = re.search(r'\$\s*([\d,.]+)\s*(M|B|K)?', text, re.IGNORECASE)
    if m:
        val = float(m.group(1).replace(',', ''))
        suffix = (m.group(2) or '').upper()
        if suffix == 'B':
            val *= 1_000_000_000
        elif suffix == 'M':
            val *= 1_000_000
        elif suffix == 'K':
            val *= 1_000
        return round(val), f"USD {m.group(1)}{m.group(2) or ''}"
    return 0, None

def scrape():
    results = []
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        articles = soup.select('article, .post-item, .entry')
        if not articles:
            articles = soup.select('div.jeg_post, div.td-block-row article')
        for art in articles[:20]:
            title_el = art.select_one('h2 a, h3 a, .entry-title a')
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            url = title_el.get('href', '')
            excerpt_el = art.select_one('.entry-summary, .jeg_post_excerpt, p')
            excerpt = excerpt_el.get_text(strip=True) if excerpt_el else ''
            full_text = title + ' ' + excerpt
            company = re.sub(r'\s+(raises|secures|closes|gets|lands|receives)\s.*', '', title, flags=re.IGNORECASE).strip()
            amount_usd, amount_orig = parse_amount(full_text)
            country = detect_country(full_text)
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
                "source_name": "LatamList",
                "verified": False,
                "data_quality_note": None,
                "sources_count": 1,
                "confidence_score": 0.45
            })
    except Exception as e:
        print(f"[latamlist] erro: {e}")
    os.makedirs(".tmp", exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[latamlist] {len(results)} deals encontrados")
    return results

if __name__ == "__main__":
    scrape()
