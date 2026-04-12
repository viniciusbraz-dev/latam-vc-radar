"""
merge_and_normalize.py
Faz merge de todos os scrapers, normaliza campos e remove duplicatas com fuzzy matching.
"""
import json, os, re, glob
from datetime import datetime, timedelta
from unicodedata import normalize as unorm

TMP = ".tmp"
OUTPUT = os.path.join(TMP, "merged.json")
ROLLING_DAYS = 365

SOURCE_PRIORITY = {
    "Seed Data": 10,
    "startups.com.br": 9,
    "LatamList": 8,
    "Bloomberg Línea BR": 7,
    "LAVCA": 7,
    "Latam Republic": 6,
    "Techloy": 6,
    "Cuántico VP": 5,
    "Distrito": 5,
    "Google News RSS": 4,
    "Y Combinator": 3,
    "Crunchbase": 3,
    "Wellfound": 2,
    "Dealroom": 2,
    "Tracxn": 2,
    "Product Hunt": 1,
}

ROUND_NORMALIZE = {
    "pre-seed": "Pre-Seed", "pré-seed": "Pre-Seed", "pre seed": "Pre-Seed",
    "seed": "Seed",
    "series a": "Series A", "série a": "Series A", "series-a": "Series A",
    "series b": "Series B", "série b": "Series B",
    "series c": "Series C", "série c": "Series C",
    "series d": "Series D", "série d": "Series D",
    "series e": "Series E", "série e": "Series E",
    "series f": "Series F", "série f": "Series F",
    "growth": "Growth", "growth equity": "Growth",
    "ipo": "IPO", "ipo/listing": "IPO",
    "secondary": "Secondary",
    "debt": "Debt",
    "grant": "Grant",
    "corporate": "Corporate Round",
    "follow-on": "Follow-on",
}

NOISE_NAMES = {
    'startup', 'startups', 'fintech', 'tech', 'empresa', 'company',
    'startup brasileira', 'startup latina', 'nova startup', 'a startup',
    'the startup', 'uma startup',
}

NOISE_FOUNDERS = {
    'fundada', 'founded', 'ceo', 'cto', 'cfo', 'co-founder', 'cofundador',
    'editor', 'reporter', 'journalist', 'redator', 'correspondente',
    'são paulo', 'rio de janeiro', 'brasília', 'cidade', 'city', 'país',
    'navigation', 'menu', 'search', 'home', 'about', 'contact',
}

BRL_TO_USD = 5.5


def slugify(s):
    """Normaliza string para comparação fuzzy."""
    s = unorm('NFKD', s.lower()).encode('ascii', 'ignore').decode()
    s = re.sub(r'[^a-z0-9]', '', s)
    return s


def normalize_round(round_str):
    if not round_str:
        return None
    r = round_str.lower().strip()
    for k, v in ROUND_NORMALIZE.items():
        if k in r:
            return v
    return round_str.title()


def normalize_amount(deal):
    """Garante que round_amount_usd está em USD numérico."""
    amt = deal.get('round_amount_usd', 0)
    orig = deal.get('round_amount_original', '')
    if amt and amt > 0:
        return amt
    if orig:
        m = re.search(r'R\$\s*([\d,.]+)\s*(M|mi|B|bi)?', orig, re.IGNORECASE)
        if m:
            val = float(m.group(1).replace('.', '').replace(',', '.'))
            s = (m.group(2) or '').lower()
            if s.startswith('b'): val *= 1_000_000_000
            elif s.startswith('m'): val *= 1_000_000
            return round(val / BRL_TO_USD)
        m = re.search(r'USD?\s*([\d,.]+)\s*(M|B)?', orig, re.IGNORECASE)
        if m:
            val = float(m.group(1).replace(',', ''))
            s = (m.group(2) or '').upper()
            if s == 'B': val *= 1_000_000_000
            elif s == 'M': val *= 1_000_000
            return round(val)
    return 0


def is_noise_name(name):
    return slugify(name) in {slugify(n) for n in NOISE_NAMES} or len(name.strip()) < 3


def clean_founders(founders):
    if not founders:
        return []
    clean = []
    for f in founders:
        f = f.strip()
        if not f or len(f) < 3:
            continue
        if any(noise in f.lower() for noise in NOISE_FOUNDERS):
            continue
        if re.match(r'^[\d\s\-/]+$', f):
            continue
        if len(f.split()) > 5:
            continue
        clean.append(f)
    return clean


