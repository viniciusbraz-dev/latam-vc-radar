"""
generate_showcase.py
Gera o dashboard HTML single-file com design editorial luxury.
Instrument Serif + DM Sans, tema midnight (#08090d), accent emerald (#00e5a0).
"""
import json, os, re
from datetime import datetime
from collections import Counter, defaultdict
from jinja2 import Template

TMP = ".tmp"
MERGED = os.path.join(TMP, "merged.json")
OUTPUT_TMP = os.path.join(TMP, "showcase.html")
OUTPUT_PUBLIC = os.path.join("public", "index.html")

COUNTRY_COORDS = {
    'Brasil': (-14.2, -51.9),
    'México': (23.6, -102.5),
    'Argentina': (-38.4, -63.6),
    'Colômbia': (4.5, -74.0),
    'Chile': (-35.7, -71.5),
    'Peru': (-9.2, -75.0),
    'Equador': (-1.8, -78.2),
    'Uruguai': (-32.5, -55.8),
    'Costa Rica': (9.7, -83.8),
    'Panamá': (8.5, -80.8),
    'Venezuela': (6.4, -66.6),
    'Bolívia': (-16.3, -63.6),
    'Paraguai': (-23.4, -58.4),
    'Guatemala': (15.8, -90.2),
}

SECTOR_COLORS = {
    'Fintech': '#00e5a0',
    'E-commerce': '#3b82f6',
    'Proptech': '#f59e0b',
    'Healthtech': '#ec4899',
    'Logística': '#8b5cf6',
    'Edtech': '#f97316',
    'Cleantech': '#22c55e',
    'Agtech': '#84cc16',
    'SaaS': '#06b6d4',
    'HR Tech': '#a78bfa',
    'Crypto / Web3': '#fbbf24',
    'Insurtech': '#fb923c',
    'Delivery': '#34d399',
    'Automotive': '#60a5fa',
    'Other': '#6b7280',
}

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="LATAM VC Radar — Rodadas de investimento em startups da América Latina. Dados atualizados diariamente.">
<title>LATAM VC Radar — Investimentos em Startups LATAM</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#08090d;--surface:#0e1117;--surface2:#141720;--border:#1e2332;
  --accent:#00e5a0;--accent2:#00b87a;--text:#e8eaf0;--muted:#6b7280;
  --danger:#ef4444;--warning:#f59e0b;
  --font-serif:'Instrument Serif',Georgia,serif;
  --font-sans:'DM Sans',system-ui,sans-serif;
  --radius:12px;--radius-sm:8px;
}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);font-family:var(--font-sans);font-size:15px;line-height:1.6;min-height:100vh;overflow-x:hidden}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
img{display:block;max-width:100%}

/* HEADER */
.site-header{position:sticky;top:0;z-index:100;background:rgba(8,9,13,0.92);backdrop-filter:blur(16px);border-bottom:1px solid var(--border);padding:0 2rem}
.header-inner{max-width:1400px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:60px}
.logo{font-family:var(--font-serif);font-size:1.25rem;color:var(--accent);letter-spacing:-0.01em}
.logo span{color:var(--muted);font-size:.85rem;font-family:var(--font-sans);font-weight:300;margin-left:.5rem}
.header-meta{display:flex;align-items:center;gap:1rem}
.live-badge{display:flex;align-items:center;gap:.4rem;font-size:.75rem;color:var(--accent);font-weight:500;text-transform:uppercase;letter-spacing:.08em}
.live-dot{width:6px;height:6px;background:var(--accent);border-radius:50%;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.5;transform:scale(1.3)}}

/* HERO */
.hero{max-width:1400px;margin:0 auto;padding:5rem 2rem 3rem}
.hero-label{font-size:.75rem;font-weight:500;text-transform:uppercase;letter-spacing:.12em;color:var(--accent);margin-bottom:1.2rem}
.hero-headline{font-family:var(--font-serif);font-size:clamp(2.5rem,5vw,4rem);line-height:1.1;letter-spacing:-0.02em;max-width:700px;margin-bottom:2rem}
.hero-headline em{font-style:italic;color:var(--accent)}
.hero-sub{color:var(--muted);font-size:1rem;max-width:500px;margin-bottom:3rem}
.bar-chart-wrap{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.5rem 2rem;overflow:hidden}
.bar-chart-title{font-size:.75rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:1.5rem}
.bars{display:flex;align-items:flex-end;gap:6px;height:80px}
.bar{flex:1;background:linear-gradient(180deg,var(--accent),var(--accent2));border-radius:4px 4px 0 0;opacity:.85;transition:opacity .2s;position:relative;min-width:0}
.bar:hover{opacity:1}
.bar-label{position:absolute;bottom:-1.4rem;left:50%;transform:translateX(-50%);font-size:.65rem;color:var(--muted);white-space:nowrap}
.bar-months{margin-top:2.2rem;display:flex;justify-content:space-between}

