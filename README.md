# LATAM VC Radar 🌎

> Plataforma automatizada de inteligência de mercado que rastreia rodadas de investimento em startups da América Latina.

**🔗 [latam-vc-radar.vercel.app](https://latam-vc-radar.vercel.app)** · **[API JSON](https://latam-vc-radar.vercel.app/api/deals.json)** · **[RSS Feed](https://latam-vc-radar.vercel.app/api/rss.xml)**

---

## O que é

Um pipeline Python que roda diariamente no GitHub Actions e:

1. **Coleta** dados de 15 fontes públicas (sites de notícias, databases globais, feeds RSS)
2. **Pesquisa** cada nova empresa via Playwright (Google + site da empresa + artigo fonte)
3. **Limpa e deduplica** com fuzzy matching e scoring de qualidade
4. **Publica** um dashboard HTML interativo com gráficos, mapa, filtros e busca
5. **Disponibiliza** API JSON e feed RSS para consumo externo

## Stack

| Componente | Tecnologia |
|-----------|------------|
| Scrapers | Python 3.12 + requests + BeautifulSoup |
| Pesquisa | Playwright (headless Chromium) |
| Templates | Jinja2 |
| CI/CD | GitHub Actions (cron diário 10:30 BRT) |
| Hosting | Vercel (static deploy) |

## Rodando localmente

```bash
# Instala dependências
pip install -r requirements.txt
python -m playwright install chromium

# Cria pastas necessárias
mkdir -p .tmp data/runs public/api

# Executa o pipeline completo
python tools/seed_known_deals.py
python tools/scrape_google_news.py   # (ou qualquer scraper)
python tools/merge_and_normalize.py
python tools/deep_clean.py
python tools/apply_research.py
python tools/research_new_companies.py
python tools/apply_research.py
python tools/generate_showcase.py
python tools/generate_rss.py
python tools/save_run.py

# Abre o dashboard
open public/index.html
```

## Estrutura

```
tools/               # Scripts Python
  seed_known_deals.py          # 25 deals baseline
  scrape_*.py                  # 15 scrapers
  merge_and_normalize.py       # Dedup + normalização
  deep_clean.py                # Remoção de ruído
  research_new_companies.py    # Pesquisa via Playwright
  apply_research.py            # Aplica pesquisas
  generate_showcase.py         # Dashboard HTML
  generate_rss.py              # RSS + API JSON
  save_run.py                  # Salva histórico

public/
  index.html           # Dashboard (Vercel)
  api/deals.json       # API pública
  api/rss.xml          # Feed RSS

data/
  runs/                # Histórico de runs
  latest.json          # Última run

.github/workflows/
  daily-pipeline.yml   # Cron diário 10:30 BRT
```

## API

```
GET https://latam-vc-radar.vercel.app/api/deals.json
GET https://latam-vc-radar.vercel.app/api/rss.xml
```

## Deploy

1. Fork este repositório
2. Conecte ao [Vercel](https://vercel.com) — detecta o `vercel.json` automaticamente
3. Configure `Output Directory: public` nas configurações do projeto
4. Cada push no `main` faz re-deploy automático
5. O GitHub Actions roda o pipeline diariamente e faz push → Vercel atualiza

---

Made with Python, Playwright & GitHub Actions.
