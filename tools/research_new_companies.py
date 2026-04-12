"""
research_new_companies.py
Pesquisa automática de empresas novas via Playwright.
Busca founders, descrição e detalhes no Google + site da empresa + artigo fonte.
"""
import json, os, re, asyncio
from playwright.async_api import async_playwright

TMP = ".tmp"
MERGED = os.path.join(TMP, "merged.json")
RESEARCH = os.path.join(TMP, "research_results.json")

MAX_RESEARCH = 15  # máximo de novas pesquisas por run

FOUNDER_PATTERNS = [
    r'fundad[ao]\s+por\s+([A-ZÁÉÍÓÚÀÂÃÊÔÇ][a-záéíóúàâãêôç]+(?:\s+[A-ZÁÉÍÓÚÀÂÃÊÔÇ][a-záéíóúàâãêôç]+){1,3})',
    r'founded\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
    r'CEO[:\s]+([A-ZÁÉÍÓÚÀÂÃÊÔÇ][a-záéíóúàâãêôç]+(?:\s+[A-ZÁÉÍÓÚÀÂÃÊÔÇ][a-záéíóúàâãêôç]+){1,3})',
    r'cofundador[es]*[:\s]+([A-ZÁÉÍÓÚÀÂÃÊÔÇ][a-záéíóúàâãêôç]+(?:\s+[A-ZÁÉÍÓÚÀÂÃÊÔÇ][a-záéíóúàâãêôç]+){1,3})',
    r'co-founder[s]*[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
    r'founder[s]*[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
]

INVESTOR_PATTERNS = [
    r'liderada?\s+por\s+([A-ZÁÉÍÓÚÀÂÃÊÔÇ][^\,\.]+)',
    r'led\s+by\s+([A-Z][^\,\.]+)',
    r'investidor[es]*[:\s]+([A-ZÁÉÍÓÚÀÂÃÊÔÇ][^\,\.]+)',
    r'investor[s]*[:\s]+([A-Z][^\,\.]+)',
]

def load_research():
    if os.path.exists(RESEARCH):
        with open(RESEARCH, encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_research(data):
    os.makedirs(TMP, exist_ok=True)
    with open(RESEARCH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def extract_founders(text):
    founders = []
    for pattern in FOUNDER_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            m = m.strip().rstrip('.,;:')
            if 2 <= len(m.split()) <= 4 and len(m) > 3:
                founders.append(m)
    return list(dict.fromkeys(founders))[:4]

def extract_investors(text):
    investors = []
    for pattern in INVESTOR_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            m = m.strip().rstrip('.,;:')
            if len(m) > 2 and len(m) < 60:
                investors.append(m)
    return list(dict.fromkeys(investors))[:4]

def extract_description(text, company_name):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    relevant = []
    for sent in sentences:
        if company_name.lower() in sent.lower() and len(sent) > 40:
            relevant.append(sent.strip())
            if len(' '.join(relevant)) > 300:
                break
    if relevant:
        return ' '.join(relevant)[:500]
    return None

async def research_company(page, company_name, source_url):
    result = {
        "company_name": company_name,
        "founders": [],
        "description": None,
        "lead_investors": [],
        "website_url": None,
        "linkedin_url": None,
    }
    try:
        # 1. Busca Google
        query = f"{company_name} startup founders CEO LATAM"
        await page.goto(f"https://www.google.com/search?q={query.replace(' ', '+')}", timeout=15000)
        await page.wait_for_timeout(2000)
        google_text = await page.inner_text('body')

        founders = extract_founders(google_text)
        investors = extract_investors(google_text)
        desc = extract_description(google_text, company_name)
        if founders: result['founders'] = founders
        if investors: result['lead_investors'] = investors
        if desc: result['description'] = desc

        # 2. Visita artigo fonte se disponível
        if source_url and source_url.startswith('http') and 'google' not in source_url:
            try:
                await page.goto(source_url, timeout=12000)
                await page.wait_for_timeout(1500)
                article_text = await page.inner_text('article, main, .content, body')
                founders2 = extract_founders(article_text)
                investors2 = extract_investors(article_text)
                desc2 = extract_description(article_text, company_name)
                result['founders'] = list(dict.fromkeys(result['founders'] + founders2))[:4]
                result['lead_investors'] = list(dict.fromkeys(result['lead_investors'] + investors2))[:4]
                if not result['description'] and desc2:
                    result['description'] = desc2
            except Exception as e:
                print(f"[research] erro no artigo {source_url}: {e}")

        print(f"[research] {company_name}: {len(result['founders'])} founders, desc={'sim' if result['description'] else 'não'}")
    except Exception as e:
        print(f"[research] erro ao pesquisar {company_name}: {e}")
    return result


async def run():
    with open(MERGED, encoding='utf-8') as f:
        deals = json.load(f)

    research_cache = load_research()
    new_companies = [
        d for d in deals
        if d.get('company_name') not in research_cache
        and d.get('source_name') != 'Seed Data'
    ]

    if not new_companies:
        print("[research] Nenhuma empresa nova para pesquisar.")
        return

    to_research = new_companies[:MAX_RESEARCH]
    print(f"[research] Pesquisando {len(to_research)} empresas novas...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        for deal in to_research:
            name = deal['company_name']
            source_url = deal.get('source_url', '')
            result = await research_company(page, name, source_url)
            research_cache[name] = result
            save_research(research_cache)  # salva incrementalmente
        await browser.close()

    print(f"[research] Concluído. Cache agora com {len(research_cache)} empresas.")


def main():
    asyncio.run(run())

if __name__ == "__main__":
    main()