/* STAT CARDS */
.stats-row{max-width:1400px;margin:0 auto;padding:0 2rem 3rem;display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}
@media(max-width:900px){.stats-row{grid-template-columns:repeat(2,1fr)}}
@media(max-width:500px){.stats-row{grid-template-columns:1fr}}
.stat-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.5rem;position:relative;overflow:hidden}
.stat-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,var(--accent),transparent)}
.stat-label{font-size:.7rem;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);margin-bottom:.5rem}
.stat-value{font-family:var(--font-serif);font-size:2.2rem;line-height:1;color:var(--accent);margin-bottom:.25rem}
.stat-desc{font-size:.75rem;color:var(--muted)}

/* CHARTS */
.charts-row{max-width:1400px;margin:0 auto;padding:0 2rem 3rem;display:grid;grid-template-columns:1fr 1fr;gap:1.5rem}
@media(max-width:800px){.charts-row{grid-template-columns:1fr}}
.chart-box{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.5rem}
.chart-title{font-size:.75rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:1.5rem}
.sector-bars{display:flex;flex-direction:column;gap:.6rem}
.sector-row{display:flex;align-items:center;gap:.75rem}
.sector-name{font-size:.8rem;color:var(--text);min-width:100px;text-align:right}
.sector-bar-wrap{flex:1;background:var(--surface2);border-radius:4px;height:20px;overflow:hidden}
.sector-bar-fill{height:100%;border-radius:4px;transition:width .8s ease}
.sector-amount{font-size:.75rem;color:var(--muted);min-width:60px;text-align:right}

/* MAP */
.map-section{max-width:1400px;margin:0 auto;padding:0 2rem 3rem}
.map-title{font-family:var(--font-serif);font-size:1.5rem;margin-bottom.5rem;margin-bottom:.5rem}
.map-subtitle{color:var(--muted);font-size:.85rem;margin-bottom:1.5rem}
.map-wrap{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.5rem;overflow:hidden}
.latam-map{width:100%;max-width:500px;margin:0 auto;display:block}
.map-bubble{cursor:pointer;transition:all .2s}
.map-bubble:hover circle{opacity:1!important;filter:drop-shadow(0 0 8px var(--accent))}
.map-bubble text{fill:var(--text);font-family:var(--font-sans);font-weight:600;pointer-events:none}

/* LEADERBOARD */
.leaderboard{max-width:1400px;margin:0 auto;padding:0 2rem 3rem}
.section-title{font-family:var(--font-serif);font-size:1.5rem;margin-bottom:.5rem}
.section-sub{color:var(--muted);font-size:.85rem;margin-bottom:1.5rem}
.lb-table{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden}
.lb-row{display:flex;align-items:center;padding:.9rem 1.5rem;border-bottom:1px solid var(--border);cursor:pointer;transition:background .15s}
.lb-row:last-child{border-bottom:none}
.lb-row:hover,.lb-row.active{background:var(--surface2)}
.lb-rank{font-family:var(--font-serif);font-size:1.1rem;color:var(--muted);min-width:2rem}
.lb-name{flex:1;font-weight:500;font-size:.9rem}
.lb-deals{font-size:.8rem;color:var(--muted);margin-right:1rem}
.lb-bar-wrap{width:120px;background:var(--surface2);height:6px;border-radius:3px;overflow:hidden}
.lb-bar-fill{height:100%;background:var(--accent);border-radius:3px;transition:width .6s ease}

/* FILTERS */
.filters-section{position:sticky;top:60px;z-index:90;background:rgba(8,9,13,0.95);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);padding:.75rem 0}
.filters-inner{max-width:1400px;margin:0 auto;padding:0 2rem;display:flex;align-items:center;gap:1rem;flex-wrap:wrap}
.filter-label{font-size:.7rem;text-transform:uppercase;letter-spacing:.1em;color:var(--muted)}
.stage-pills{display:flex;gap:.4rem;flex-wrap:wrap}
.pill{background:var(--surface);border:1px solid var(--border);border-radius:20px;padding:.3rem .8rem;font-size:.75rem;cursor:pointer;transition:all .2s;white-space:nowrap;color:var(--muted)}
.pill:hover,.pill.active{background:var(--accent);border-color:var(--accent);color:#000;font-weight:500}
.search-wrap{flex:1;min-width:200px;position:relative}
.search-input{width:100%;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-sm);padding:.4rem 1rem .4rem 2.2rem;font-size:.85rem;color:var(--text);font-family:var(--font-sans);outline:none;transition:border-color .2s}
.search-input:focus{border-color:var(--accent)}
.search-icon{position:absolute;left:.7rem;top:50%;transform:translateY(-50%);color:var(--muted);font-size:.9rem}
.time-select,.sort-select{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-sm);padding:.4rem .8rem;font-size:.75rem;color:var(--text);font-family:var(--font-sans);cursor:pointer;outline:none}

/* GRID */
.deals-section{max-width:1400px;margin:0 auto;padding:1.5rem 2rem 4rem}
.deals-count{font-size:.8rem;color:var(--muted);margin-bottom:1.5rem}
.deals-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:1.25rem}
@media(max-width:600px){.deals-grid{grid-template-columns:1fr}}

