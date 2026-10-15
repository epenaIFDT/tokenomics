# Tokenomics: AI Token Price Index (TPI)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Output: JSON & CSV](https://img.shields.io/badge/Output-JSON%20%26%20CSV-blue.svg)](#dataset-structure)
[![Tracked Providers](https://img.shields.io/badge/Providers-OpenAI%20%7C%20Anthropic-orange.svg)](#supported-providers)

**Tokenomics** is an automated, standalone Python tool (`token_index.py`) that monitors official public token pricing across major AI providers (**OpenAI** and **Anthropic Claude**). It parses developer documentation tables, extracts standard inference rates per million tokens, calculates aggregate market metrics, and exports clean datasets in both **CSV** and **JSON** formats.

Designed to run seamlessly via **Cron**, **Windows Task Scheduler**, **n8n**, **Node-RED**, or CI/CD pipelines with zero external database dependencies.

---

## 🚀 Key Features

* **Authoritative Source Scraping:** Directly queries official developer documentation pages:
  * [OpenAI Developers Pricing](https://developers.openai.com/api/docs/pricing)
  * [Anthropic Claude Platform Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
* **High-Precision Data Extraction:**
  * Extracts normalized costs in **USD per Million Tokens (MTok)**.
  * Accurately isolates standard base inference rates (Short Context / Prompt base).
  * Excludes batch discounts (e.g., 50% off), priority/fast mode surcharges, prompt caching writes, and non-token services (per-minute audio, search tools, container runtimes).
* **Identifier Normalization:** Slugs model names into clean, lowercase strings (e.g., `gpt-6.1-sol`, `claude-sonnet-5.5`).
* **Dual Output:** Generates structured datasets under `data/`:
  * `data/token_prices.csv`: Tabular format for spreadsheets, Pandas, and BI analysis.
  * `data/token_prices.json`: Full JSON payload including UTC timestamp and aggregate summary metrics.
* **Summary Metrics:** Automatically computes model counts, averages, and min/max boundaries.

---

## 📊 Dataset Structure

All consolidated outputs are saved in the `data/` directory:

### 1. Tabular Format (`data/token_prices.csv`)
Ready for ingestion into Pandas, spreadsheets, DuckDB, or BI dashboards:

```csv
provider,model,input_price,output_price
openai,gpt-6-astra,10.0,50.0
openai,gpt-6.1-sol,2.0,10.0
openai,gpt-6-luna,0.1,0.5
openai,gpt-5.6-sol,4.0,20.0
openai,gpt-5.6-cyber,12.5,75.0
anthropic,claude-fable-5.1,10.0,50.0
anthropic,claude-opus-5.5,4.0,20.0
anthropic,claude-sonnet-5.5,2.0,10.0
anthropic,claude-haiku-5.5,0.1,0.5
...
```

### 2. Structured JSON (`data/token_prices.json`)
Includes UTC timestamp, full models array, and aggregate index summary:

```json
{
  "timestamp": "2026-10-15T19:16:05",
  "models": [
    {
      "provider": "openai",
      "model": "gpt-6.1-sol",
      "input_price": 2.0,
      "output_price": 10.0
    },
    {
      "provider": "anthropic",
      "model": "claude-sonnet-5.5",
      "input_price": 2.0,
      "output_price": 10.0
    }
  ],
  "summary": {
    "models_count": 29,
    "avg_input": 5.4914,
    "avg_output": 28.2414,
    "min_input": 0.1,
    "max_input": 15.0,
    "min_output": 0.5,
    "max_output": 75.0
  }
}
```

---

## 📈 Benchmark Snapshot

| Metric | Input Cost (USD / MTok) | Output Cost (USD / MTok) |
| :--- | :---: | :---: |
| **Market Average** | **$5.4914** | **$28.2414** |
| **Lowest Price** | **$0.10** (`gpt-6-luna`, `claude-haiku-5.5`) | **$0.50** (`gpt-6-luna`, `claude-haiku-5.5`) |
| **Highest Price** | **$15.00** (`claude-opus-4.1`, `claude-opus-4`) | **$75.00** (`gpt-5.6-cyber`, `claude-opus-4.1`) |

*Currently tracking **29 active production models** (9 from OpenAI, 20 from Anthropic).*

---

## ⚙️ Installation & Requirements

Ensure you have **Python 3.10+** installed, then install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## 🖥️ Usage

Run the standalone script:

```bash
python token_index.py
```

### Execution Pipeline:
1. Fetches and parses live tables from OpenAI and Anthropic developer portals.
2. Normalizes model names and pricing.
3. Computes market summary metrics.
4. Saves `data/token_prices.json` and `data/token_prices.csv`.
5. Prints the summary index JSON to `stdout`.

---

## ⏰ Automated Scheduling

### Option 1: Linux / macOS Cron
To execute daily at 06:00 UTC:
```cron
0 6 * * * cd /path/to/tokenomics && /usr/bin/python3 token_index.py >> scraper.log 2>&1
```

### Option 2: Windows Task Scheduler
* **Program/script:** `python`
* **Add arguments:** `token_index.py`
* **Start in:** `F:\path\to\tokenomics`

### Option 3: GitHub Actions (Optional Daily Workflow)
Create `.github/workflows/daily_sync.yml`:

```yaml
name: Daily Token Price Scraping

on:
  schedule:
    - cron: '0 6 * * *' # Every day at 06:00 UTC
  workflow_dispatch:

jobs:
  run-scraper:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run Scraper
        run: python token_index.py
```

---

## 🗺️ Roadmap

- [ ] Add support for **Google Gemini**, **Mistral AI**, and **DeepSeek**.
- [ ] Historical time-series logging via SQLite or DuckDB.
- [ ] Calculate a **Weighted Token Price Index (TPI)** based on estimated enterprise usage volumes.
- [ ] Webhook alerts (Discord/Slack/Telegram) on price change events.
- [ ] Interactive web dashboard via GitHub Pages.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
