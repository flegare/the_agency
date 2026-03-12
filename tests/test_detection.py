"""Tests for AI assistant auto-detection logic."""
import json
import pytest
from pathlib import Path

import agency


class TestDetectCopilot:
    def test_detects_instructions_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".github").mkdir()
        (tmp_path / ".github" / "copilot-instructions.md").write_text("# Copilot", encoding="utf-8")
        assert agency._detect_copilot() is True

    def test_detects_github_directory_alone(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".github").mkdir()
        assert agency._detect_copilot() is True

    def test_detects_vscode_settings_with_copilot(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".vscode").mkdir()
        settings = {"github.copilot.enable": {"*": True}}
        (tmp_path / ".vscode" / "settings.json").write_text(
            json.dumps(settings), encoding="utf-8"
        )
        assert agency._detect_copilot() is True

    def test_ignores_vscode_settings_without_copilot(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".vscode").mkdir()
        (tmp_path / ".vscode" / "settings.json").write_text(
            '{"editor.fontSize": 14}', encoding="utf-8"
        )
        assert agency._detect_copilot() is False

    def test_returns_false_when_nothing_present(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        assert agency._detect_copilot() is False


class TestAutoDetect:
    """Smoke-test that auto_detect_and_install writes the right files."""

    def _make_skills_src(self, tmp_path: Path) -> Path:
        """Create a minimal fake skills source tree."""
        skills = tmp_path / "fake_skills" / "project_manager"
        skills.mkdir(parents=True)
        (skills / "SKILL.md").write_text("# PM", encoding="utf-8")
        return tmp_path / "fake_skills"

    def test_detects_cursor_and_injects(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(agency, "SKILLS_SRC_DIR", self._make_skills_src(tmp_path))
        # Create the cursor marker
        (tmp_path / ".cursorrules").write_text("# Cursor", encoding="utf-8")

        agency.auto_detect_and_install()

        content = (tmp_path / ".cursorrules").read_text(encoding="utf-8")
        assert "The Agency" in content

    def test_detects_claude_and_injects(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(agency, "SKILLS_SRC_DIR", self._make_skills_src(tmp_path))
        (tmp_path / "CLAUDE.md").write_text("# Claude", encoding="utf-8")

        agency.auto_detect_and_install()

        assert "The Agency" in (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")

    def test_detects_copilot_via_github_dir_and_creates_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(agency, "SKILLS_SRC_DIR", self._make_skills_src(tmp_path))
        (tmp_path / ".github").mkdir()

        agency.auto_detect_and_install()

        copilot_file = tmp_path / ".github" / "copilot-instructions.md"
        assert copilot_file.exists()
        assert "The Agency" in copilot_file.read_text(encoding="utf-8")

    def test_no_detection_writes_nothing(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(agency, "SKILLS_SRC_DIR", self._make_skills_src(tmp_path))

        agency.auto_detect_and_install()

        # No config files should have been created
        config_files = [".cursorrules", "CLAUDE.md", "GEMINI.md", ".clinerules", "CONVENTIONS.md"]
        for f in config_files:
            assert not (tmp_path / f).exists(), f"{f} should not have been created"
