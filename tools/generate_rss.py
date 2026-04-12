"""
generate_rss.py
Gera RSS 2.0 e API JSON pública.
"""
import json, os, re
from datetime import datetime, timezone

TMP = ".tmp"
MERGED = os.path.join(TMP, "merged.json")
RSS_OUT = os.path.join("public", "api", "rss.xml")
JSON_OUT = os.path.join("public", "api", "deals.json")


def fmt_usd(n):
    if not n or n == 0: return "N/D"
    if n >= 1e9: return f"${n/1e9:.1f}B"
    if n >= 1e6: return f"${n/1e6:.0f}M"
    return f"${n:,.0f}"


def escape_xml(s):
    if not s: return ''
    return (s.replace('&', '&amp;')
             .replace('<', '&lt;')
             .replace('>', '&gt;')
             .replace('"', '&quot;')
             .replace("'", '&apos;'))


def generate():
    with open(MERGED, encoding='utf-8') as f:
        deals = json.load(f)

    # Ordena por valor e pega top 20 para RSS
    top_deals = sorted(
        [d for d in deals if d.get('round_amount_usd', 0) > 0],
        key=lambda d: d.get('round_amount_usd', 0),
        reverse=True
    )[:20]

    now_rfc = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')

    # RSS
    items = []
    for d in top_deals:
        investors = ', '.join((d.get('lead_investors') or []) + (d.get('other_investors') or []))[:80]
        founders = ', '.join(d.get('founders') or [])
        desc = f"{fmt_usd(d.get('round_amount_usd',0))} · {d.get('round_type','')} · {d.get('country','')} · Investidores: {investors}"
        if founders:
            desc += f" · Fundadores: {founders}"
        if d.get('description'):
            desc += f" | {d['description'][:200]}"
        pub_date = now_rfc
        if d.get('date'):
            try:
                dt = datetime.strptime(str(d['date'])[:10], '%Y-%m-%d').replace(tzinfo=timezone.utc)
                pub_date = dt.strftime('%a, %d %b %Y %H:%M:%S +0000')
            except:
                pass
        items.append(f"""    <item>
      <title>{escape_xml(d.get('company_name',''))} — {escape_xml(fmt_usd(d.get('round_amount_usd',0)))} {escape_xml(d.get('round_type',''))}</title>
      <link>{escape_xml(d.get('source_url','https://latam-vc-radar.vercel.app'))}</link>
      <description>{escape_xml(desc)}</description>
      <pubDate>{pub_date}</pubDate>
      <guid isPermaLink="false">latam-vc-{escape_xml(d.get('company_name','').lower().replace(' ','-'))}-{str(d.get('date',''))[:10]}</guid>
      <category>{escape_xml(d.get('sector',''))}</category>
    </item>""")

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>LATAM VC Radar — Rodadas de Investimento</title>
    <link>https://latam-vc-radar.vercel.app</link>
    <description>Rodadas de investimento em startups da América Latina, atualizadas diariamente.</description>
    <language>pt-br</language>
    <lastBuildDate>{now_rfc}</lastBuildDate>
    <atom:link href="https://latam-vc-radar.vercel.app/api/rss.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(items)}
  </channel>
</rss>"""

    os.makedirs(os.path.dirname(RSS_OUT), exist_ok=True)
    with open(RSS_OUT, "w", encoding="utf-8") as f:
        f.write(rss)
    print(f"[rss] RSS gerado com {len(top_deals)} deals → {RSS_OUT}")

    # API JSON
    api_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_deals": len(deals),
        "total_capital_usd": sum(d.get('round_amount_usd', 0) for d in deals),
        "countries": list(set(d.get('country') for d in deals if d.get('country'))),
        "deals": deals
    }
    with open(JSON_OUT, "w", encoding="utf-8") as f:
        json.dump(api_payload, f, ensure_ascii=False, indent=2)
    print(f"[api] deals.json gerado com {len(deals)} deals → {JSON_OUT}")


if __name__ == "__main__":
    generate()
