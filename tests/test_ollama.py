"""Tests for Ollama availability checks and model list parsing."""
import subprocess
import pytest
from unittest.mock import patch, MagicMock

import agency


class TestOllamaAvailable:
    def test_returns_true_when_binary_found(self):
        mock_result = MagicMock(returncode=0)
        with patch("subprocess.run", return_value=mock_result):
            assert agency._ollama_available() is True

    def test_returns_false_when_binary_missing(self):
        with patch("subprocess.run", side_effect=FileNotFoundError):
            assert agency._ollama_available() is False

    def test_returns_true_even_if_version_exits_nonzero(self):
        # Without check=True, subprocess.run returns normally on non-zero exit.
        # _ollama_available() should return True — the binary exists, just bad exit code.
        mock_result = MagicMock(returncode=1)
        with patch("subprocess.run", return_value=mock_result):
            assert agency._ollama_available() is True


class TestCheckOllama:
    def test_returns_false_when_binary_missing(self, capsys):
        with patch.object(agency, "_ollama_available", return_value=False):
            result = agency.check_ollama()
        assert result is False

    def test_returns_true_when_daemon_running(self):
        with patch.object(agency, "_ollama_available", return_value=True):
            with patch("subprocess.run", return_value=MagicMock(returncode=0)):
                assert agency.check_ollama() is True

    def test_returns_false_when_daemon_not_running(self):
        with patch.object(agency, "_ollama_available", return_value=True):
            with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "ollama")):
                assert agency.check_ollama() is False


class TestGetInstalledModels:
    OLLAMA_LIST_OUTPUT = (
        "NAME              ID            SIZE    MODIFIED\n"
        "llama3.2:latest   abc123        2.0 GB  2 days ago\n"
        "mistral:latest    def456        4.1 GB  5 days ago\n"
        "codellama:latest  ghi789        3.8 GB  1 week ago\n"
    )

    def test_parses_model_names(self):
        mock_result = MagicMock(stdout=self.OLLAMA_LIST_OUTPUT, returncode=0)
        with patch("subprocess.run", return_value=mock_result):
            models = agency.get_installed_models()
        assert models == ["llama3.2:latest", "mistral:latest", "codellama:latest"]

    def test_skips_header_row(self):
        mock_result = MagicMock(stdout=self.OLLAMA_LIST_OUTPUT, returncode=0)
        with patch("subprocess.run", return_value=mock_result):
            models = agency.get_installed_models()
        assert "NAME" not in models

    def test_returns_empty_list_when_none_installed(self):
        mock_result = MagicMock(stdout="NAME    ID    SIZE    MODIFIED\n", returncode=0)
        with patch("subprocess.run", return_value=mock_result):
            models = agency.get_installed_models()
        assert models == []

    def test_returns_empty_list_on_subprocess_failure(self):
        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "ollama")):
            models = agency.get_installed_models()
        assert models == []

    def test_returns_empty_list_when_ollama_not_found(self):
        with patch("subprocess.run", side_effect=FileNotFoundError):
            models = agency.get_installed_models()
        assert models == []


class TestPullOllamaModel:
    def test_returns_true_on_success(self):
        with patch("subprocess.run", return_value=MagicMock(returncode=0)):
            assert agency.pull_ollama_model("llama3.2") is True

    def test_returns_false_on_failure(self):
        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "ollama")):
            assert agency.pull_ollama_model("doesnotexist") is False

    def test_returns_false_on_keyboard_interrupt(self):
        with patch("subprocess.run", side_effect=KeyboardInterrupt):
            assert agency.pull_ollama_model("llama3.2") is False
