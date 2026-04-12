"""
apply_research.py
Aplica dados verificados do research_results.json no dataset merged.
"""
import json, os

TMP = ".tmp"
MERGED = os.path.join(TMP, "merged.json")
RESEARCH = os.path.join(TMP, "research_results.json")


def apply():
    if not os.path.exists(RESEARCH):
        print("[apply_research] Sem research_results.json — pulando.")
        return

    with open(MERGED, encoding='utf-8') as f:
        deals = json.load(f)
    with open(RESEARCH, encoding='utf-8') as f:
        research = json.load(f)

    applied = 0
    for deal in deals:
        name = deal.get('company_name', '')
        if name not in research:
            continue
        r = research[name]
        changed = False
        # Founders: preenche se vazio
        if not deal.get('founders') and r.get('founders'):
            deal['founders'] = r['founders']
            changed = True
        # Description: preenche se vazio ou muito curta
        if (not deal.get('description') or len(deal.get('description', '')) < 30) and r.get('description'):
            deal['description'] = r['description']
            changed = True
        # Investors: enriquece
        if r.get('lead_investors'):
            existing = deal.get('lead_investors', [])
            new_investors = [i for i in r['lead_investors'] if i not in existing]
            if new_investors:
                deal['lead_investors'] = (existing + new_investors)[:5]
                changed = True
        # Website
        if not deal.get('website_url') and r.get('website_url'):
            deal['website_url'] = r['website_url']
            changed = True
        # LinkedIn
        if not deal.get('linkedin_url') and r.get('linkedin_url'):
            deal['linkedin_url'] = r['linkedin_url']
            changed = True
        if changed:
            deal['verified'] = True
            applied += 1
            # Recalcula confidence score
            from merge_and_normalize import score_deal
            deal['confidence_score'] = score_deal(deal)

    with open(MERGED, "w", encoding="utf-8") as f:
        json.dump(deals, f, ensure_ascii=False, indent=2)

    print(f"[apply_research] Research aplicado em {applied}/{len(deals)} deals.")


if __name__ == "__main__":
    apply()
