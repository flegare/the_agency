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
    "Reel Production": ["reel_creative_director", "voiceover_script_writer", "storyboard_artist", "cinematography_director"],
    "Quality Assurance": ["chief_test_officer", "qa_automation_engineer", "test_engineer", "e2e_journey_tester", "test_data_manager", "ui_qa_engineer"],
    "Security & Deploy": ["chief_information_security_officer", "application_security_engineer", "security_operations_analyst", "ssdlc_manager"],
    "Support Ops": ["customer_support_triage", "makefile_orchestrator"]
}

# Popular models shown when the user wants to pull one
POPULAR_MODELS = [
    "llama3.2",
    "llama3.2:1b",
    "llama3.1:8b",
    "mistral",
    "codellama",
    "deepseek-coder-v2",
    "qwen2.5-coder",
    "phi3",
    "gemma2",
    "gemma2:2b",
]

# Rich instruction text injected into AI tool config files.
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
| Reel Production | `reel_creative_director`, `voiceover_script_writer`, `storyboard_artist`, `cinematography_director` |
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
        pass

def print_header():
    try:
        current_version = importlib.metadata.version("the-agency-cli")
    except Exception:
        current_version = "unknown"
    console.print(Text(AGENCY_LOGO, style="bold cyan"))
    console.print(f"[dim]Version {current_version}[/dim]\n", justify="center")

# ---------------------------------------------------------------------------
# Ollama helpers
# ---------------------------------------------------------------------------

def _ollama_available() -> bool:
    """Return True if the ollama binary exists in PATH."""
    try:
        subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
        )
        return True
    except FileNotFoundError:
        return False

def check_ollama() -> bool:
    """Verify Ollama is installed and its daemon is responsive.
    Prints a helpful error and returns False on failure."""
    if not _ollama_available():
        console.print(
            "[red]Error: 'ollama' not found in PATH.[/red]\n"
            "Use [cyan]agency ollama[/cyan] to install it, or visit https://ollama.com"
        )
        return False
    try:
        subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        console.print(
            "[red]Ollama is installed but its daemon isn't running.\n"
            "Start the Ollama application and try again.[/red]"
        )
        return False

