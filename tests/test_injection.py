"""Tests for inject_context() — the core file-injection logic."""
import pytest
from pathlib import Path

import agency


SAMPLE_INSTRUCTION = "## The Agency - Virtual IT Team\nTest instruction."


class TestInjectContext:
    def test_creates_new_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        target = tmp_path / "CLAUDE.md"

        result = agency.inject_context("Claude", str(target), SAMPLE_INSTRUCTION)

        assert result is True
        assert target.exists()
        assert SAMPLE_INSTRUCTION in target.read_text(encoding="utf-8")

    def test_appends_to_existing_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        target = tmp_path / ".cursorrules"
        target.write_text("# Existing content", encoding="utf-8")

        result = agency.inject_context("Cursor", str(target), SAMPLE_INSTRUCTION)

        assert result is True
        content = target.read_text(encoding="utf-8")
        assert "# Existing content" in content
        assert SAMPLE_INSTRUCTION in content

    def test_skips_if_already_configured(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        target = tmp_path / "CLAUDE.md"
        target.write_text("## The Agency - already here", encoding="utf-8")

        result = agency.inject_context("Claude", str(target), SAMPLE_INSTRUCTION)

        assert result is True
        # File should be unchanged — instruction not appended again
        assert target.read_text(encoding="utf-8") == "## The Agency - already here"

    def test_creates_parent_directories(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        target = tmp_path / ".github" / "copilot-instructions.md"

        result = agency.inject_context("Copilot", str(target), SAMPLE_INSTRUCTION)

        assert result is True
        assert target.exists()
        assert SAMPLE_INSTRUCTION in target.read_text(encoding="utf-8")

    def test_returns_false_on_write_error(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        # File exists → hits the open(..., "a") append branch
        target = tmp_path / "existing.md"
        target.write_text("# existing", encoding="utf-8")

        def _raise(*a, **kw):
            raise PermissionError("denied")

        monkeypatch.setattr("builtins.open", _raise)
        result = agency.inject_context("Test", str(target), SAMPLE_INSTRUCTION)
        assert result is False
