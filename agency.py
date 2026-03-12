import os
import sys
import shutil
import subprocess
import threading
import importlib.metadata
import requests
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import questionary

console = Console()

# ASCII ART LOGO
AGENCY_LOGO = r"""
  _____ _             _
 |_   _| |__   ___   / \   __ _  ___ _ __   ___ _   _
   | | | '_ \ / _ \ / _ \ / _` |/ _ \ '_ \ / __| | | |
   | | | | | |  __// ___ \ (_| |  __/ | | | (__| |_| |
   |_| |_| |_|\___/_/   \_\__, |\___|_| |_|\___|\__, |
                          |___/                 |___/
      [ The Virtual IT Team in Your Pocket ]
"""

AGENCY_DIR = Path(".agency")
# Base the skills source directory on the location of THIS installed script, not the user's CWD
SKILLS_SRC_DIR = Path(__file__).resolve().parent / "skills"

# Mapping of skills for display
SKILL_CATEGORIES = {
    "Planning & Management": ["project_manager", "workspace_manager", "historian"],
    "Architecture": ["solution_architect", "cmo_analyst", "sre_cloud_architect"],
    "Development": ["backend_developer", "frontend_developer", "coder"],
    "Data & AI": ["relational_dba", "graph_database_architect", "data_scientist", "prompt_engineer"],
    "Design & Docs": ["ux_ui_designer", "technical_writer", "content_copywriter"],
    "Marketing": ["head_of_marketing", "product_marketing_manager"],
    "Quality Assurance": ["chief_test_officer", "qa_automation_engineer", "test_engineer", "e2e_journey_tester", "test_data_manager", "ui_qa_engineer"],
    "Security & Deploy": ["chief_information_security_officer", "application_security_engineer", "security_operations_analyst", "ssdlc_manager"],
    "Support Ops": ["customer_support_triage", "makefile_orchestrator"]
}

# Rich instruction text injected into AI tool config files.
# Deliberately detailed so every assistant — regardless of vendor — understands
# the skills system and can self-navigate without extra prompting.
AGENCY_INSTRUCTION = """\
## The Agency - Virtual IT Team

This project is equipped with **The Agency** — a complete Virtual IT Organization made of
specialized AI Personas called "Skills". Before acting on any task, identify the most
relevant skill, read its definition file, and adopt that persona for the duration of the task.

### Skill Directory
All skills live in `.agency/skills/<skill_name>/SKILL.md`. Available skills:

| Department | Skills |
|---|---|
| Planning & Management | `project_manager`, `historian`, `workspace_manager` |
| Architecture | `solution_architect`, `cmo_analyst`, `sre_cloud_architect` |
| Development | `backend_developer`, `frontend_developer`, `coder` |
| Data & AI | `relational_dba`, `graph_database_architect`, `data_scientist`, `prompt_engineer` |
| Design & Docs | `ux_ui_designer`, `technical_writer`, `content_copywriter` |
| Marketing | `head_of_marketing`, `product_marketing_manager` |
| Quality Assurance | `chief_test_officer`, `qa_automation_engineer`, `test_engineer`, `e2e_journey_tester`, `test_data_manager`, `ui_qa_engineer` |
| Security & Deploy | `chief_information_security_officer`, `application_security_engineer`, `security_operations_analyst`, `ssdlc_manager` |
| Support Ops | `customer_support_triage`, `makefile_orchestrator` |
| Meta-Skills | `skill_creator`, `tool_smith` |

### How to Use the Skills System
1. **Route first:** For any non-trivial request, read `.agency/skills/project_manager/SKILL.md`
   to determine which skill owns this task.
2. **Adopt the persona:** Read the chosen `SKILL.md` and strictly follow its
   "Core Responsibilities" and "Workflow Integration" sections for the entire task.
3. **Hand off correctly:** When a task requires another skill, explicitly switch personas
   by reading that skill's `SKILL.md` before continuing.
4. **Discover before writing:** Skills like `historian` and `cmo_analyst` require you to
   read existing files before generating any output — never infer or hallucinate state.
5. **Master state:** The canonical project state lives in `docs/cmo_state.md` (if it exists).
   Always consult it before making architectural decisions.

### Recommended Workflow for New Tasks
```
project_manager → solution_architect → ciso → backend_developer / frontend_developer
    → chief_test_officer → ssdlc_manager → technical_writer → historian
```
"""

