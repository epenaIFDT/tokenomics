#!/usr/bin/env python3
"""
Token Price Index (TPI) Scraper
Collects daily public token pricing for AI providers (OpenAI, Anthropic Claude),
normalizes model identifiers, computes aggregate market metrics, and exports
the dataset to JSON and CSV files.
"""

import os
import re
import sys
import json
from datetime import datetime, timezone
import requests
import pandas as pd
from bs4 import BeautifulSoup

# Ensure UTF-8 output encoding across platforms (specifically Windows console)
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OPENAI_URL = "https://developers.openai.com/api/docs/pricing"
ANTHROPIC_URL = "https://platform.claude.com/docs/en/about-claude/pricing"

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def parse_dollar(val: str):
    """Extracts numeric float value from a dollar-formatted string."""
    if not val:
        return None
    match = re.search(r"\$([0-9]+(?:\.[0-9]+)?)", str(val))
    return float(match.group(1)) if match else None


def normalize_model_name(name: str) -> str:
    """Normalizes model names into clean, lowercase slug identifiers."""
    # Strip web font icon glyphs (Unicode Private Use Area)
    clean = re.sub(r"[\ue000-\uf8ff]", "", name).strip()
    # Replace spaces and underscores with single hyphens
    clean = re.sub(r"[\s_]+", "-", clean.lower())
    clean = re.sub(r"-+", "-", clean).strip("-")
    return clean


def scrape_openai():
    """
    Scrapes standard text models from OpenAI developer pricing documentation.
    Isolates standard inference rates (Short Context / base pricing) and ignores
    audio, transcription, and non-token services.
    """
    models = []
    seen = set()

    try:
        response = requests.get(OPENAI_URL, headers=REQUEST_HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        ignored_sections = ["tools", "transcription", "audio", "live", "finetuning"]

        for table in soup.find_all("table"):
            heading = table.find_previous(["h1", "h2", "h3", "h4"])
            heading_text = heading.get_text(strip=True).lower() if heading else ""
            if any(ign in heading_text for ign in ignored_sections):
                continue

            rows = table.find_all("tr")
            if not rows:
                continue

            # Dynamically identify column indices from table header
            model_col = None
            input_col = None
            output_col = None

            for row in rows:
                cells = [c.get_text(strip=True).lower() for c in row.find_all(["th", "td"])]
                if not cells:
                    continue

                if "model" in cells and "input" in cells and "output" in cells:
                    model_col = cells.index("model")
                    input_col = cells.index("input")
                    output_col = cells.index("output")
                    break
                elif "input" in cells and "output" in cells and any("model" in c for c in cells):
                    for i, c in enumerate(cells):
                        if "model" in c and model_col is None:
                            model_col = i
                        elif c == "input" and input_col is None:
                            input_col = i
                        elif c == "output" and output_col is None:
                            output_col = i
                    break

            if model_col is None or input_col is None or output_col is None:
                continue

            for row in rows:
                cells = [c.get_text(strip=True) for c in row.find_all(["th", "td"])]
                if len(cells) <= max(model_col, input_col, output_col):
                    continue

                raw_name = cells[model_col]
                if not raw_name or raw_name.lower() in ["model", "name", "category", "-"]:
                    continue

                # Exclude non-text modalities
                if any(m in raw_name.lower() for m in ["audio", "image", "call", "web search"]):
                    continue

                inp = parse_dollar(cells[input_col])
                out = parse_dollar(cells[output_col])

                # Validate valid positive pricing
                if inp is not None and out is not None and inp > 0 and out > 0:
                    model_slug = normalize_model_name(raw_name)
                    # The first table under each category represents the Standard tier
                    if model_slug not in seen:
                        seen.add(model_slug)
                        models.append({
                            "provider": "openai",
                            "model": model_slug,
                            "input_price": inp,
                            "output_price": out,
                        })

    except Exception as e:
        print(f"[OpenAI Scraper Error] {e}", file=sys.stderr)

    return models


def scrape_anthropic():
    """
    Scrapes standard base token models from Anthropic Claude pricing documentation.
    Isolates standard base rates per million tokens (MTok) and ignores
    batch processing and cache write discounts.
    """
    models = []
    seen = set()

    try:
        response = requests.get(ANTHROPIC_URL, headers=REQUEST_HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Locate the official base token pricing table
        for table in soup.find_all("table"):
            table_text = table.get_text()
            if "Base tokens" not in table_text and "Prompt caching" not in table_text:
                continue

            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if not cells or len(cells) < 3:
                    continue

                link = cells[0].find("a")
                raw_name = link.get_text(strip=True) if link else cells[0].get_text(strip=True)
                raw_name = re.sub(r"[\ue000-\uf8ff]", "", raw_name).strip()

                if not raw_name.startswith("Claude") or "docs" in raw_name.lower():
                    continue

                inp = parse_dollar(cells[1].get_text())
                out = parse_dollar(cells[2].get_text())

                if inp is not None and out is not None and inp > 0 and out > 0:
                    model_slug = normalize_model_name(raw_name)
                    if model_slug not in seen:
                        seen.add(model_slug)
                        models.append({
                            "provider": "anthropic",
                            "model": model_slug,
                            "input_price": inp,
                            "output_price": out,
                        })

    except Exception as e:
        print(f"[Anthropic Scraper Error] {e}", file=sys.stderr)

    return models


def build_index(rows):
    """Calculates aggregate summary statistics across all collected models."""
    if not rows:
        return {}
    inputs = [r["input_price"] for r in rows]
    outputs = [r["output_price"] for r in rows]
    return {
        "models_count": len(rows),
        "avg_input": round(sum(inputs) / len(inputs), 4),
        "avg_output": round(sum(outputs) / len(outputs), 4),
        "min_input": min(inputs),
        "max_input": max(inputs),
        "min_output": min(outputs),
        "max_output": max(outputs),
    }


def save_files(rows, summary, output_dir="data"):
    """
    Saves structured data and summary metrics to:
    - {output_dir}/token_prices.json
    - {output_dir}/token_prices.csv
    """
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    data = {
        "timestamp": ts,
        "models": rows,
        "summary": summary,
    }

    json_path = os.path.join(output_dir, "token_prices.json")
    csv_path = os.path.join(output_dir, "token_prices.csv")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df[["provider", "model", "input_price", "output_price"]]
    df.to_csv(csv_path, index=False, encoding="utf-8")

    return json_path, csv_path


def main():
    rows = []
    rows.extend(scrape_openai())
    rows.extend(scrape_anthropic())
    summary = build_index(rows)
    save_files(rows, summary, output_dir="data")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