.deal-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.25rem;cursor:pointer;transition:all .25s;opacity:0;transform:translateY(20px)}
.deal-card.visible{opacity:1;transform:translateY(0)}
.deal-card:hover{border-color:var(--accent);transform:translateY(-3px);box-shadow:0 8px 30px rgba(0,229,160,.1)}
.card-header{display:flex;align-items:flex-start;gap:.75rem;margin-bottom:.8rem}
.card-logo{width:40px;height:40px;border-radius:8px;background:var(--surface2);border:1px solid var(--border);overflow:hidden;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-family:var(--font-serif);font-size:1.1rem;color:var(--accent)}
.card-logo img{width:100%;height:100%;object-fit:cover}
.card-name{font-weight:600;font-size:.95rem;line-height:1.3;flex:1}
.card-country{font-size:.7rem;color:var(--muted)}
.card-desc{font-size:.8rem;color:var(--muted);line-height:1.5;margin-bottom:.8rem;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.card-meta{display:flex;align-items:center;gap:.5rem;flex-wrap:wrap;margin-bottom:.75rem}
.badge{display:inline-flex;align-items:center;gap:.25rem;padding:.2rem .55rem;border-radius:20px;font-size:.68rem;font-weight:500;letter-spacing:.02em}
.badge-round{background:rgba(0,229,160,.12);color:var(--accent);border:1px solid rgba(0,229,160,.2)}
.badge-sector{background:var(--surface2);color:var(--muted);border:1px solid var(--border)}
.card-amount{font-family:var(--font-serif);font-size:1.3rem;color:var(--text);margin-bottom:.5rem}
.card-amount-sub{font-size:.7rem;color:var(--muted)}
.card-investors{font-size:.75rem;color:var(--muted);margin-bottom:.6rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.card-founders{display:flex;gap:.3rem;flex-wrap:wrap}
.founder-pill{background:var(--surface2);border:1px solid var(--border);border-radius:20px;padding:.15rem .5rem;font-size:.68rem;color:var(--muted);cursor:pointer;transition:all .15s}
.founder-pill:hover{border-color:var(--accent);color:var(--accent)}
.card-footer{display:flex;align-items:center;justify-content:space-between;margin-top:.75rem;padding-top:.75rem;border-top:1px solid var(--border)}
.card-date{font-size:.7rem;color:var(--muted)}
.card-confidence{display:flex;align-items:center;gap:.3rem;font-size:.65rem;color:var(--muted)}
.confidence-dot{width:6px;height:6px;border-radius:50%;background:var(--muted)}
.confidence-dot.high{background:var(--accent)}
.confidence-dot.med{background:var(--warning)}
.confidence-dot.low{background:var(--muted)}

/* MODAL */
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.8);backdrop-filter:blur(4px);z-index:200;display:none;align-items:center;justify-content:center;padding:1rem}
.modal-overlay.open{display:flex}
.modal{background:var(--surface);border:1px solid var(--border);border-radius:16px;max-width:600px;width:100%;max-height:90vh;overflow-y:auto;padding:2rem;position:relative}
.modal-close{position:absolute;top:1rem;right:1rem;background:var(--surface2);border:1px solid var(--border);border-radius:50%;width:32px;height:32px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:1rem;color:var(--muted);transition:all .15s}
.modal-close:hover{background:var(--border);color:var(--text)}
.modal-logo{width:56px;height:56px;border-radius:12px;background:var(--surface2);border:1px solid var(--border);overflow:hidden;margin-bottom:1rem;display:flex;align-items:center;justify-content:center;font-family:var(--font-serif);font-size:1.5rem;color:var(--accent)}
.modal-logo img{width:100%;height:100%;object-fit:cover}
.modal-name{font-family:var(--font-serif);font-size:1.75rem;margin-bottom:.25rem}
.modal-country{font-size:.8rem;color:var(--muted);margin-bottom:1.25rem}
.modal-section{margin-bottom:1.25rem}
.modal-section-label{font-size:.65rem;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);margin-bottom:.4rem}
.modal-desc{font-size:.9rem;line-height:1.65;color:var(--text)}
.modal-amount{font-family:var(--font-serif);font-size:2rem;color:var(--accent)}
.modal-amount-sub{font-size:.8rem;color:var(--muted)}
.modal-badges{display:flex;flex-wrap:wrap;gap:.4rem}
.modal-investors{display:flex;flex-wrap:wrap;gap:.4rem}
.investor-tag{background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius-sm);padding:.25rem .6rem;font-size:.78rem}
.modal-founders{display:flex;flex-wrap:wrap;gap:.4rem}
.founder-link{background:rgba(0,229,160,.08);border:1px solid rgba(0,229,160,.2);border-radius:var(--radius-sm);padding:.3rem .7rem;font-size:.8rem;color:var(--accent);transition:all .15s}
.founder-link:hover{background:rgba(0,229,160,.15)}
.modal-links{display:flex;gap:.75rem;flex-wrap:wrap;margin-top:1rem}
.modal-link{display:flex;align-items:center;gap:.3rem;font-size:.8rem;color:var(--muted);transition:color .15s}
.modal-link:hover{color:var(--accent)}

/* FOOTER */
.site-footer{border-top:1px solid var(--border);padding:2rem;text-align:center}
.footer-inner{max-width:1400px;margin:0 auto}
.footer-stats{display:flex;justify-content:center;gap:2rem;margin-bottom.5rem;margin-bottom:.75rem;flex-wrap:wrap}
.footer-stat{font-size:.8rem;color:var(--muted)}
.footer-stat strong{color:var(--text)}
.footer-copy{font-size:.75rem;color:var(--muted)}