UPDATE_AVAILABLE = None

def check_for_updates():
    """Background thread to check PyPI for a newer version of the CLI."""
    global UPDATE_AVAILABLE
    try:
        current_version = importlib.metadata.version("the-agency-cli")
        response = requests.get("https://pypi.org/pypi/the-agency-cli/json", timeout=1.5)
        if response.status_code == 200:
            latest_version = response.json()["info"]["version"]
            curr_parts = [int(p) for p in current_version.split('.') if p.isdigit()]
            latest_parts = [int(p) for p in latest_version.split('.') if p.isdigit()]
            if latest_parts > curr_parts:
                UPDATE_AVAILABLE = latest_version
    except Exception:
        pass  # Fail silently (offline, or not installed via PyPI)

def print_header():
    try:
        current_version = importlib.metadata.version("the-agency-cli")
    except Exception:
        current_version = "unknown"
    console.print(Text(AGENCY_LOGO, style="bold cyan"))
    console.print(f"[dim]Version {current_version}[/dim]\n", justify="center")

def check_ollama(model: str = "llama3.2") -> bool:
    """Check if the Ollama CLI is available and responsive. Returns True if ready."""
    try:
        subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except FileNotFoundError:
        console.print(
            "[red]Error: 'ollama' CLI not found in PATH.\n"
            "  • Install Ollama from https://ollama.com (available for Windows, macOS, Linux)\n"
            "  • After installation, make sure the 'ollama' command is accessible in your terminal.[/red]"
        )
        return False
    except subprocess.CalledProcessError:
        console.print(
            "[red]Error: Ollama is not running. Please start the Ollama application and try again.[/red]"
        )
        return False

def install_agency_skills() -> bool:
    """Bootstrap .agency folder with skills from the installed package."""
    skills_dst = AGENCY_DIR / "skills"

    if skills_dst.exists() and any(skills_dst.iterdir()):
        console.print("[yellow]The Agency skills are already present in .agency/skills/[/yellow]")
        return True

    if not SKILLS_SRC_DIR.exists():
        console.print(
            "[red]Error: 'skills/' directory not found in the installed package.\n"
            "Please reinstall the-agency-cli: pipx reinstall the-agency-cli[/red]"
        )
        return False

    try:
        shutil.copytree(SKILLS_SRC_DIR, skills_dst)
        console.print("[green]Installed skills to .agency/skills/[/green]")
        return True
    except Exception as e:
        console.print(f"[red]Failed to install skills: {e}[/red]")
        return False

def inject_context(tool_name: str, file_path_str: str, instruction: str) -> bool:
    """Injects Agency instructions into a tool's project memory file."""
    path = Path(file_path_str)
    try:
        if path.exists():
            content = path.read_text(encoding="utf-8")
            if "The Agency" in content:
                console.print(f"[yellow]{tool_name} already configured in {path}.[/yellow]")
                return True
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"\n\n{instruction}")
            console.print(f"[green]Appended Agency instructions to {path}[/green]")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(instruction, encoding="utf-8")
            console.print(f"[green]Created {path} with Agency instructions.[/green]")
        return True
    except Exception as e:
        console.print(f"[red]Failed to configure {tool_name}: {e}[/red]")
        return False

def _detect_copilot() -> bool:
    """
    Detect GitHub Copilot presence.

    Copilot doesn't create a unique marker file on its own — it reads from
    `.github/copilot-instructions.md` when present.  We therefore trigger on:
      1. The instruction file already existing (already configured).
      2. The `.github/` directory existing (repo is GitHub-connected; Copilot
         may be active).
      3. `.vscode/settings.json` mentioning 'copilot' (VS Code extension
         is configured).
    """
    if Path(".github/copilot-instructions.md").exists():
        return True
    if Path(".github").is_dir():
        return True
    vscode_settings = Path(".vscode") / "settings.json"
    if vscode_settings.exists():
        try:
            if "copilot" in vscode_settings.read_text(encoding="utf-8").lower():
                return True
        except Exception:
            pass
    return False