def get_installed_models() -> list:
    """Return list of model name strings from `ollama list`."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True,
        )
        lines = result.stdout.strip().splitlines()
        models = []
        for line in lines[1:]:  # skip header row
            parts = line.split()
            if parts:
                models.append(parts[0])
        return models
    except Exception:
        return []

def pull_ollama_model(model_name: str) -> bool:
    """Pull a model from Ollama Hub, streaming progress directly to the terminal."""
    console.print(f"\n[bold yellow]Pulling [cyan]{model_name}[/cyan]...[/bold yellow] (this may take a few minutes)\n")
    try:
        subprocess.run(["ollama", "pull", model_name], check=True)
        console.print(f"\n[green]Model '{model_name}' ready.[/green]")
        return True
    except subprocess.CalledProcessError:
        console.print(f"[red]Failed to pull '{model_name}'. Check the model name and try again.[/red]")
        return False
    except KeyboardInterrupt:
        console.print("\n[yellow]Pull cancelled.[/yellow]")
        return False

def select_model(prompt_text: str = "Which Ollama model?") -> str:
    """Show installed models as a selection list.
    Offers to pull a new model if none are installed or user wants a different one."""
    installed = get_installed_models()

    choices = []
    if installed:
        for m in installed:
            choices.append(questionary.Choice(f"  {m}", value=m))
        choices.append(questionary.Separator())

    choices.append(questionary.Choice("📥  Pull / install a model...", value="__pull__"))
    if installed:
        choices.append(questionary.Choice("✏️   Type a model name manually", value="__manual__"))

    choice = questionary.select(prompt_text, choices=choices).ask()

    if not choice:
        return ""

    if choice == "__manual__":
        return questionary.text("Model name:").ask() or ""

    if choice == "__pull__":
        # Filter out already-installed models from the suggestions
        suggestions = [m for m in POPULAR_MODELS if m not in installed]
        pull_choices = [questionary.Choice(m, value=m) for m in suggestions]
        pull_choices.append(questionary.Separator())
        pull_choices.append(questionary.Choice("✏️   Type a custom model name", value="__custom__"))

        model_to_pull = questionary.select("Which model would you like to pull?", choices=pull_choices).ask()

        if not model_to_pull:
            return ""
        if model_to_pull == "__custom__":
            model_to_pull = questionary.text("Enter model name (e.g. llama3.2:8b):").ask() or ""

        if not model_to_pull:
            return ""

        return model_to_pull if pull_ollama_model(model_to_pull) else ""

    return choice

def setup_ollama():
    """Guide the user through installing Ollama and managing local models."""
    console.print(Panel("🦙  Ollama Setup", style="bold cyan"))

    ollama_installed = _ollama_available()

    if not ollama_installed:
        console.print("[yellow]Ollama is not installed on this system.[/yellow]\n")
        platform = sys.platform

        if platform == "win32":
            console.print(
                "Install via [bold]winget[/bold] (Windows Package Manager):\n"
                "  [cyan]winget install Ollama.Ollama[/cyan]\n\n"
                "Or download the installer directly from [cyan]https://ollama.com/download/windows[/cyan]"
            )
            if questionary.confirm("\nTry to install now via winget?").ask():
                try:
                    subprocess.run(["winget", "install", "Ollama.Ollama", "--accept-package-agreements", "--accept-source-agreements"], check=True)
                    console.print("[green]Ollama installed. Please restart your terminal and run `agency ollama` again.[/green]")
                except FileNotFoundError:
                    console.print("[red]winget not found. Please install Ollama manually from https://ollama.com/download/windows[/red]")
                except subprocess.CalledProcessError:
                    console.print("[red]winget install failed. Please install Ollama manually.[/red]")
            return

        elif platform == "darwin":
            console.print(
                "Install via [bold]Homebrew[/bold]:\n"
                "  [cyan]brew install ollama[/cyan]\n\n"
                "Or download the macOS app from [cyan]https://ollama.com/download/mac[/cyan]"
            )
            if questionary.confirm("\nTry to install now via Homebrew?").ask():
                try:
                    subprocess.run(["brew", "install", "ollama"], check=True)
                    console.print("[green]Ollama installed. Run `ollama serve` then `agency ollama` again.[/green]")
                except FileNotFoundError:
                    console.print("[red]Homebrew not found. Install it from https://brew.sh or install Ollama manually.[/red]")
                except subprocess.CalledProcessError:
                    console.print("[red]brew install failed. Please install Ollama manually.[/red]")
            return

        else:  # Linux
            console.print(
                "Install via the official script:\n"
                "  [cyan]curl -fsSL https://ollama.com/install.sh | sh[/cyan]"
            )
            if questionary.confirm("\nRun the install script now?").ask():
                try:
                    subprocess.run(
                        "curl -fsSL https://ollama.com/install.sh | sh",
                        shell=True,
                        check=True,
                    )
                    console.print("[green]Ollama installed. Run `ollama serve` in a separate terminal, then `agency ollama` again.[/green]")
                except subprocess.CalledProcessError:
                    console.print("[red]Install script failed. Please install manually from https://ollama.com[/red]")
            return

    # Ollama is installed — check daemon
    daemon_ok = check_ollama()
    installed_models = get_installed_models() if daemon_ok else []

    console.print("[green]Ollama is installed.[/green]")
    if not daemon_ok:
        console.print("[yellow]Daemon not running — start the Ollama application to manage models.[/yellow]")
        return

    # Show installed models
    if installed_models:
        table = Table(title="Installed Models", show_lines=False)
        table.add_column("Model", style="cyan")
        for m in installed_models:
            table.add_row(m)
        console.print(table)
    else:
        console.print("[yellow]No models installed yet.[/yellow]")

    # Offer to pull more
    while True:
        action = questionary.select(
            "What would you like to do?",
            choices=[
                "📥  Pull a model",
                "🔙  Back",
            ],
        ).ask()

        if not action or "Back" in action:
            break

        if "Pull" in action:
            suggestions = [m for m in POPULAR_MODELS if m not in installed_models]
            pull_choices = [questionary.Choice(m, value=m) for m in suggestions]
            pull_choices.append(questionary.Separator())
            pull_choices.append(questionary.Choice("✏️   Type a custom model name", value="__custom__"))

            model_to_pull = questionary.select("Which model?", choices=pull_choices).ask()
            if not model_to_pull:
                continue
            if model_to_pull == "__custom__":
                model_to_pull = questionary.text("Model name (e.g. llama3.2:8b):").ask() or ""
            if model_to_pull:
                if pull_ollama_model(model_to_pull):
                    installed_models.append(model_to_pull)

# ---------------------------------------------------------------------------
# Skills installation & context injection
# ---------------------------------------------------------------------------

def install_agency_skills() -> bool:
    """Bootstrap .agency folder with skills from the installed package."""
    skills_dst = AGENCY_DIR / "skills"

    if skills_dst.exists() and any(skills_dst.iterdir()):
        console.print("[yellow]The Agency skills are already present in .agency/skills/[/yellow]")
        return True

    if not SKILLS_SRC_DIR.exists():
        console.print(
            "[red]Error: 'skills/' directory not found in the installed package.\n"
            "Please reinstall: pipx reinstall the-agency-cli[/red]"
        )
        return False

    try:
        shutil.copytree(SKILLS_SRC_DIR, skills_dst)
        console.print("[green]Installed skills to .agency/skills/[/green]")
        return True
    except Exception as e:
        console.print(f"[red]Failed to install skills: {e}[/red]")
        return False


def get_skill_diff() -> list[str]:
    """Return skill names present in the package but missing from .agency/skills/."""
    if not SKILLS_SRC_DIR.exists():
        return []
    skills_dst = AGENCY_DIR / "skills"
    installed = {p.name for p in skills_dst.iterdir()} if skills_dst.exists() else set()
    package_skills = {p.name for p in SKILLS_SRC_DIR.iterdir() if p.is_dir()}
    return sorted(package_skills - installed)


def sync_skills() -> int:
    """Copy new skills from the package into .agency/skills/. Returns count of skills added."""
    new_skills = get_skill_diff()
    if not new_skills:
        console.print("[green]Skills are up to date — no new skills to sync.[/green]")
        return 0

    skills_dst = AGENCY_DIR / "skills"
    skills_dst.mkdir(parents=True, exist_ok=True)

    added = 0
    for skill_name in new_skills:
        src = SKILLS_SRC_DIR / skill_name
        dst = skills_dst / skill_name
        try:
            shutil.copytree(src, dst)
            console.print(f"[green]  + {skill_name}[/green]")
            added += 1
        except Exception as e:
            console.print(f"[red]  ✗ {skill_name}: {e}[/red]")

    console.print(f"\n[bold green]Synced {added} new skill(s) to .agency/skills/[/bold green]")
    return added


def update_agency():
    """Sync new skills and optionally re-inject the latest AGENCY_INSTRUCTION."""
    console.print(Panel("Checking for new skills...", style="cyan"))

    if not SKILLS_SRC_DIR.exists():
        console.print("[red]Package skills directory not found. Run: pipx reinstall the-agency-cli[/red]")
        return

    new_skills = get_skill_diff()
    if new_skills:
        console.print(f"[cyan]Found {len(new_skills)} new skill(s):[/cyan]")
        for s in new_skills:
            console.print(f"  • {s}")
        sync_skills()
    else:
        console.print("[green]No new skills found — already up to date.[/green]")

    re_inject = questionary.confirm(
        "Re-inject updated Agency instructions into detected AI tool config files?",
        default=False,
    ).ask()
    if re_inject:
        auto_detect_and_install()

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
    """Detect GitHub Copilot via .github/ dir, copilot-instructions.md, or VS Code settings."""
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

    if Path(".cursorrules").exists() or Path(".cursor").exists():
        inject_context("Cursor", ".cursorrules", AGENCY_INSTRUCTION)
        detected = True

    if Path(".clinerules").exists() or Path(".clinerules").is_dir() or Path(".roomodes").exists():
        inject_context("Roo Code / Cline", ".clinerules", AGENCY_INSTRUCTION)
        detected = True

    if Path(".gemini").exists() or Path("GEMINI.md").exists() or Path(".agents").exists():
        inject_context("Gemini CLI", "GEMINI.md", AGENCY_INSTRUCTION)
        detected = True

    if Path(".claude").exists() or Path("CLAUDE.md").exists():
        inject_context("Claude Code", "CLAUDE.md", AGENCY_INSTRUCTION)
        detected = True

    if Path(".aider.conf.yml").exists() or Path(".aider.chat.history.md").exists():
        inject_context("Aider", "CONVENTIONS.md", AGENCY_INSTRUCTION)
        detected = True

    if _detect_copilot():
        inject_context("GitHub Copilot", ".github/copilot-instructions.md", AGENCY_INSTRUCTION)
        detected = True

    if Path(".windsurfrules").exists() or Path(".codeiumrc").exists():
        inject_context("Windsurf", ".windsurfrules", AGENCY_INSTRUCTION)
        detected = True

    if Path(".continue").is_dir() or Path(".amp").is_dir():
        inject_context("Continue / Amp", ".continue/system.md", AGENCY_INSTRUCTION)
        detected = True

    if not detected:
        console.print(
            "[yellow]No AI assistant config files detected automatically.\n"
            "Use 'Manual AI Assistant Selection' to configure your tool.[/yellow]"
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

    selected = questionary.checkbox("Select AI Assistants to configure:", choices=choices).ask()

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
                "🦙  Setup Ollama (install / pull models)",
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
        elif "Ollama" in choice:
            setup_ollama()
        elif "Digital Twin" in choice:
            map_digital_twin()

        print("\n")

# ---------------------------------------------------------------------------
# Skill runner
# ---------------------------------------------------------------------------

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

    task_input = questionary.text("Describe the task you want this skill to perform:").ask()
    if not task_input:
        return

    default_out = f"docs/{skill_choice}_output.md"
    output_path_str = questionary.text(
        "Save output to file (leave blank to stream to terminal):",
        default=default_out,
    ).ask()

    model = select_model("Which Ollama model should run this skill?")
    if not model:
        return

    console.print(f"\n[bold yellow]Dispatching task to {skill_choice} via {model}...[/bold yellow]\n")

    if output_path_str and output_path_str.strip():
        # Use file-writing path with spinner and full context injection
        context = gather_codebase_context()
        output_file = Path(output_path_str.strip())
        ok = run_agent_to_file(skill_choice, model, task_input, output_file, context)
        if ok:
            console.print(f"[bold green]Output written to {output_file}[/bold green]")
        return

    # Stream to terminal (no file output)
    active_path_str, prompt = _build_skill_prompt(skill_choice, task_input, gather_codebase_context())
    if not active_path_str:
        console.print(f"[red]Could not find SKILL.md for '{skill_choice}'[/red]")
        return

    try:
        subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            text=True,
            check=True,
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        console.print("\n[red]Timed out after 10 minutes. Try a smaller/faster model.[/red]")
    except subprocess.CalledProcessError as e:
        console.print(f"\n[red]Ollama pipeline failed: {e}[/red]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled.[/yellow]")

# ---------------------------------------------------------------------------
# Digital Twin mapping
# ---------------------------------------------------------------------------

def gather_codebase_context() -> str:
    """Scan the root directory for standard files and capture a directory listing."""
    console.print("[dim]Gathering codebase context...[/dim]")
    context_parts = []

    try:
        context_parts.append("### Project Root Directory Listing ###")
        skip = {".git", ".venv", "node_modules", ".idea", "__pycache__", ".agency"}
        listing = []
        for item in Path(".").iterdir():
            if item.name in skip:
                continue
            label = "(DIR)" if item.is_dir() else "(FILE)"
            listing.append(f"{label} {item.name}")
        context_parts.append("\n".join(sorted(listing)))
    except Exception as e:
        context_parts.append(f"Error gathering directory listing: {e}")

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

def _build_skill_prompt(skill_choice: str, task_input: str, context: str = "") -> tuple[str | None, str]:
    """Load SKILL.md, inject discovery files and codebase context, return (active_path_str, prompt)."""
    skill_path_agency = AGENCY_DIR / "skills" / skill_choice / "SKILL.md"
    skill_path_main = SKILLS_SRC_DIR / skill_choice / "SKILL.md"

    active_path = None
    if skill_path_agency.exists():
        active_path = skill_path_agency
    elif skill_path_main.exists():
        active_path = skill_path_main

    if not active_path:
        return None, ""

    skill_context = active_path.read_text(encoding="utf-8")

    # Inject discovery files that skills' protocols ask for
    discovery_files = [
        "docs/cmo_state.md",
        "docs/product_brief.md",
        "docs/features",  # directory — list contents
    ]
    discovery_parts = []
    for df in discovery_files:
        dp = Path(df)
        if dp.is_file():
            try:
                txt = dp.read_text(encoding="utf-8")
                if len(txt) > 10000:
                    txt = txt[:10000] + "\n...[TRUNCATED]..."
                discovery_parts.append(f"### {df} ###\n{txt}")
            except Exception:
                pass
        elif dp.is_dir():
            files = list(dp.glob("*.md"))
            for fp in files[:10]:
                try:
                    txt = fp.read_text(encoding="utf-8")
                    if len(txt) > 5000:
                        txt = txt[:5000] + "\n...[TRUNCATED]..."
                    discovery_parts.append(f"### {fp} ###\n{txt}")
                except Exception:
                    pass

    output_instruction = (
        "\n\n## OUTPUT REQUIREMENT\n"
        "Your response MUST be a complete, structured Markdown document ready to be saved as a file. "
        "Do NOT produce a conversational reply. Do NOT summarise what you will do. "
        "Write the actual deliverable defined in the skill above — headers, sections, and all content — "
        "exactly as it would appear in the final file. Begin with the document title on line 1."
    )

    prompt = skill_context + output_instruction + f"\n\n## TASK\n{task_input}"

    if discovery_parts:
        prompt += "\n\n## PROJECT DISCOVERY FILES\n" + "\n\n".join(discovery_parts)

    if context:
        prompt += f"\n\n## CODEBASE CONTEXT\n{context}"

    return str(active_path), prompt


def run_agent_to_file(skill_choice: str, model: str, task_input: str, output_file: Path, context: str = "") -> bool:
    """Run an agent and write output to a file, with a live spinner and 10-min timeout."""
    active_path, prompt = _build_skill_prompt(skill_choice, task_input, context)
    if not active_path:
        console.print(f"[red]Could not find SKILL.md for '{skill_choice}'[/red]")
        return False

    output_file.parent.mkdir(parents=True, exist_ok=True)

    result = {"success": False, "error": None}

    def _run():
        try:
            with open(output_file, "w", encoding="utf-8") as out_f:
                subprocess.run(
                    ["ollama", "run", model],
                    input=prompt,
                    text=True,
                    stdout=out_f,
                    check=True,
                    timeout=600,
                )
            result["success"] = True
        except subprocess.TimeoutExpired:
            result["error"] = "Timed out after 10 minutes."
        except subprocess.CalledProcessError as e:
            result["error"] = str(e)
        except Exception as e:
            result["error"] = str(e)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()

    with console.status(
        f"[bold yellow]{skill_choice}[/bold yellow] is working "
        f"([dim]{model}[/dim]) → [cyan]{output_file.name}[/cyan]"
    ):
        thread.join()

    if result["success"]:
        console.print(f"[green]✓ Generated: {output_file}[/green]")
        return True
    else:
        console.print(f"[red]✗ {skill_choice} failed: {result['error']}[/red]")
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

    model = select_model("Which Ollama model should run the agents?")
    if not model:
        return

    context = gather_codebase_context()

    historian_task = (
        "Analyze the provided project context. Summarize what this project is, "
        "its history (if discernible), and its key components. "
        "Output a historian_context.md summarizing the current state."
    )
    architect_task = (
        "Review the provided codebase context. Generate a system_architecture.md "
        "outlining the system architecture, technologies used, and deployment structure."
    )
    cmo_task = (
        "Review the provided codebase context. Generate a cmo_state.md master index "
        "that defines the infrastructure, architecture, and feature landscape as the Digital Twin."
    )

    docs_dir = Path("docs")
    (docs_dir / "architecture").mkdir(parents=True, exist_ok=True)
    (docs_dir / "features").mkdir(parents=True, exist_ok=True)
    (docs_dir / "infrastructure").mkdir(parents=True, exist_ok=True)

    run_agent_to_file("historian",         model, historian_task, docs_dir / "architecture" / "historian_context.md",  context)
    run_agent_to_file("solution_architect", model, architect_task, docs_dir / "architecture" / "system_architecture.md", context)
    run_agent_to_file("cmo_analyst",        model, cmo_task,       docs_dir / "cmo_state.md",                           context)

    console.print("\n[bold green]Digital Twin Mapping Complete![/bold green]")
    console.print("Review the generated files in the [cyan]docs/[/cyan] directory.")

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main_menu():
    # Handle CLI subcommands — entry point in pyproject.toml calls main_menu() directly
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        print_header()
        if cmd == "init":
            init_agency()
        elif cmd == "list":
            browse_skills()
        elif cmd == "run":
            run_skill()
        elif cmd == "twin":
            map_digital_twin()
        elif cmd == "ollama":
            setup_ollama()
        elif cmd == "update":
            update_agency()
        else:
            console.print(
                f"[red]Unknown command: '{cmd}'[/red]\n"
                "Available: [cyan]init  list  run  twin  ollama  update[/cyan]\n"
                "Run [cyan]agency[/cyan] with no arguments for the interactive menu."
            )
        return

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
                "🔄 Update Skills (sync new skills from package)",
                "👥 Browse Organization Chart (list)",
                "⚡ Task a specific Skill (run)",
                "🦙 Ollama Setup (install / pull models)",
                "❌ Exit",
            ],
        ).ask()

        if not choice or "Exit" in choice:
            console.print("[dim]Shutting down Virtual IT Team. Goodbye![/dim]")
            break
        elif "init" in choice:
            init_agency()
        elif "Update Skills" in choice:
            update_agency()
        elif "list" in choice:
            browse_skills()
        elif "run" in choice:
            run_skill()
        elif "Ollama" in choice:
            setup_ollama()

        print("\n")

if __name__ == "__main__":
    main_menu()