/* EMPTY STATE */
.empty-state{text-align:center;padding:4rem 2rem;color:var(--muted)}
.empty-state h3{font-family:var(--font-serif);font-size:1.5rem;margin-bottom:.5rem;color:var(--text)}

/* SCROLL ANIMATIONS */
@keyframes fadeInUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
.fade-in{animation:fadeInUp .6s ease forwards}

/* DONUT */
.donut-wrap{display:flex;align-items:center;gap:2rem;flex-wrap:wrap}
.donut-svg{flex-shrink:0}
.donut-legend{display:flex;flex-direction:column;gap:.4rem}
.legend-item{display:flex;align-items:center;gap:.5rem;font-size:.78rem;color:var(--muted);cursor:pointer}
.legend-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
</style>
</head>
<body>

<!-- HEADER -->
<header class="site-header">
  <div class="header-inner">
    <div class="logo">LATAM VC Radar <span>{{ date_range }}</span></div>
    <div class="header-meta">
      <div class="live-badge"><span class="live-dot"></span> Live</div>
      <a href="/api/deals.json" style="font-size:.75rem;color:var(--muted)">API JSON</a>
      <a href="/api/rss.xml" style="font-size:.75rem;color:var(--muted)">RSS</a>
    </div>
  </div>
</header>

<!-- HERO -->
<section class="hero">
  <div class="hero-label">Inteligência de Mercado · América Latina</div>
  <h1 class="hero-headline">O capital está fluindo<br>para o <em>ecossistema LATAM</em></h1>
  <p class="hero-sub">Rastreamos rodadas de investimento em startups da América Latina em tempo real — fundadores, investidores e setores, tudo em um só lugar.</p>
  <div class="bar-chart-wrap">
    <div class="bar-chart-title">Capital por mês (USD)</div>
    <div class="bars" id="heroBarChart">
      {% for month_data in monthly_data %}
      <div class="bar" style="height:{{ month_data.pct }}%" title="{{ month_data.label }}: ${{ month_data.total_fmt }}">
        <span class="bar-label">{{ month_data.short }}</span>
      </div>
      {% endfor %}
    </div>
    <div class="bar-months"></div>
  </div>
</section>

<!-- STAT CARDS -->
<section class="stats-row">
  <div class="stat-card fade-in">
    <div class="stat-label">Total de Deals</div>
    <div class="stat-value" id="statDeals" data-target="{{ total_deals }}">0</div>
    <div class="stat-desc">rodadas rastreadas</div>
  </div>
  <div class="stat-card fade-in" style="animation-delay:.1s">
    <div class="stat-label">Capital Total</div>
    <div class="stat-value" id="statCapital" data-target="{{ total_capital_m }}">0</div>
    <div class="stat-desc">bilhões USD investidos</div>
  </div>
  <div class="stat-card fade-in" style="animation-delay:.2s">
    <div class="stat-label">Deal Médio</div>
    <div class="stat-value" id="statAvg" data-target="{{ avg_deal_m }}">0</div>
    <div class="stat-desc">milhões USD por rodada</div>
  </div>
  <div class="stat-card fade-in" style="animation-delay:.3s">
    <div class="stat-label">Países</div>
    <div class="stat-value" id="statCountries" data-target="{{ countries_count }}">0</div>
    <div class="stat-desc">países com startups trackeadas</div>
  </div>
</section>

<!-- CHARTS ROW -->
<section class="charts-row">
  <!-- Capital por Setor -->
  <div class="chart-box">
    <div class="chart-title">Capital por Setor</div>
    <div class="sector-bars">
      {% for s in sector_capital %}
      <div class="sector-row">
        <div class="sector-name">{{ s.name }}</div>
        <div class="sector-bar-wrap">
          <div class="sector-bar-fill" style="width:{{ s.pct }}%;background:{{ s.color }}"></div>
        </div>
        <div class="sector-amount">${{ s.amount_fmt }}</div>
      </div>
      {% endfor %}
    </div>
  </div>
  <!-- Deals por País (Donut) -->
  <div class="chart-box">
    <div class="chart-title">Deals por País</div>
    <div class="donut-wrap">
      <svg class="donut-svg" width="140" height="140" viewBox="0 0 140 140">
        {% for seg in donut_segments %}
        <circle cx="70" cy="70" r="54" fill="transparent"
          stroke="{{ seg.color }}" stroke-width="22"
          stroke-dasharray="{{ seg.dash }} {{ seg.gap }}"
          stroke-dashoffset="{{ seg.offset }}"
          style="cursor:pointer"
          onclick="filterByCountry('{{ seg.country }}')"
          title="{{ seg.country }}: {{ seg.count }} deals">
          <title>{{ seg.country }}: {{ seg.count }} deals</title>
        </circle>
        {% endfor %}
        <text x="70" y="66" text-anchor="middle" fill="var(--text)" font-family="Instrument Serif" font-size="22">{{ total_deals }}</text>
        <text x="70" y="82" text-anchor="middle" fill="var(--muted)" font-size="9" font-family="DM Sans">deals</text>
      </svg>
      <div class="donut-legend">
        {% for seg in donut_segments[:8] %}
        <div class="legend-item" onclick="filterByCountry('{{ seg.country }}')">
          <div class="legend-dot" style="background:{{ seg.color }}"></div>
          <span>{{ seg.country }} <strong style="color:var(--text)">{{ seg.count }}</strong></span>
        </div>
        {% endfor %}
      </div>
    </div>
  </div>