def auto_detect_and_install():
    if not install_agency_skills():
        return

    detected = False
    console.print(Panel("Scanning for AI Assistants...", style="cyan"))

    # Cursor
    if Path(".cursorrules").exists() or Path(".cursor").exists():
        inject_context("Cursor", ".cursorrules", AGENCY_INSTRUCTION)
        detected = True

    # Roo Code / Cline
    if Path(".clinerules").exists() or Path(".clinerules").is_dir() or Path(".roomodes").exists():
        inject_context("Roo Code / Cline", ".clinerules", AGENCY_INSTRUCTION)
        detected = True

    # Gemini CLI
    if Path(".gemini").exists() or Path("GEMINI.md").exists() or Path(".agents").exists():
        inject_context("Gemini CLI", "GEMINI.md", AGENCY_INSTRUCTION)
        detected = True

    # Claude Code
    if Path(".claude").exists() or Path("CLAUDE.md").exists():
        inject_context("Claude Code", "CLAUDE.md", AGENCY_INSTRUCTION)
        detected = True

    # Aider
    if Path(".aider.conf.yml").exists() or Path(".aider.chat.history.md").exists():
        inject_context("Aider", "CONVENTIONS.md", AGENCY_INSTRUCTION)
        detected = True

    # GitHub Copilot — detected via .github/ dir, copilot-instructions.md, or VS Code settings
    if _detect_copilot():
        inject_context("GitHub Copilot", ".github/copilot-instructions.md", AGENCY_INSTRUCTION)
        detected = True

    # Windsurf / Codeium
    if Path(".windsurfrules").exists() or Path(".codeiumrc").exists():
        inject_context("Windsurf", ".windsurfrules", AGENCY_INSTRUCTION)
        detected = True

    # Amp / Continue
    if Path(".continue").is_dir() or Path(".amp").is_dir():
        inject_context("Continue / Amp", ".continue/system.md", AGENCY_INSTRUCTION)
        detected = True

    if not detected:
        console.print(
            "[yellow]No AI assistant config files detected automatically.\n"
            "Run the 'Manual AI Assistant Selection' option to configure your tool.[/yellow]"
        )
    else:
        console.print("\n[bold green]Success![/bold green] The Virtual IT team is ready to assist your AI.")

def manual_install():
    if not install_agency_skills():
        return

    choices = [
        questionary.Choice("Cursor (.cursorrules)", value="cursor"),
        questionary.Choice("Roo Code / Cline (.clinerules)", value="roo"),
        questionary.Choice("Gemini CLI (GEMINI.md)", value="gemini"),
        questionary.Choice("Claude Code (CLAUDE.md)", value="claude"),
        questionary.Choice("Aider (CONVENTIONS.md)", value="aider"),
        questionary.Choice("GitHub Copilot (.github/copilot-instructions.md)", value="copilot"),
        questionary.Choice("Windsurf (.windsurfrules)", value="windsurf"),
        questionary.Choice("Continue / Amp (.continue/system.md)", value="continue"),
        questionary.Separator(),
        questionary.Choice("Back", value="back"),
    ]

    selected = questionary.checkbox(
        "Select AI Assistants to configure:",
        choices=choices,
    ).ask()

    if not selected or "back" in selected:
        return

    mapping = {
        "cursor":   ("Cursor",             ".cursorrules"),
        "roo":      ("Roo Code / Cline",   ".clinerules"),
        "gemini":   ("Gemini CLI",         "GEMINI.md"),
        "claude":   ("Claude Code",        "CLAUDE.md"),
        "aider":    ("Aider",              "CONVENTIONS.md"),
        "copilot":  ("GitHub Copilot",     ".github/copilot-instructions.md"),
        "windsurf": ("Windsurf",           ".windsurfrules"),
        "continue": ("Continue / Amp",     ".continue/system.md"),
    }

    for choice in selected:
        if choice in mapping:
            tool_name, file_path = mapping[choice]
            inject_context(tool_name, file_path, AGENCY_INSTRUCTION)

    console.print("\n[bold green]Success![/bold green] The Virtual IT team is ready to assist your AI.")

def init_agency():
    """Interactive Init Menu."""
    while True:
        console.print(Panel("Initialization Options", style="bold green"))
        choice = questionary.select(
            "How would you like to initialize The Agency?",
            choices=[
                "🔍 Auto-detect AI Assistants & Install",
                "🛠️  Manual AI Assistant Selection",
                "🗺️  Map Digital Twin (Historian + Architect + CMO)",
                "🔙 Back",
            ],
        ).ask()

        if not choice or "Back" in choice:
            break
        elif "Auto-detect" in choice:
            auto_detect_and_install()
        elif "Manual" in choice:
            manual_install()
        elif "Digital Twin" in choice:
            map_digital_twin()

        print("\n")

