"""
Unit tests for Token Price Index (token_index.py)
Validates parser logic, model normalization, tier classification,
aggregate metrics computation, and cache/export handling.
"""

import os
import json
import tempfile
import unittest
import pandas as pd

from token_index import (
    parse_dollar,
    normalize_model_name,
    classify_tier,
    compute_metrics,
    build_index,
    save_files,
    load_cached_data,
)


class TestTokenIndex(unittest.TestCase):
    def test_parse_dollar(self):
        self.assertEqual(parse_dollar("$0.80"), 0.80)
        self.assertEqual(parse_dollar("$2.50"), 2.50)
        self.assertEqual(parse_dollar("$15"), 15.0)
        self.assertEqual(parse_dollar("$0.00"), 0.0)
        self.assertIsNone(parse_dollar(None))
        self.assertIsNone(parse_dollar(""))
        self.assertIsNone(parse_dollar("free"))

    def test_normalize_model_name(self):
        self.assertEqual(normalize_model_name("Claude 3.5 Sonnet"), "claude-3.5-sonnet")
        self.assertEqual(normalize_model_name("GPT-4o Mini"), "gpt-4o-mini")
        self.assertEqual(normalize_model_name("  gpt_6.1_sol  "), "gpt-6.1-sol")
        self.assertEqual(normalize_model_name("model---name"), "model-name")

    def test_classify_tier(self):
        self.assertEqual(classify_tier("claude-3-5-haiku-20241022"), "lightweight")
        self.assertEqual(classify_tier("gpt-4o-mini"), "lightweight")
        self.assertEqual(classify_tier("gpt-5-luna"), "lightweight")
        self.assertEqual(classify_tier("claude-3-5-sonnet"), "flagship")
        self.assertEqual(classify_tier("gpt-6.1-sol"), "flagship")
        self.assertEqual(classify_tier("claude-3-opus"), "frontier")
        self.assertEqual(classify_tier("gpt-cyber-frontier"), "frontier")

    def test_compute_metrics(self):
        self.assertEqual(compute_metrics([]), {})

        sample_models = [
            {"model": "m1", "input_price": 1.0, "output_price": 5.0},
            {"model": "m2", "input_price": 3.0, "output_price": 15.0},
        ]
        metrics = compute_metrics(sample_models)
        self.assertEqual(metrics["models_count"], 2)
        self.assertEqual(metrics["avg_input"], 2.0)
        self.assertEqual(metrics["avg_output"], 10.0)
        self.assertEqual(metrics["min_input"], 1.0)
        self.assertEqual(metrics["max_input"], 3.0)
        self.assertEqual(metrics["min_output"], 5.0)
        self.assertEqual(metrics["max_output"], 15.0)

    def test_build_index(self):
        self.assertEqual(build_index([]), {})

        sample_models = [
            {"model": "claude-3-5-haiku", "input_price": 0.8, "output_price": 4.0, "tier": "lightweight"},
            {"model": "claude-3-5-sonnet", "input_price": 3.0, "output_price": 15.0, "tier": "flagship"},
            {"model": "claude-3-opus", "input_price": 15.0, "output_price": 75.0, "tier": "frontier"},
        ]
        summary = build_index(sample_models)
        self.assertEqual(summary["models_count"], 3)
        self.assertIn("by_tier", summary)
        self.assertIn("lightweight", summary["by_tier"])
        self.assertIn("flagship", summary["by_tier"])
        self.assertIn("frontier", summary["by_tier"])
        self.assertEqual(summary["by_tier"]["lightweight"]["models_count"], 1)

    def test_save_and_load_files(self):
        sample_models = [
            {"provider": "anthropic", "model": "test-model", "input_price": 1.0, "output_price": 2.0, "tier": "lightweight"}
        ]
        summary = build_index(sample_models)

        with tempfile.TemporaryDirectory() as temp_dir:
            json_path, csv_path = save_files(sample_models, summary, output_dir=temp_dir)
            self.assertTrue(os.path.exists(json_path))
            self.assertTrue(os.path.exists(csv_path))

            # Verify history was created
            history_dir = os.path.join(temp_dir, "history")
            self.assertTrue(os.path.exists(history_dir))
            history_files = os.listdir(history_dir)
            self.assertTrue(any(f.endswith(".json") for f in history_files))
            self.assertTrue(any(f.endswith(".csv") for f in history_files))

            # Verify JSON payload
            cached = load_cached_data(data_dir=temp_dir)
            self.assertIsNotNone(cached)
            self.assertEqual(len(cached["models"]), 1)
            self.assertEqual(cached["models"][0]["model"], "test-model")

            # Verify CSV payload
            df = pd.read_csv(csv_path)
            self.assertEqual(len(df), 1)
            self.assertEqual(df.iloc[0]["model"], "test-model")

    def test_cli_query_and_summary(self):
        import io
        from unittest.mock import patch
        from token_index import main

        sample_models = [
            {"provider": "anthropic", "model": "claude-3.5-sonnet", "input_price": 3.0, "output_price": 15.0, "tier": "flagship"},
            {"provider": "openai", "model": "gpt-4o-mini", "input_price": 0.15, "output_price": 0.60, "tier": "lightweight"},
        ]
        summary = build_index(sample_models)

        with tempfile.TemporaryDirectory() as temp_dir:
            save_files(sample_models, summary, output_dir=temp_dir)

            # Test --query sonnet --json
            with patch("sys.argv", ["token_index.py", "-q", "sonnet", "--json", "-o", temp_dir]):
                with patch("sys.stdout", new=io.StringIO()) as fake_out:
                    main()
                    output = json.loads(fake_out.getvalue())
                    self.assertEqual(output["count"], 1)
                    self.assertEqual(output["models"][0]["model"], "claude-3.5-sonnet")

            # Test --tier lightweight --json
            with patch("sys.argv", ["token_index.py", "-t", "lightweight", "--json", "-o", temp_dir]):
                with patch("sys.stdout", new=io.StringIO()) as fake_out:
                    main()
                    output = json.loads(fake_out.getvalue())
                    self.assertEqual(output["count"], 1)
                    self.assertEqual(output["models"][0]["model"], "gpt-4o-mini")

            # Test --summary
            with patch("sys.argv", ["token_index.py", "--summary", "-o", temp_dir]):
                with patch("sys.stdout", new=io.StringIO()) as fake_out:
                    main()
                    output = json.loads(fake_out.getvalue())
                    self.assertEqual(output["models_count"], 2)
                    self.assertIn("by_tier", output)


if __name__ == "__main__":
    unittest.main()
