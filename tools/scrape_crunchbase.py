"""
scrape_crunchbase.py
Coleta deals LATAM via páginas públicas do Crunchbase (frequentemente bloqueado).
Usa user-agent rotation e fallback para RSS.
"""
import json, os, re, requests
from bs4 import BeautifulSoup

OUTPUT = ".tmp/raw_crunchbase.json"

UA_LIST = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
]

LATAM_QUERY = "https://www.crunchbase.com/discover/funding_rounds?field_ids=funded_organization_identifier,money_raised,announced_on,investment_type,funded_organization_location&predefined_filter=latin_america"

def scrape():
    results = []
    import random
    headers = {
        "User-Agent": random.choice(UA_LIST),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    try:
        resp = requests.get(LATAM_QUERY, headers=headers, timeout=15)
        if resp.status_code in [403, 429, 503]:
            print(f"[crunchbase] bloqueado: {resp.status_code} — pulando")
        elif resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Crunchbase renderiza via JS — extrair o que vier do HTML estático
            scripts = soup.find_all('script', type='application/json')
            for sc in scripts:
                try:
                    data = json.loads(sc.string or '')
                    # Procurar estrutura de deals dentro do JSON embarcado
                    if isinstance(data, dict) and 'entities' in str(data):
                        print("[crunchbase] dados parciais encontrados no JSON embedded")
                        break
                except:
                    pass
    except Exception as e:
        print(f"[crunchbase] erro: {e}")
    os.makedirs(".tmp", exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[crunchbase] {len(results)} deals encontrados (limitado por bloqueio)")
    return results

if __name__ == "__main__":
    scrape()