def browse_skills():
    """Show the organization chart."""
    table = Table(title="The Agency Organization Chart", show_lines=True)
    table.add_column("Department", style="cyan", justify="right")
    table.add_column("Specialized Skills", style="green")

    for dept, skills in SKILL_CATEGORIES.items():
        table.add_row(dept, "\n".join(skills))

    console.print(table)

def run_skill():
    """Interactive prompt to run a specific skill via Ollama."""
    if not check_ollama():
        return

    flat_skills = [skill for dept in SKILL_CATEGORIES.values() for skill in dept]

    skill_choice = questionary.autocomplete(
        "Which skill would you like to employ?",
        choices=flat_skills,
    ).ask()

    if not skill_choice:
        return

    skill_path_agency = AGENCY_DIR / "skills" / skill_choice / "SKILL.md"
    skill_path_main = SKILLS_SRC_DIR / skill_choice / "SKILL.md"

    active_path = None
    if skill_path_agency.exists():
        active_path = skill_path_agency
    elif skill_path_main.exists():
        active_path = skill_path_main

    if not active_path:
        console.print(f"[red]Could not find SKILL.md for '{skill_choice}'[/red]")
        return

    task_input = questionary.text("Describe the task you want this skill to perform:").ask()
    if not task_input:
        return

    model = questionary.text("Which local Ollama model?", default="llama3.2").ask()
    if not model:
        return

    console.print(f"\n[bold yellow]Dispatching task to {skill_choice}...[/bold yellow]\n")

    skill_context = active_path.read_text(encoding="utf-8")
    prompt = f"{skill_context}\n\nTASK: {task_input}"

    try:
        subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        console.print(f"\n[red]Ollama pipeline failed: {e}[/red]")

def gather_codebase_context() -> str:
    """Scan the root directory for standard files and capture a directory listing."""
    console.print("[dim]Gathering codebase context (root directory files and listing)...[/dim]")
    context_parts = []

    # 1. Directory listing (top-level only to avoid massive outputs)
    try:
        context_parts.append("### Project Root Directory Listing ###")
        listing = []
        skip = {".git", ".venv", "node_modules", ".idea", "__pycache__", ".agency"}
        for item in Path(".").iterdir():
            if item.name in skip:
                continue
            label = "(DIR)" if item.is_dir() else "(FILE)"
            listing.append(f"{label} {item.name}")
        context_parts.append("\n".join(sorted(listing)))
    except Exception as e:
        context_parts.append(f"Error gathering directory listing: {e}")

    # 2. Key files
    key_files = [
        "README.md", "README.txt", "README",
        "requirements.txt", "Pipfile", "pyproject.toml", "poetry.lock",
        "package.json", "yarn.lock", "package-lock.json",
        "docker-compose.yml", "docker-compose.yaml", "Dockerfile",
        "Makefile", "build.gradle", "pom.xml",
    ]
    for filename in key_files:
        filepath = Path(filename)
        if filepath.exists() and filepath.is_file():
            try:
                content = filepath.read_text(encoding="utf-8")
                if len(content) > 20000:
                    content = content[:20000] + "\n...[TRUNCATED]..."
                context_parts.append(f"\n### File: {filename} ###\n```\n{content}\n```")
            except Exception as e:
                console.print(f"[yellow]Could not read {filename}: {e}[/yellow]")

    return "\n\n".join(context_parts)

def run_agent_to_file(skill_choice: str, model: str, task_input: str, output_file: Path, context: str = "") -> bool:
    """Run an agent and redirect stdout to an output file."""
    skill_path_agency = AGENCY_DIR / "skills" / skill_choice / "SKILL.md"
    skill_path_main = SKILLS_SRC_DIR / skill_choice / "SKILL.md"

    active_path = None
    if skill_path_agency.exists():
        active_path = skill_path_agency
    elif skill_path_main.exists():
        active_path = skill_path_main

    if not active_path:
        console.print(f"[red]Could not find SKILL.md for '{skill_choice}'[/red]")
        return False

    skill_context = active_path.read_text(encoding="utf-8")
    prompt = f"{skill_context}\n\nTASK: {task_input}"
    if context:
        prompt += f"\n\nCODEBASE CONTEXT:\n{context}"

    output_file.parent.mkdir(parents=True, exist_ok=True)

    console.print(f"\n[bold yellow]Dispatching {skill_choice} → {output_file.name}...[/bold yellow]")

    try:
        with open(output_file, "w", encoding="utf-8") as out_f:
            subprocess.run(
                ["ollama", "run", model],
                input=prompt,
                text=True,
                stdout=out_f,
                check=True,
            )
        console.print(f"[green]Generated: {output_file}[/green]")
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"\n[red]Ollama pipeline failed for {skill_choice}: {e}[/red]")
        return False

