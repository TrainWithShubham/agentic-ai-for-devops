"""Credential handling and free-model selection, with no provider requests."""

import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "check_openrouter", Path(__file__).resolve().parents[1] / "scripts/check_openrouter.py"
)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


class ModelCheckTests(unittest.TestCase):
    def test_env_file_is_data_not_shell_code(self):
        with tempfile.TemporaryDirectory() as folder:
            env = Path(folder) / ".env"
            marker = Path(folder) / "must-not-exist"
            env.write_text(
                f"UNRELATED=$(touch {marker})\n"
                "export OPENROUTER_API_KEY='example-test-only' # local comment\n"
            )
            with patch.dict(os.environ, {"OPENROUTER_API_KEY": "ambient-test-only"}):
                self.assertEqual(check.read_key(env), "example-test-only")
            self.assertFalse(marker.exists())

    def test_missing_key_does_not_fall_back_to_another_accounts_key(self):
        with tempfile.TemporaryDirectory() as folder:
            env = Path(folder) / ".env"
            env.write_text("OTHER_API_KEY=example-test-only\n")
            with patch.dict(os.environ, {"OPENROUTER_API_KEY": "ambient-test-only"}):
                with self.assertRaises(ValueError):
                    check.read_key(env)

    def test_free_label_does_not_allow_nonzero_pricing(self):
        model = {
            "id": "example/model:free",
            "pricing": {"prompt": "0", "completion": "0.01"},
            "supported_parameters": ["tools", "tool_choice"],
        }
        self.assertFalse(check.is_free_tool_model(model))
        model["pricing"]["completion"] = "0"
        self.assertTrue(check.is_free_tool_model(model))

    def test_unknown_prices_or_missing_tool_support_are_rejected(self):
        self.assertFalse(check.is_free_tool_model({"id": "example/model:free"}))
        self.assertFalse(
            check.is_free_tool_model(
                {
                    "id": "example/model:free",
                    "pricing": {"prompt": "0", "completion": "0"},
                    "supported_parameters": None,
                }
            )
        )


if __name__ == "__main__":
    unittest.main()
