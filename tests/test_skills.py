"""Tests for skills installation and codebase context gathering."""
import pytest
from pathlib import Path
from unittest.mock import patch

import agency


def _make_fake_skills_src(base: Path) -> Path:
    """Create a minimal fake skills source directory."""
    src = base / "skills_src"
    for skill in ["project_manager", "historian", "frontend_developer"]:
        skill_dir = src / skill
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(f"# {skill}", encoding="utf-8")
    return src


class TestInstallAgencySkills:
    def test_copies_skills_to_agency_dir(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(agency, "SKILLS_SRC_DIR", _make_fake_skills_src(tmp_path))
        monkeypatch.setattr(agency, "AGENCY_DIR", tmp_path / ".agency")

        result = agency.install_agency_skills()

        assert result is True
        assert (tmp_path / ".agency" / "skills" / "project_manager" / "SKILL.md").exists()

    def test_skips_if_skills_already_installed(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        skills_dst = tmp_path / ".agency" / "skills" / "project_manager"
        skills_dst.mkdir(parents=True)
        (skills_dst / "SKILL.md").write_text("# PM", encoding="utf-8")
        monkeypatch.setattr(agency, "AGENCY_DIR", tmp_path / ".agency")
        monkeypatch.setattr(agency, "SKILLS_SRC_DIR", _make_fake_skills_src(tmp_path))

        result = agency.install_agency_skills()

        assert result is True  # returns True but does not re-copy

    def test_returns_false_if_src_missing(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(agency, "SKILLS_SRC_DIR", tmp_path / "nonexistent_skills")
        monkeypatch.setattr(agency, "AGENCY_DIR", tmp_path / ".agency")

        result = agency.install_agency_skills()

        assert result is False


class TestGatherCodebaseContext:
    def test_includes_directory_listing(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "src").mkdir()
        (tmp_path / "README.md").write_text("# My Project", encoding="utf-8")

        context = agency.gather_codebase_context()

        assert "Project Root Directory Listing" in context
        assert "(DIR) src" in context

    def test_includes_readme_content(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "README.md").write_text("# Hello World Project", encoding="utf-8")

        context = agency.gather_codebase_context()

        assert "Hello World Project" in context

    def test_includes_package_json(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "package.json").write_text('{"name": "my-app"}', encoding="utf-8")

        context = agency.gather_codebase_context()

        assert "my-app" in context

    def test_truncates_large_files(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        big_content = "x" * 25000
        (tmp_path / "README.md").write_text(big_content, encoding="utf-8")

        context = agency.gather_codebase_context()

        assert "[TRUNCATED]" in context

    def test_skips_ignored_directories(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        for skip_dir in [".git", ".venv", "node_modules", ".agency"]:
            (tmp_path / skip_dir).mkdir()

        context = agency.gather_codebase_context()

        for skip_dir in [".git", ".venv", "node_modules", ".agency"]:
            assert skip_dir not in context

    def test_handles_empty_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        # Should not raise
        context = agency.gather_codebase_context()
        assert "Project Root Directory Listing" in context


class TestGetSkillDiff:
    def test_returns_new_skills(self, tmp_path, monkeypatch):
        src = _make_fake_skills_src(tmp_path)
        # Only install one of the three package skills
        skills_dst = tmp_path / ".agency" / "skills" / "project_manager"
        skills_dst.mkdir(parents=True)
        monkeypatch.setattr(agency, "SKILLS_SRC_DIR", src)
        monkeypatch.setattr(agency, "AGENCY_DIR", tmp_path / ".agency")

        diff = agency.get_skill_diff()

        assert "historian" in diff
        assert "frontend_developer" in diff
        assert "project_manager" not in diff

    def test_returns_empty_when_up_to_date(self, tmp_path, monkeypatch):
        src = _make_fake_skills_src(tmp_path)
        # Install all skills
        for skill in ["project_manager", "historian", "frontend_developer"]:
            d = tmp_path / ".agency" / "skills" / skill
            d.mkdir(parents=True)
        monkeypatch.setattr(agency, "SKILLS_SRC_DIR", src)
        monkeypatch.setattr(agency, "AGENCY_DIR", tmp_path / ".agency")

        diff = agency.get_skill_diff()

        assert diff == []

    def test_returns_empty_if_src_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(agency, "SKILLS_SRC_DIR", tmp_path / "nonexistent")
        monkeypatch.setattr(agency, "AGENCY_DIR", tmp_path / ".agency")

        diff = agency.get_skill_diff()

        assert diff == []


class TestSyncSkills:
    def test_copies_only_new_skills(self, tmp_path, monkeypatch):
        src = _make_fake_skills_src(tmp_path)
        # Pre-install one skill
        existing = tmp_path / ".agency" / "skills" / "project_manager"
        existing.mkdir(parents=True)
        (existing / "SKILL.md").write_text("# PM", encoding="utf-8")
        monkeypatch.setattr(agency, "SKILLS_SRC_DIR", src)
        monkeypatch.setattr(agency, "AGENCY_DIR", tmp_path / ".agency")

        count = agency.sync_skills()

        assert count == 2
        assert (tmp_path / ".agency" / "skills" / "historian" / "SKILL.md").exists()
        assert (tmp_path / ".agency" / "skills" / "frontend_developer" / "SKILL.md").exists()
        # Existing skill not touched
        assert (tmp_path / ".agency" / "skills" / "project_manager" / "SKILL.md").read_text() == "# PM"

    def test_returns_zero_when_up_to_date(self, tmp_path, monkeypatch):
        src = _make_fake_skills_src(tmp_path)
        for skill in ["project_manager", "historian", "frontend_developer"]:
            d = tmp_path / ".agency" / "skills" / skill
            d.mkdir(parents=True)
        monkeypatch.setattr(agency, "SKILLS_SRC_DIR", src)
        monkeypatch.setattr(agency, "AGENCY_DIR", tmp_path / ".agency")

        count = agency.sync_skills()

        assert count == 0


class TestAgencyInstruction:
    """Verify the injected instruction contains the expected skill system content."""

    def test_contains_skill_table(self):
        assert "project_manager" in agency.AGENCY_INSTRUCTION
        assert "chief_test_officer" in agency.AGENCY_INSTRUCTION
        assert "cmo_analyst" in agency.AGENCY_INSTRUCTION

    def test_contains_workflow_guidance(self):
        assert "Route first" in agency.AGENCY_INSTRUCTION
        assert "Adopt the persona" in agency.AGENCY_INSTRUCTION
        assert ".agency/skills/" in agency.AGENCY_INSTRUCTION

    def test_contains_all_departments(self):
        departments = [
            "Planning & Management",
            "Architecture",
            "Development",
            "Quality Assurance",
            "Security & Deploy",
        ]
        for dept in departments:
            assert dept in agency.AGENCY_INSTRUCTION, f"Missing department: {dept}"