</section>

<!-- LEADERBOARD -->
<section class="leaderboard">
  <h2 class="section-title">Top Investidores</h2>
  <p class="section-sub">VCs mais ativos no ecossistema LATAM</p>
  <div class="lb-table">
    {% for inv in top_investors %}
    <div class="lb-row" onclick="filterByInvestor('{{ inv.name }}')" title="Filtrar por {{ inv.name }}">
      <div class="lb-rank">{{ loop.index }}</div>
      <div class="lb-name">{{ inv.name }}</div>
      <div class="lb-deals">{{ inv.deals }} deal{{ 's' if inv.deals > 1 else '' }}</div>
      <div class="lb-bar-wrap">
        <div class="lb-bar-fill" style="width:{{ inv.pct }}%"></div>
      </div>
    </div>
    {% endfor %}
  </div>
</section>

<!-- FILTERS -->
<div class="filters-section" id="filtersBar">
  <div class="filters-inner">
    <span class="filter-label">Estágio</span>
    <div class="stage-pills" id="stagePills">
      <div class="pill active" data-stage="all" onclick="filterStage('all',this)">Todos</div>
      <div class="pill" data-stage="Pre-Seed" onclick="filterStage('Pre-Seed',this)">Pre-Seed</div>
      <div class="pill" data-stage="Seed" onclick="filterStage('Seed',this)">Seed</div>
      <div class="pill" data-stage="Series A" onclick="filterStage('Series A',this)">Series A</div>
      <div class="pill" data-stage="Series B" onclick="filterStage('Series B',this)">Series B</div>
      <div class="pill" data-stage="Series C" onclick="filterStage('Series C',this)">Series C+</div>
      <div class="pill" data-stage="Growth" onclick="filterStage('Growth',this)">Growth</div>
    </div>
    <div class="search-wrap">
      <span class="search-icon">🔍</span>
      <input class="search-input" type="text" id="searchInput" placeholder="Buscar empresa, setor, país, investidor..." oninput="applyFilters()">
    </div>
    <select class="time-select" id="timeSelect" onchange="applyFilters()">
      <option value="all">Todo período</option>
      <option value="2026">2026</option>
      <option value="2025">2025</option>
      <option value="2024">2024</option>
    </select>
    <select class="sort-select" id="sortSelect" onchange="applyFilters()">
      <option value="amount">Maior valor</option>
      <option value="date">Mais recente</option>
      <option value="confidence">Mais verificado</option>
      <option value="name">Nome A-Z</option>
    </select>
  </div>
</div>

<!-- DEALS GRID -->
<section class="deals-section">
  <div class="deals-count" id="dealsCount"></div>
  <div class="deals-grid" id="dealsGrid"></div>
  <div class="empty-state" id="emptyState" style="display:none">
    <h3>Nenhum deal encontrado</h3>
    <p>Tente outros filtros ou termos de busca.</p>
  </div>
</section>

<!-- MODAL -->
<div class="modal-overlay" id="modalOverlay" onclick="closeModal(event)">
  <div class="modal" id="modalContent">
    <button class="modal-close" onclick="closeModal()">✕</button>
    <div id="modalBody"></div>
  </div>
</div>

<!-- FOOTER -->
<footer class="site-footer">
  <div class="footer-inner">
    <div class="footer-stats">
      <div class="footer-stat"><strong>{{ total_deals }}</strong> deals rastreados</div>
      <div class="footer-stat"><strong>{{ sources_count }}</strong> fontes ativas</div>
      <div class="footer-stat">Atualizado em <strong>{{ generated_at }}</strong></div>
    </div>
    <div class="footer-copy">LATAM VC Radar · Dados públicos · Atualização diária às 10:30 BRT</div>
  </div>
</footer>

<script>
// Dataset inline
const DEALS = {{ deals_json }};

// Estado dos filtros
let activeStage = 'all';
let activeInvestor = null;
let activeCountry = null;

function formatUSD(n) {
  if (!n || n === 0) return 'N/D';
  if (n >= 1e9) return '$' + (n/1e9).toFixed(1) + 'B';
  if (n >= 1e6) return '$' + (n/1e6).toFixed(0) + 'M';
  if (n >= 1e3) return '$' + (n/1e3).toFixed(0) + 'K';
  return '$' + n;
}

function formatDate(d) {
  if (!d) return '';
  try {
    return new Date(d).toLocaleDateString('pt-BR', {month:'short', year:'numeric'});
  } catch { return d; }
}

function getInitials(name) {
  return name.split(' ').map(w=>w[0]).join('').slice(0,2).toUpperCase();
}