def detect_country_from_hq(hq):
    if not hq:
        return None
    CITIES = {
        'são paulo': 'Brasil', 'rio de janeiro': 'Brasil', 'brasília': 'Brasil',
        'belo horizonte': 'Brasil', 'curitiba': 'Brasil', 'florianópolis': 'Brasil',
        'ciudad de méxico': 'México', 'guadalajara': 'México', 'monterrey': 'México',
        'buenos aires': 'Argentina', 'córdoba': 'Argentina', 'rosario': 'Argentina',
        'bogotá': 'Colômbia', 'medellín': 'Colômbia', 'cali': 'Colômbia',
        'santiago': 'Chile', 'valparaíso': 'Chile',
        'lima': 'Peru', 'arequipa': 'Peru',
        'quito': 'Equador', 'guayaquil': 'Equador',
        'montevideo': 'Uruguai',
        'san josé': 'Costa Rica',
        'ciudad de panamá': 'Panamá',
    }
    hq_lower = hq.lower()
    for city, country in CITIES.items():
        if city in hq_lower:
            return country
    COUNTRIES = {
        'brasil': 'Brasil', 'brazil': 'Brasil',
        'méxico': 'México', 'mexico': 'México',
        'argentina': 'Argentina',
        'colombia': 'Colômbia', 'colômbia': 'Colômbia',
        'chile': 'Chile',
        'peru': 'Peru',
        'equador': 'Equador', 'ecuador': 'Equador',
        'uruguai': 'Uruguai', 'uruguay': 'Uruguai',
    }
    for k, v in COUNTRIES.items():
        if k in hq_lower:
            return v
    return None


def score_deal(deal):
    score = 0.0
    if deal.get('company_name'): score += 0.1
    if deal.get('description'): score += 0.15
    if deal.get('sector'): score += 0.05
    if deal.get('country'): score += 0.05
    if deal.get('round_type'): score += 0.1
    if deal.get('round_amount_usd', 0) > 0: score += 0.2
    if deal.get('founders'): score += 0.15
    if deal.get('lead_investors'): score += 0.1
    if deal.get('date'): score += 0.05
    if deal.get('verified'): score += 0.05
    sources = deal.get('sources_count', 1)
    score += min(sources * 0.02, 0.1)
    return round(min(score, 1.0), 2)


def merge():
    all_deals = []
    # Carrega seed
    seed_path = os.path.join(TMP, "seed_deals.json")
    if os.path.exists(seed_path):
        with open(seed_path, encoding='utf-8') as f:
            all_deals.extend(json.load(f))
        print(f"[merge] {len(all_deals)} deals do seed")

    # Carrega todos os scrapers
    for raw_file in glob.glob(os.path.join(TMP, "raw_*.json")):
        try:
            with open(raw_file, encoding='utf-8') as f:
                data = json.load(f)
            all_deals.extend(data)
            print(f"[merge] +{len(data)} de {os.path.basename(raw_file)}")
        except Exception as e:
            print(f"[merge] erro ao ler {raw_file}: {e}")

    # Normaliza cada deal
    normalized = []
    cutoff = (datetime.utcnow() - timedelta(days=ROLLING_DAYS)).strftime('%Y-%m-%d')

    for deal in all_deals:
        name = (deal.get('company_name') or '').strip()
        if not name or is_noise_name(name):
            continue
        # Filtro temporal (Seed Data sempre passa)
        date = deal.get('date')
        if date and len(str(date)) >= 10 and deal.get('source_name') != 'Seed Data':
            if str(date)[:10] < cutoff:
                continue
        # Normaliza campos
        deal['round_type'] = normalize_round(deal.get('round_type'))
        deal['round_amount_usd'] = normalize_amount(deal)
        deal['founders'] = clean_founders(deal.get('founders', []))
        deal['lead_investors'] = [i.strip() for i in (deal.get('lead_investors') or []) if i and len(i.strip()) > 1]
        deal['other_investors'] = [i.strip() for i in (deal.get('other_investors') or []) if i and len(i.strip()) > 1]
        if not deal.get('country') and deal.get('headquarters'):
            deal['country'] = detect_country_from_hq(deal['headquarters'])
        deal['confidence_score'] = score_deal(deal)
        normalized.append(deal)

    # Deduplicação fuzzy por nome
    seen = {}  # slug -> índice no merged
    merged = []

    for deal in sorted(normalized, key=lambda d: SOURCE_PRIORITY.get(d.get('source_name', ''), 0), reverse=True):
        slug = slugify(deal.get('company_name', ''))
        if not slug:
            continue
        if slug in seen:
            idx = seen[slug]
            existing = merged[idx]
            # Merge: preserva campos do existente, preenche lacunas
            for field in ['description', 'sector', 'headquarters', 'country', 'founded_year',
                          'round_type', 'linkedin_url', 'website_url', 'twitter_url', 'logo_url']:
                if not existing.get(field) and deal.get(field):
                    existing[field] = deal[field]
            # Merge investors e founders (sem duplicatas)
            existing['lead_investors'] = list(dict.fromkeys(
                existing.get('lead_investors', []) + deal.get('lead_investors', [])
            ))[:5]
            existing['other_investors'] = list(dict.fromkeys(
                existing.get('other_investors', []) + deal.get('other_investors', [])
            ))[:10]
            existing['founders'] = list(dict.fromkeys(
                existing.get('founders', []) + deal.get('founders', [])
            ))[:5]
            existing['sources_count'] = existing.get('sources_count', 1) + 1
            existing['confidence_score'] = score_deal(existing)
        else:
            seen[slug] = len(merged)
            merged.append(deal)

    os.makedirs(TMP, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"[merge] {len(merged)} deals após deduplicação → {OUTPUT}")
    return merged


if __name__ == "__main__":
    merge()
