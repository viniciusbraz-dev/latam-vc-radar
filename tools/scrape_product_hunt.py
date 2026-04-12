"""
scrape_product_hunt.py
Coleta launches recentes no Product Hunt com foco em LATAM.
"""
import json, os, re, requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; LATAMVCRadar/1.0)"}
URL = "https://www.producthunt.com/posts"
OUTPUT = ".tmp/raw_product_hunt.json"

LATAM_KEYWORDS = ['latam', 'latin america', 'brasil', 'brazil', 'mexico', 'argentina', 'colombia', 'chile']

def scrape():
    results = []
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=15)
        if resp.status_code in [403, 429]:
            print(f"[product_hunt] bloqueado: {resp.status_code}")
        elif resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            posts = soup.select('[data-test="post-item"], .post-item, article')
            for post in posts[:30]:
                name_el = post.select_one('h3, h2, .product-name')
                if not name_el:
                    continue
                name = name_el.get_text(strip=True)
                desc_el = post.select_one('p, .tagline')
                desc = desc_el.get_text(strip=True) if desc_el else ''
                full = name + ' ' + desc
                if not any(k in full.lower() for k in LATAM_KEYWORDS):
                    continue
                link_el = post.select_one('a')
                url = link_el.get('href', '') if link_el else ''
                if url and not url.startswith('http'):
                    url = 'https://www.producthunt.com' + url
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
                    "source_name": "Product Hunt",
                    "verified": False,
                    "data_quality_note": "Launch — sem rodada confirmada",
                    "sources_count": 1,
                    "confidence_score": 0.15
                })
    except Exception as e:
        print(f"[product_hunt] erro: {e}")
    os.makedirs(".tmp", exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[product_hunt] {len(results)} produtos encontrados")
    return results

if __name__ == "__main__":
    scrape()
