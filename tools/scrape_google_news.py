"""
scrape_google_news.py
Coleta deals via Google News RSS com queries em PT-BR e EN.
"""
import json, os, re, feedparser
from datetime import datetime

OUTPUT = ".tmp/raw_google_news.json"

QUERIES = [
    "startup LATAM rodada investimento",
    "startup Brasil captou milhões investimento",
    "startup América Latina funding round",
    "venture capital Brazil startup raises",
    "startup Mexico Argentina Colombia funding",
]

COUNTRY_MAP = {
    'brasil': 'Brasil', 'brazil': 'Brasil', 'são paulo': 'Brasil',
    'méxico': 'México', 'mexico': 'México',
    'argentina': 'Argentina', 'buenos aires': 'Argentina',
    'colombia': 'Colômbia', 'bogotá': 'Colômbia',
    'chile': 'Chile', 'santiago': 'Chile',
    'peru': 'Peru', 'lima': 'Peru',
    'equador': 'Equador', 'ecuador': 'Equador',
    'uruguai': 'Uruguai', 'uruguay': 'Uruguai',
}

ROUND_PATTERNS = ['seed', 'pre-seed', 'pré-seed', 'series a', 'série a', 'series b', 'série b',
                  'series c', 'série c', 'series d', 'série d', 'growth', 'ipo']

def detect_country(text):
    t = text.lower()
    for k, v in COUNTRY_MAP.items():
        if k in t:
            return v
    return None

def detect_round(text):
    t = text.lower()
    for r in ROUND_PATTERNS:
        if r in t:
            return r.title()
    return None

def parse_amount(text):
    m = re.search(r'R\$\s*([\d,.]+)\s*(M|mi|milh|B|bi)?', text, re.IGNORECASE)
    if m:
        val = float(m.group(1).replace('.', '').replace(',', '.'))
        s = (m.group(2) or '').lower()
        if s.startswith('b'): val *= 1_000_000_000
        elif s.startswith('m'): val *= 1_000_000
        return round(val / 5.5), f"R$ {m.group(1)}{m.group(2) or ''}"
    m = re.search(r'US?\$?\s*([\d,.]+)\s*(M|B|million|billion)?', text, re.IGNORECASE)
    if m:
        val = float(m.group(1).replace(',', ''))
        s = (m.group(2) or '').lower()
        if 'b' in s: val *= 1_000_000_000
        elif 'm' in s: val *= 1_000_000
        return round(val), f"USD {m.group(1)}{m.group(2) or ''}"
    return 0, None

def scrape():
    results = []
    seen = set()
    for query in QUERIES:
        rss_url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:8]:
                title = entry.get('title', '')
                url = entry.get('link', '')
                summary = entry.get('summary', '')
                full = title + ' ' + summary
                if url in seen:
                    continue
                seen.add(url)
                if not any(k in full.lower() for k in ['rodada', 'captou', 'investimento', 'raises', 'funding', 'startup', 'série', 'seed']):
                    continue
                company = re.sub(r'\s*(capta|levanta|raises|secures|anuncia|fecha)\s.*', '', title, flags=re.IGNORECASE).strip()
                company = company.split(' - ')[0].split(' | ')[0].strip()
                amount_usd, amount_orig = parse_amount(full)
                country = detect_country(full)
                round_type = detect_round(full)
                pub = entry.get('published', None)
                date_str = None
                if pub:
                    try:
                        import email.utils
                        date_str = datetime(*email.utils.parsedate(pub)[:6]).strftime('%Y-%m-%d')
                    except:
                        pass
                results.append({
                    "company_name": company,
                    "description": summary[:300] if summary else None,
                    "sector": None,
                    "headquarters": None,
                    "country": country,
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
                    "source_name": "Google News RSS",
                    "verified": False,
                    "data_quality_note": None,
                    "sources_count": 1,
                    "confidence_score": 0.35
                })
        except Exception as e:
            print(f"[google_news] erro query '{query}': {e}")
    os.makedirs(".tmp", exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[google_news] {len(results)} deals encontrados")
    return results

if __name__ == "__main__":
    scrape()
