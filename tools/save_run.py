"""
save_run.py
Salva dados da run atual em data/runs/ e atualiza data/latest.json.
"""
import json, os
from datetime import datetime, timezone
from collections import Counter

TMP = ".tmp"
MERGED = os.path.join(TMP, "merged.json")
RUNS_DIR = os.path.join("data", "runs")
LATEST = os.path.join("data", "latest.json")


def fmt_usd(n):
    if not n: return "N/D"
    if n >= 1e9: return f"${n/1e9:.1f}B"
    if n >= 1e6: return f"${n/1e6:.0f}M"
    return f"${n:,.0f}"


def save():
    with open(MERGED, encoding='utf-8') as f:
        deals = json.load(f)

    ts = datetime.now(timezone.utc)
    run_id = ts.strftime('%Y-%m-%d_%H-%M')
    os.makedirs(RUNS_DIR, exist_ok=True)

    # Salva JSON completo
    run_json = os.path.join(RUNS_DIR, f"{run_id}.json")
    with open(run_json, "w", encoding="utf-8") as f:
        json.dump({
            "run_id": run_id,
            "generated_at": ts.isoformat(),
            "total_deals": len(deals),
            "total_capital_usd": sum(d.get('round_amount_usd', 0) for d in deals),
            "deals": deals
        }, f, ensure_ascii=False, indent=2)

    # Salva MD resumo
    total_capital = sum(d.get('round_amount_usd', 0) for d in deals)
    countries = Counter(d.get('country') for d in deals if d.get('country'))
    sectors = Counter(d.get('sector') for d in deals if d.get('sector'))
    sources = Counter(d.get('source_name') for d in deals if d.get('source_name'))
    top_deals = sorted(deals, key=lambda d: d.get('round_amount_usd', 0), reverse=True)[:5]

    md_lines = [
        f"# LATAM VC Radar — Run {run_id}",
        f"**Gerado em:** {ts.strftime('%d/%m/%Y %H:%M')} UTC",
        f"**Total de deals:** {len(deals)}",
        f"**Capital total:** {fmt_usd(total_capital)}",
        "",
        "## Top 5 Deals",
    ]
    for d in top_deals:
        investors = ', '.join((d.get('lead_investors') or [])[:2])
        md_lines.append(f"- **{d['company_name']}** — {fmt_usd(d.get('round_amount_usd',0))} {d.get('round_type','')} ({d.get('country','')}) · {investors}")
    md_lines += [
        "",
        "## Países",
        *[f"- {k}: {v} deals" for k, v in countries.most_common()],
        "",
        "## Setores",
        *[f"- {k}: {v} deals" for k, v in sectors.most_common()],
        "",
        "## Fontes Ativas",
        *[f"- {k}: {v} deals" for k, v in sources.most_common()],
    ]
    run_md = os.path.join(RUNS_DIR, f"{run_id}.md")
    with open(run_md, "w", encoding="utf-8") as f:
        f.write('\n'.join(md_lines))

    # Compara com última run
    if os.path.exists(LATEST):
        try:
            with open(LATEST, encoding='utf-8') as f:
                prev = json.load(f)
            prev_names = {d['company_name'] for d in prev.get('deals', [])}
            curr_names = {d['company_name'] for d in deals}
            new_companies = curr_names - prev_names
            if new_companies:
                print(f"[save_run] {len(new_companies)} novas empresas detectadas: {', '.join(list(new_companies)[:5])}")
        except:
            pass

    # Atualiza latest.json
    with open(LATEST, "w", encoding="utf-8") as f:
        json.dump({
            "run_id": run_id,
            "generated_at": ts.isoformat(),
            "total_deals": len(deals),
            "total_capital_usd": total_capital,
            "deals": deals
        }, f, ensure_ascii=False, indent=2)

    print(f"[save_run] Run {run_id} salva. {len(deals)} deals, {fmt_usd(total_capital)} total.")


if __name__ == "__main__":
    save()