function getConfidenceClass(score) {
  if (score >= 0.7) return 'high';
  if (score >= 0.4) return 'med';
  return 'low';
}

function getSectorColor(sector) {
  const map = {{ sector_colors_json }};
  return map[sector] || '#6b7280';
}

// Count-up animado
function countUp(el, target, suffix='', decimals=0) {
  const duration = 1500;
  const start = performance.now();
  const startVal = 0;
  function step(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    const val = startVal + (target - startVal) * ease;
    el.textContent = decimals > 0 ? val.toFixed(decimals) + suffix : Math.round(val) + suffix;
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

// Inicia count-up quando visível
const observer = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      const el = e.target;
      const target = parseFloat(el.dataset.target);
      const id = el.id;
      if (id === 'statCapital') countUp(el, target, 'B', 1);
      else if (id === 'statAvg') countUp(el, target, 'M', 1);
      else countUp(el, target);
      observer.unobserve(el);
    }
  });
}, {threshold: 0.5});
['statDeals','statCapital','statAvg','statCountries'].forEach(id => {
  const el = document.getElementById(id);
  if (el) observer.observe(el);
});

function renderCard(deal) {
  const logoHTML = deal.logo_url
    ? `<img src="${deal.logo_url}" alt="${deal.company_name}" onerror="this.parentElement.textContent='${getInitials(deal.company_name)}'"/>`
    : getInitials(deal.company_name);
  const allInvestors = [...(deal.lead_investors||[]), ...(deal.other_investors||[])].slice(0,3);
  const foundersHTML = (deal.founders||[]).slice(0,3).map(f => {
    const liUrl = deal.founder_linkedin_urls && deal.founder_linkedin_urls.length > 0
      ? deal.founder_linkedin_urls[0] : `https://linkedin.com/search/results/all/?keywords=${encodeURIComponent(f)}`;
    return `<a class="founder-pill" href="${liUrl}" target="_blank" rel="noopener" onclick="event.stopPropagation()">${f}</a>`;
  }).join('');
  return `
    <div class="deal-card" onclick="openModal(${DEALS.indexOf(deal)})">
      <div class="card-header">
        <div class="card-logo">${logoHTML}</div>
        <div>
          <div class="card-name">${deal.company_name}</div>
          <div class="card-country">${deal.country || ''}${deal.headquarters ? ' · ' + deal.headquarters : ''}</div>
        </div>
      </div>
      ${deal.description ? `<div class="card-desc">${deal.description}</div>` : ''}
      <div class="card-meta">
        ${deal.round_type ? `<span class="badge badge-round">${deal.round_type}</span>` : ''}
        ${deal.sector ? `<span class="badge badge-sector">${deal.sector}</span>` : ''}
      </div>
      <div class="card-amount">${formatUSD(deal.round_amount_usd)}</div>
      ${allInvestors.length ? `<div class="card-investors">🏦 ${allInvestors.join(' · ')}</div>` : ''}
      ${foundersHTML ? `<div class="card-founders">${foundersHTML}</div>` : ''}
      <div class="card-footer">
        <div class="card-date">${formatDate(deal.date)}</div>
        <div class="card-confidence">
          <div class="confidence-dot ${getConfidenceClass(deal.confidence_score)}"></div>
          ${Math.round((deal.confidence_score||0)*100)}% confiança
        </div>
      </div>
    </div>`;
}

function getFilteredDeals() {
  let deals = [...DEALS];
  const search = (document.getElementById('searchInput')?.value || '').toLowerCase();
  const time = document.getElementById('timeSelect')?.value || 'all';
  const sort = document.getElementById('sortSelect')?.value || 'amount';
  deals = deals.filter(d => {
    if (activeStage !== 'all' && d.round_type !== activeStage) {
      if (activeStage === 'Series C' && !['Series C','Series D','Series E','Series F'].includes(d.round_type)) return false;
      else if (activeStage !== 'Series C' && d.round_type !== activeStage) return false;
    }
    if (activeInvestor) {
      const allInvs = [...(d.lead_investors||[]), ...(d.other_investors||[])].join(' ').toLowerCase();
      if (!allInvs.includes(activeInvestor.toLowerCase())) return false;
    }
    if (activeCountry && d.country !== activeCountry) return false;
    if (search) {
      const text = [d.company_name, d.description, d.sector, d.country, d.headquarters,
        ...(d.founders||[]), ...(d.lead_investors||[]), ...(d.other_investors||[])].join(' ').toLowerCase();
      if (!text.includes(search)) return false;
    }
    if (time !== 'all' && d.date) {
      if (!d.date.startsWith(time)) return false;
    }
    return true;
  });
  deals.sort((a,b) => {
    if (sort === 'amount') return (b.round_amount_usd||0) - (a.round_amount_usd||0);
    if (sort === 'date') return (b.date||'') > (a.date||'') ? 1 : -1;
    if (sort === 'confidence') return (b.confidence_score||0) - (a.confidence_score||0);
    if (sort === 'name') return a.company_name.localeCompare(b.company_name);
    return 0;
  });
  return deals;
}

