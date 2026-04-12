"""
deep_clean.py
Remove ruído, empresas não-LATAM, entradas sem dados substanciais.
"""
import json, os, re

TMP = ".tmp"
INPUT = os.path.join(TMP, "merged.json")
OUTPUT = os.path.join(TMP, "merged.json")

LATAM_COUNTRIES = {
    'Brasil', 'México', 'Argentina', 'Colômbia', 'Chile', 'Peru',
    'Equador', 'Uruguai', 'Costa Rica', 'Panamá', 'Venezuela',
    'Bolívia', 'Paraguai', 'Guatemala', 'República Dominicana', 'Honduras',
    'El Salvador', 'Nicarágua', 'Cuba', 'Jamaica',
}

NON_LATAM_HINTS = [
    'india', 'china', 'usa', 'united states', 'uk', 'united kingdom',
    'germany', 'france', 'singapore', 'nigeria', 'africa', 'kenya',
    'israel', 'australia', 'canada', 'japan', 'korea', 'new york',
    'san francisco', 'london', 'berlin', 'paris',
]

GENERIC_NAMES = {
    'startup', 'fintech', 'tech', 'saas', 'app', 'platform', 'company',
    'empresa', 'plataforma', 'solução', 'solution', 'startup brasileira',
    'nova fintech', 'nova startup', 'unnamed', 'n/a', 'tbd',
}

MIN_DESCRIPTION_LENGTH = 30
YC_BATCH_RE = re.compile(r'^[WS]\d{2}\s')


def is_non_latam(deal):
    """Detecta empresas claramente não-LATAM."""
    country = (deal.get('country') or '').lower()
    hq = (deal.get('headquarters') or '').lower()
    combined = country + ' ' + hq
    if country and deal.get('country') not in LATAM_COUNTRIES:
        # Sem país definido: tudo bem, mantém
        pass
    for hint in NON_LATAM_HINTS:
        if hint in combined:
            return True
    return False


def is_too_noisy(deal):
    """Remove entradas sem valor mínimo de dados."""
    name = (deal.get('company_name') or '').strip().lower()
    if name in GENERIC_NAMES:
        return True
    if len(name) < 2:
        return True
    # Sem amount E sem descrição: descarta
    amount = deal.get('round_amount_usd', 0)
    desc = deal.get('description') or ''
    if amount == 0 and len(desc) < MIN_DESCRIPTION_LENGTH:
        # Exceção: seed data sempre fica
        if deal.get('source_name') == 'Seed Data':
            return False
        return True
    # YC batch noise (W21, S22 etc.) no nome
    if YC_BATCH_RE.match(name):
        return True
    return False


def clean_description(desc):
    if not desc:
        return None
    # Remove HTML tags residuais
    desc = re.sub(r'<[^>]+>', '', desc)
    # Remove múltiplos espaços
    desc = re.sub(r'\s+', ' ', desc).strip()
    # Remove navigation text
    nav_patterns = ['read more', 'leia mais', 'continue reading', 'ver mais', 'saiba mais']
    for p in nav_patterns:
        desc = re.sub(p, '', desc, flags=re.IGNORECASE).strip()
    return desc if len(desc) > 10 else None


def clean():
    with open(INPUT, encoding='utf-8') as f:
        deals = json.load(f)

    before = len(deals)
    cleaned = []

    for deal in deals:
        if is_non_latam(deal):
            continue
        if is_too_noisy(deal):
            continue
        deal['description'] = clean_description(deal.get('description'))
        # Garante campos mínimos
        if 'lead_investors' not in deal:
            deal['lead_investors'] = []
        if 'other_investors' not in deal:
            deal['other_investors'] = []
        if 'founders' not in deal:
            deal['founders'] = []
        if 'founder_linkedin_urls' not in deal:
            deal['founder_linkedin_urls'] = []
        # Sanitiza logo_url (só clearbit ou None)
        logo = deal.get('logo_url')
        if logo and 'clearbit.com' not in logo and not logo.startswith('https://'):
            deal['logo_url'] = None
        cleaned.append(deal)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    removed = before - len(cleaned)
    print(f"[deep_clean] {before} → {len(cleaned)} deals ({removed} removidos)")
    return cleaned


if __name__ == "__main__":
    clean()
