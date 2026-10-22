---
name: tokenomics
description: Look up AI model token pricing, compare inference costs across providers (OpenAI, Anthropic Claude), query benchmark tiers (lightweight, flagship, frontier), and update token pricing indexes.
metadata: {"nanobot":{"emoji":"🪙","requires":{"bins":["python"]}}}
---

# Tokenomics - AI Token Price Index

Use this skill when the user asks about:
- Current pricing for AI models (e.g. Claude 3.5 Sonnet, GPT-4o, Haiku, GPT-4o Mini, GPT-6).
- Inference cost comparisons between models or providers (OpenAI vs Anthropic).
- Industry pricing tiers and market benchmarks (`lightweight`, `flagship`, `frontier`).
- Refreshing or scraping the latest token price catalog from official documentation.

## Environment & Paths
* **Project Directory:** `F:\proyectos\tokenomics`
* **CLI Script:** `F:\proyectos\tokenomics\token_index.py`
* **Current Snapshot:** `F:\proyectos\tokenomics\data\token_prices.json` (and `.csv`)
* **Historical Backups:** `F:\proyectos\tokenomics\data\history\`

---

## Usage & Commands

Run commands via PowerShell or Command Prompt.

### 1. Search Pricing for a Specific Model
To search by model name slug or substring:
```powershell
python "F:\proyectos\tokenomics\token_index.py" -q sonnet
```
Or for machine-readable JSON output:
```powershell
python "F:\proyectos\tokenomics\token_index.py" -q sonnet --json
```

### 2. Filter Models by Tier
Available tiers: `lightweight` (budget/fast), `flagship` (workhorse), `frontier` (heavy reasoning):
```powershell
python "F:\proyectos\tokenomics\token_index.py" -t lightweight
python "F:\proyectos\tokenomics\token_index.py" -t flagship
python "F:\proyectos\tokenomics\token_index.py" -t frontier
```

### 3. View Market Summary & Benchmark Metrics
To view global averages, min/max, and tier breakdown:
```powershell
python "F:\proyectos\tokenomics\token_index.py" --summary
```

### 4. Force a Fresh Scrape & Update Cache
To scrape live developer documentation and update `data/`:
```powershell
python "F:\proyectos\tokenomics\token_index.py" --scrape
```

---

## Output Format & Rates

All rates are reported in **USD per million tokens ($/MTok)**:
- `input_price`: Cost per 1,000,000 input prompt tokens.
- `output_price`: Cost per 1,000,000 generated completion tokens.
- `tier`: `lightweight`, `flagship`, or `frontier`.