function applyFilters() {
  const deals = getFilteredDeals();
  const grid = document.getElementById('dealsGrid');
  const count = document.getElementById('dealsCount');
  const empty = document.getElementById('emptyState');
  if (deals.length === 0) {
    grid.innerHTML = '';
    empty.style.display = 'block';
    count.textContent = '';
  } else {
    empty.style.display = 'none';
    count.textContent = `${deals.length} deal${deals.length>1?'s':''} encontrado${deals.length>1?'s':''}`;
    grid.innerHTML = deals.map(d => renderCard(d)).join('');
    // Scroll animation
    setTimeout(() => {
      grid.querySelectorAll('.deal-card').forEach((card, i) => {
        setTimeout(() => card.classList.add('visible'), i * 30);
      });
    }, 50);
  }
}

function filterStage(stage, el) {
  activeStage = stage;
  document.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
  el.classList.add('active');
  applyFilters();
}

function filterByInvestor(name) {
  if (activeInvestor === name) {
    activeInvestor = null;
    document.querySelectorAll('.lb-row').forEach(r => r.classList.remove('active'));
  } else {
    activeInvestor = name;
    document.querySelectorAll('.lb-row').forEach(r => {
      r.classList.toggle('active', r.textContent.includes(name));
    });
  }
  applyFilters();
  document.getElementById('dealsGrid').scrollIntoView({behavior:'smooth', block:'start'});
}

function filterByCountry(country) {
  activeCountry = activeCountry === country ? null : country;
  applyFilters();
  document.getElementById('dealsGrid').scrollIntoView({behavior:'smooth', block:'start'});
}

function openModal(idx) {
  const d = DEALS[idx];
  if (!d) return;
  const logoHTML = d.logo_url
    ? `<img src="${d.logo_url}" alt="${d.company_name}" onerror="this.parentElement.textContent='${getInitials(d.company_name)}'"/>`
    : getInitials(d.company_name);
  const allInvestors = [...new Set([...(d.lead_investors||[]), ...(d.other_investors||[])])];
  const foundersHTML = (d.founders||[]).map((f,i) => {
    const liUrl = (d.founder_linkedin_urls||[])[i] || `https://linkedin.com/search/results/all/?keywords=${encodeURIComponent(f)}`;
    return `<a class="founder-link" href="${liUrl}" target="_blank" rel="noopener">${f} ↗</a>`;
  }).join('');
  const links = [];
  if (d.website_url) links.push(`<a class="modal-link" href="${d.website_url}" target="_blank">🌐 Site</a>`);
  if (d.linkedin_url) links.push(`<a class="modal-link" href="${d.linkedin_url}" target="_blank">💼 LinkedIn</a>`);
  if (d.twitter_url) links.push(`<a class="modal-link" href="${d.twitter_url}" target="_blank">🐦 Twitter</a>`);
  if (d.source_url) links.push(`<a class="modal-link" href="${d.source_url}" target="_blank">📰 Fonte</a>`);
  document.getElementById('modalBody').innerHTML = `
    <div class="modal-logo">${logoHTML}</div>
    <h2 class="modal-name">${d.company_name}</h2>
    <div class="modal-country">${d.country || ''}${d.headquarters ? ' · ' + d.headquarters : ''}${d.founded_year ? ' · Fundada em ' + d.founded_year : ''}</div>
    ${d.description ? `<div class="modal-section"><div class="modal-section-label">Sobre</div><div class="modal-desc">${d.description}</div></div>` : ''}
    <div class="modal-section">
      <div class="modal-section-label">Rodada</div>
      <div class="modal-amount">${formatUSD(d.round_amount_usd)}</div>
      <div class="modal-amount-sub">${d.round_amount_original||''} ${d.round_type ? '· ' + d.round_type : ''} ${d.date ? '· ' + formatDate(d.date) : ''}</div>
    </div>
    ${allInvestors.length ? `<div class="modal-section"><div class="modal-section-label">Investidores</div><div class="modal-investors">${allInvestors.map(i=>`<div class="investor-tag">${i}</div>`).join('')}</div></div>` : ''}
    ${foundersHTML ? `<div class="modal-section"><div class="modal-section-label">Fundadores</div><div class="modal-founders">${foundersHTML}</div></div>` : ''}
    <div class="modal-section"><div class="modal-section-label">Setor</div><div class="modal-badges"><span class="badge badge-sector">${d.sector||'N/D'}</span></div></div>
    ${links.length ? `<div class="modal-links">${links.join('')}</div>` : ''}
  `;
  document.getElementById('modalOverlay').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeModal(event) {
  if (event && event.target !== document.getElementById('modalOverlay') && !event.target.classList.contains('modal-close')) return;
  document.getElementById('modalOverlay').classList.remove('open');
  document.body.style.overflow = '';
}

document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal({target:document.getElementById('modalOverlay')}); });

