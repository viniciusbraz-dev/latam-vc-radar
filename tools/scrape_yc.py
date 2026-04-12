"""
scrape_yc.py
Coleta startups LATAM via Y Combinator API pública (filtrado por país).
"""
import json, os, requests

OUTPUT = ".tmp/raw_yc.json"

LATAM_COUNTRIES = {
    'Brazil', 'Mexico', 'Argentina', 'Colombia', 'Chile',
    'Peru', 'Ecuador', 'Uruguay', 'Costa Rica', 'Panama',
    'Venezuela', 'Bolivia', 'Paraguay', 'Guatemala', 'Dominican Republic'
}

COUNTRY_PT = {
    'Brazil': 'Brasil', 'Mexico': 'México', 'Argentina': 'Argentina',
    'Colombia': 'Colômbia', 'Chile': 'Chile', 'Peru': 'Peru',
    'Ecuador': 'Equador', 'Uruguay': 'Uruguai', 'Costa Rica': 'Costa Rica',
    'Panama': 'Panamá', 'Venezuela': 'Venezuela', 'Bolivia': 'Bolívia',
    'Paraguay': 'Paraguai', 'Guatemala': 'Guatemala',
}

SECTOR_MAP = {
    'fintech': 'Fintech', 'finance': 'Fintech', 'banking': 'Fintech',
    'health': 'Healthtech', 'medical': 'Healthtech',
    'education': 'Edtech', 'edtech': 'Edtech',
    'ecommerce': 'E-commerce', 'marketplace': 'E-commerce',
    'logistics': 'Logística', 'delivery': 'Logística',
    'real estate': 'Proptech', 'proptech': 'Proptech',
    'saas': 'SaaS', 'software': 'SaaS',
    'climate': 'Cleantech', 'energy': 'Cleantech',
    'agriculture': 'Agtech', 'agtech': 'Agtech',
    'crypto': 'Crypto / Web3', 'blockchain': 'Crypto / Web3',
    'hr': 'HR Tech', 'recruiting': 'HR Tech',
    'insurance': 'Insurtech', 'insurtech': 'Insurtech',
}

def map_sector(tags):
    if not tags:
        return None
    tags_lower = [t.lower() for t in tags]
    for key, val in SECTOR_MAP.items():
        if any(key in t for t in tags_lower):
            return val
    return tags[0] if tags else None

def scrape():
    results = []
    try:
        resp = requests.get(
            "https://api.ycombinator.com/v0.1/companies?batch=&status=active",
            headers={"User-Agent": "Mozilla/5.0 (compatible; LATAMVCRadar/1.0)"},
            timeout=20
        )
        if resp.status_code != 200:
            # Fallback: página pública de companies
            raise Exception(f"API retornou {resp.status_code}")
        data = resp.json()
        companies = data.get('companies', data) if isinstance(data, dict) else data
        for co in companies:
            country = co.get('country', '')
            if country not in LATAM_COUNTRIES:
                continue
            batch = co.get('batch', '')
            # Skip YC batch entries — tratar como aceleração, não rodada VC
            if batch and re.match(r'^[WS]\d{2}$', batch):
                continue
            name = co.get('name', '')
            if not name:
                continue
            sector = map_sector(co.get('tags', []))
            website = co.get('website', None)
            domain = website.replace('https://', '').replace('http://', '').split('/')[0] if website else None
            logo_url = f"https://logo.clearbit.com/{domain}" if domain else None
            results.append({
                "company_name": name,
                "description": co.get('one_liner', None),
                "sector": sector,
                "headquarters": None,
                "country": COUNTRY_PT.get(country, country),
                "founded_year": co.get('founded_date', None),
                "round_type": None,
                "round_amount_usd": 0,
                "round_amount_original": None,
                "lead_investors": ["Y Combinator"],
                "other_investors": [],
                "founders": [],
                "founder_linkedin_urls": [],
                "date": None,
                "linkedin_url": None,
                "website_url": website,
                "twitter_url": None,
                "logo_url": logo_url,
                "source_url": co.get('url', f"https://www.ycombinator.com/companies/{name.lower().replace(' ', '-')}"),
                "source_name": "Y Combinator",
                "verified": False,
                "data_quality_note": "YC company — sem valor de rodada confirmado",
                "sources_count": 1,
                "confidence_score": 0.3
            })
    except Exception as e:
        print(f"[yc] erro: {e}")
    import re
    os.makedirs(".tmp", exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[yc] {len(results)} empresas LATAM encontradas")
    return results

if __name__ == "__main__":
    import re
    scrape()