def map_digital_twin():
    """Automate codebase mapping to build the Digital Twin documentation."""
    if not check_ollama():
        return

    console.print(Panel("🗺️  Mapping the Digital Twin", style="bold magenta"))
    console.print(
        "This will read your repository structure and dispatch the Historian, "
        "Solution Architect, and CMO Analyst to build architecture state docs.\n"
    )

    confirm = questionary.confirm("Are you ready to automate your codebase mapping?").ask()
    if not confirm:
        return

    model = questionary.text("Which local Ollama model?", default="llama3.2").ask()
    if not model:
        return

    context = gather_codebase_context()

    historian_task = (
        "Analyze the provided project context (files and structure). Summarize what this "
        "project is, its history (if discernible), and its key components. "
        "Output a 'historian_context.md' summarizing the current state."
    )
    architect_task = (
        "Review the provided codebase context. Generate a 'system_architecture.md' document "
        "outlining the system architecture, technologies used, and deployment structure."
    )
    cmo_task = (
        "Review the provided codebase context. Generate a 'cmo_state.md' master index document "
        "that defines the infrastructure, architecture, and feature landscape as the Digital Twin."
    )

    docs_dir = Path("docs")
    (docs_dir / "architecture").mkdir(parents=True, exist_ok=True)
    (docs_dir / "features").mkdir(parents=True, exist_ok=True)
    (docs_dir / "infrastructure").mkdir(parents=True, exist_ok=True)

    run_agent_to_file("historian", model, historian_task, docs_dir / "architecture" / "historian_context.md", context)
    run_agent_to_file("solution_architect", model, architect_task, docs_dir / "architecture" / "system_architecture.md", context)
    run_agent_to_file("cmo_analyst", model, cmo_task, docs_dir / "cmo_state.md", context)

    console.print("\n[bold green]Digital Twin Mapping Complete![/bold green]")
    console.print("Review the generated files in the [cyan]docs/[/cyan] directory.")

def main_menu():
    # Handle CLI subcommands when called as `agency <cmd>`
    # (entry point in pyproject.toml calls main_menu() directly)
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "init":
            print_header()
            init_agency()
        elif cmd == "list":
            print_header()
            browse_skills()
        elif cmd == "run":
            print_header()
            run_skill()
        elif cmd == "twin":
            print_header()
            map_digital_twin()
        else:
            console.print(
                f"[red]Unknown command: '{cmd}'[/red]\n"
                "Available commands: init, list, run, twin\n"
                "Run [cyan]agency[/cyan] with no arguments for the interactive menu."
            )
        return

    # Start update check in background
    threading.Thread(target=check_for_updates, daemon=True).start()

    print_header()

    while True:
        if UPDATE_AVAILABLE:
            console.print(Panel(
                f"[bold yellow]Update Available![/bold yellow] Version {UPDATE_AVAILABLE} is out.\n"
                f"Run [cyan]pipx upgrade the-agency-cli[/cyan] to get the latest skills.",
                border_style="yellow",
            ))

        choice = questionary.select(
            "Welcome to The Agency. How can the IT Team assist you today?",
            choices=[
                "🚀 Initialize / Configure Project (init)",
                "👥 Browse Organization Chart (list)",
                "⚡ Task a specific Skill (run)",
                "❌ Exit",
            ],
        ).ask()

        if not choice or "Exit" in choice:
            console.print("[dim]Shutting down Virtual IT Team. Goodbye![/dim]")
            break
        elif "init" in choice:
            init_agency()
        elif "list" in choice:
            browse_skills()
        elif "run" in choice:
            run_skill()

        print("\n")

if __name__ == "__main__":
    main_menu()