// Init
applyFilters();
</script>
</body>
</html>'''


def fmt_usd(n):
    if n >= 1e9: return f"{n/1e9:.1f}B"
    if n >= 1e6: return f"{n/1e6:.0f}M"
    if n >= 1e3: return f"{n/1e3:.0f}K"
    return str(n)


def build_monthly_data(deals):
    monthly = defaultdict(float)
    for d in deals:
        date = d.get('date')
        if date and len(str(date)) >= 7:
            key = str(date)[:7]
            monthly[key] += d.get('round_amount_usd', 0)
    if not monthly:
        return []
    sorted_months = sorted(monthly.keys())[-12:]
    values = [monthly[m] for m in sorted_months]
    max_val = max(values) if values else 1
    result = []
    MONTH_SHORT = {'01':'Jan','02':'Fev','03':'Mar','04':'Abr','05':'Mai','06':'Jun',
                   '07':'Jul','08':'Ago','09':'Set','10':'Out','11':'Nov','12':'Dez'}
    for i, m in enumerate(sorted_months):
        pct = round((values[i] / max_val) * 100) if max_val > 0 else 0
        parts = m.split('-')
        short = MONTH_SHORT.get(parts[1], parts[1]) if len(parts) > 1 else m
        result.append({
            'label': m,
            'short': short,
            'total': values[i],
            'total_fmt': fmt_usd(values[i]),
            'pct': max(pct, 4)
        })
    return result


def build_donut(deals):
    COUNTRY_PALETTE = [
        '#00e5a0','#3b82f6','#f59e0b','#ec4899','#8b5cf6',
        '#f97316','#22c55e','#06b6d4','#a78bfa','#fbbf24',
    ]
    counts = Counter(d.get('country') for d in deals if d.get('country'))
    if not counts:
        return []
    total = sum(counts.values())
    circumference = 2 * 3.14159 * 54
    segments = []
    offset = circumference * 0.25
    for i, (country, count) in enumerate(counts.most_common(10)):
        pct = count / total
        dash = pct * circumference
        gap = circumference - dash
        segments.append({
            'country': country,
            'count': count,
            'color': COUNTRY_PALETTE[i % len(COUNTRY_PALETTE)],
            'dash': round(dash, 2),
            'gap': round(gap, 2),
            'offset': round(offset, 2),
        })
        offset -= dash
    return segments


def build_sector_capital(deals):
    capital = defaultdict(float)
    for d in deals:
        sector = d.get('sector') or 'Other'
        capital[sector] += d.get('round_amount_usd', 0)
    if not capital:
        return []
    sorted_sectors = sorted(capital.items(), key=lambda x: x[1], reverse=True)[:8]
    max_val = sorted_sectors[0][1] if sorted_sectors else 1
    return [{
        'name': s,
        'amount': v,
        'amount_fmt': fmt_usd(v),
        'pct': round((v / max_val) * 100) if max_val > 0 else 0,
        'color': SECTOR_COLORS.get(s, SECTOR_COLORS['Other']),
    } for s, v in sorted_sectors]


def build_top_investors(deals):
    investor_counts = Counter()
    for d in deals:
        for inv in (d.get('lead_investors') or []):
            investor_counts[inv] += 1
        for inv in (d.get('other_investors') or []):
            investor_counts[inv] += 0.5
    top = [(k, round(v)) for k, v in investor_counts.most_common(10) if v >= 1 and k]
    if not top:
        return []
    max_deals = top[0][1] if top else 1
    return [{'name': k, 'deals': v, 'pct': round((v / max_deals) * 100)} for k, v in top]


def generate():
    with open(MERGED, encoding='utf-8') as f:
        deals = json.load(f)

    deals_sorted = sorted(deals, key=lambda d: d.get('round_amount_usd', 0), reverse=True)

    total_capital = sum(d.get('round_amount_usd', 0) for d in deals)
    deals_with_amount = [d for d in deals if d.get('round_amount_usd', 0) > 0]
    avg_deal = total_capital / len(deals_with_amount) if deals_with_amount else 0
    countries = set(d.get('country') for d in deals if d.get('country'))
    monthly = build_monthly_data(deals)
    donut = build_donut(deals)
    sector_cap = build_sector_capital(deals)
    top_inv = build_top_investors(deals)

    dates = [d.get('date') for d in deals if d.get('date')]
    if dates:
        min_date = min(dates)[:7]
        max_date = max(dates)[:7]
        date_range = f"{min_date} → {max_date}"
    else:
        date_range = datetime.now().strftime('%Y')

    template = Template(HTML_TEMPLATE)
    html = template.render(
        date_range=date_range,
        total_deals=len(deals),
        total_capital_m=round(total_capital / 1e9, 1),
        avg_deal_m=round(avg_deal / 1e6, 1),
        countries_count=len(countries),
        monthly_data=monthly,
        donut_segments=donut,
        sector_capital=sector_cap,
        top_investors=top_inv,
        sources_count=len(set(d.get('source_name') for d in deals)),
        generated_at=datetime.now().strftime('%d/%m/%Y %H:%M'),
        deals_json=json.dumps(deals_sorted, ensure_ascii=False),
        sector_colors_json=json.dumps(SECTOR_COLORS, ensure_ascii=False),
    )

    os.makedirs(TMP, exist_ok=True)
    with open(OUTPUT_TMP, "w", encoding="utf-8") as f:
        f.write(html)
    os.makedirs("public", exist_ok=True)
    with open(OUTPUT_PUBLIC, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[generate] Dashboard gerado: {len(deals)} deals, {len(html)//1024}KB → {OUTPUT_PUBLIC}")


if __name__ == "__main__":
    generate()
