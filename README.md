# Tokenomics: AI Token Price Index (TPI)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Output: JSON & CSV](https://img.shields.io/badge/Output-JSON%20%26%20CSV-blue.svg)](#dataset-structure)
[![Tracked Providers](https://img.shields.io/badge/Providers-OpenAI%20%7C%20Anthropic-orange.svg)](#key-features)

**Tokenomics** is an automated, standalone Python tool (`token_index.py`) that monitors official public token pricing across major AI providers (**OpenAI** and **Anthropic Claude**). It parses developer documentation tables, extracts standard inference rates per million tokens, calculates aggregate market metrics (global and categorized by model tier), and exports clean datasets in both **CSV** and **JSON** formats, maintaining point-in-time historical backups.

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
* **Categorized Benchmarks:** Automatically segments models into three industry-standard tiers:
  * **Lightweight:** Fast, low-latency, high-volume models (Haiku, Luna, Mini).
  * **Flagship:** Balanced, standard production workhorse models (Sonnet, Sol, Codex).
  * **Frontier:** Heavy reasoning, complex agentic models (Opus, Astra, Fable, Mythos, Cyber).
* **Dual Output & Historical Archiving:**
  * Generates current snapshots in `data/token_prices.json` and `data/token_prices.csv`.
  * Preserves point-in-time dated archives under `data/history/` (`token_prices_YYYY-MM-DD.json`, `token_prices_YYYY-MM-DD.csv`).

---

## 📊 Dataset Structure

All consolidated outputs are organized in the `data/` directory:

```text
data/
├── token_prices.csv           # Current latest CSV snapshot
├── token_prices.json          # Current latest JSON snapshot with tier metrics
└── history/
    ├── token_prices_YYYY-MM-DD.csv   # Historical daily backup
    └── token_prices_YYYY-MM-DD.json  # Historical daily backup
```

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
Includes UTC timestamp, models array, global summary, and tier breakdowns:

```json
{
  "timestamp": "2026-10-15T21:42:14",
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
    "max_output": 75.0,
    "by_tier": {
      "lightweight": {
        "models_count": 4,
        "avg_input": 0.5,
        "avg_output": 2.5,
        "min_input": 0.1,
        "max_input": 1.0,
        "min_output": 0.5,
        "max_output": 5.0
      },
      "flagship": {
        "models_count": 9,
        "avg_input": 2.8611,
        "avg_output": 15.4444,
        "min_input": 1.75,
        "max_input": 5.0,
        "min_output": 10.0,
        "max_output": 30.0
      },
      "frontier": {
        "models_count": 16,
        "avg_input": 8.2188,
        "avg_output": 41.875,
        "min_input": 4.0,
        "max_input": 15.0,
        "min_output": 20.0,
        "max_output": 75.0
      }
    }
  }
}
```

---

## 📈 Benchmark Snapshot by Tier

| Performance Tier | Models Count | Avg Input ($ / MTok) | Avg Output ($ / MTok) | Typical Models |
| :--- | :---: | :---: | :---: | :--- |
| **Lightweight** (Mini / Fast) | 4 | **$0.50** | **$2.50** | `gpt-6-luna`, `claude-haiku-5.5`, `claude-haiku-3.5` |
| **Flagship** (Workhorse / Balanced) | 9 | **$2.86** | **$15.44** | `gpt-6.1-sol`, `claude-sonnet-5.5`, `gpt-5.3-codex` |
| **Frontier** (Reasoning / Complex) | 16 | **$8.22** | **$41.88** | `gpt-6-astra`, `claude-opus-5.5`, `claude-fable-5.1` |
| **Global Market Average** | **29** | **$5.49** | **$28.24** | *All tracked models* |

---

## ⚙️ Installation & Requirements

Ensure you have **Python 3.10+** installed, then install dependencies:

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
3. Computes market summary metrics globally and per tier.
4. Updates current snapshots in `data/token_prices.json` and `data/token_prices.csv`.
5. Automatically creates point-in-time dated backups in `data/history/`.
6. Prints the summary index JSON to `stdout`.

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

---

## 🗺️ Roadmap

- [x] High-precision scraping for OpenAI and Anthropic.
- [x] Dual-format export (`token_prices.csv` & `token_prices.json`).
- [x] Automated point-in-time daily backups in `data/history/`.
- [x] Tier-based categorization & benchmarks (`lightweight`, `flagship`, `frontier`).
- [ ] Add support for **Google Gemini** developer pricing.
- [ ] Add support for **DeepSeek** API token rates.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
