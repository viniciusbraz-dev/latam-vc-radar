"""
scrape_startups_br.py
Scraper para startups.com.br — notícias de rodadas de investimento brasileiras.
"""
import json, os, re, requests
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; LATAMVCRadar/1.0)"}
BASE_URL = "https://startups.com.br"
SEARCH_URL = f"{BASE_URL}/?s=rodada+investimento"
OUTPUT = ".tmp/raw_startups_br.json"


def parse_amount(text):
    if not text:
        return 0, None
    text = text.strip()
    m = re.search(r'R\$\s*([\d,.]+)\s*(M|mi|milh|B|bi|bilh)?', text, re.IGNORECASE)
    if m:
        val = float(m.group(1).replace('.', '').replace(',', '.'))
        suffix = (m.group(2) or '').lower()
        if suffix.startswith('b') or suffix.startswith('bi'):
            val *= 1_000_000_000
        elif suffix.startswith('m') or suffix.startswith('mi'):
            val *= 1_000_000
        return round(val / 5.5), f"R$ {m.group(1)}{m.group(2) or ''}"
    m = re.search(r'US?\$?\s*([\d,.]+)\s*(M|mi|B|bi)?', text, re.IGNORECASE)
    if m:
        val = float(m.group(1).replace(',', ''))
        suffix = (m.group(2) or '').lower()
        if suffix.startswith('b'):
            val *= 1_000_000_000
        elif suffix.startswith('m'):
            val *= 1_000_000
        return round(val), f"USD {m.group(1)}{m.group(2) or ''}"
    return 0, None


def scrape():
    results = []
    try:
        resp = requests.get(SEARCH_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        articles = soup.select('article.post, .td-module-container, .jeg_post')
        if not articles:
            articles = soup.select('article')
        for art in articles[:20]:
            title_el = art.select_one('h2 a, h3 a, .entry-title a, .jeg_post_title a')
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            url = title_el.get('href', '')
            if not any(k in title.lower() for k in ['rodada', 'investimento', 'aporte', 'série', 'seed', 'milhões']):
                continue
            company = re.sub(r'\s*(capta|levanta|recebe|anuncia|fecha)\s.*', '', title, flags=re.IGNORECASE).strip()
            company = re.sub(r'^startup\s+', '', company, flags=re.IGNORECASE).strip()
            amount_usd, amount_orig = parse_amount(title)
            date_el = art.select_one('time, .entry-date, .jeg_meta_date')
            date_str = None
            if date_el:
                date_str = date_el.get('datetime', date_el.get_text(strip=True))
            results.append({
                "company_name": company,
                "description": None,
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
                "source_name": "startups.com.br",
                "verified": False,
                "data_quality_note": None,
                "sources_count": 1,
                "confidence_score": 0.4
            })
    except Exception as e:
        print(f"[startups_br] erro: {e}")
    os.makedirs(".tmp", exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[startups_br] {len(results)} deals encontrados")
    return results


if __name__ == "__main__":
    scrape()
