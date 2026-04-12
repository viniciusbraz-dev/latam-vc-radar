"""
scrape_cuantico.py
Scraper para Cuántico VP — pesquisa de VC LATAM, reports públicos.
"""
import json, os, re, requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; LATAMVCRadar/1.0)"}
URLS = [
    "https://cuantico.vc/",
    "https://cuantico.vc/blog/",
]
OUTPUT = ".tmp/raw_cuantico.json"

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
    for base_url in URLS:
        try:
            resp = requests.get(base_url, headers=HEADERS, timeout=15)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, 'html.parser')
            articles = soup.select('article, .post, .entry, .blog-post')
            for art in articles[:10]:
                title_el = art.select_one('h2 a, h3 a, .title a, .entry-title a')
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                url = title_el.get('href', '')
                if url and not url.startswith('http'):
                    url = 'https://cuantico.vc' + url
                excerpt_el = art.select_one('p, .excerpt')
                excerpt = excerpt_el.get_text(strip=True) if excerpt_el else ''
                full = title + ' ' + excerpt
                if not any(k in full.lower() for k in ['startup', 'vc', 'venture', 'fondo', 'fundo', 'investment', 'fund']):
                    continue
                amount_usd, amount_orig = parse_amount(full)
                date_el = art.select_one('time')
                date_str = date_el.get('datetime') if date_el else None
                results.append({
                    "company_name": title.split(':')[0].strip(),
                    "description": excerpt[:300] if excerpt else None,
                    "sector": None,
                    "headquarters": None,
                    "country": None,
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
                    "source_name": "Cuántico VP",
                    "verified": False,
                    "data_quality_note": None,
                    "sources_count": 1,
                    "confidence_score": 0.35
                })
        except Exception as e:
            print(f"[cuantico] erro em {base_url}: {e}")
    os.makedirs(".tmp", exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[cuantico] {len(results)} items encontrados")
    return results

if __name__ == "__main__":
    scrape()
