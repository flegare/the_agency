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

UPDATE_AVAILABLE = None

def check_for_updates():
    """Background thread to check PyPI for a newer version of the CLI."""
    global UPDATE_AVAILABLE
    try:
        # Get the currently installed version
        current_version = importlib.metadata.version("the-agency-cli")
        
        # Ping PyPI, timeout quickly so it doesn't hang
        response = requests.get("https://pypi.org/pypi/the-agency-cli/json", timeout=1.5)
        if response.status_code == 200:
            latest_version = response.json()["info"]["version"]
            
            # Very basic semantic version comparison
            curr_parts = [int(p) for p in current_version.split('.') if p.isdigit()]
            latest_parts = [int(p) for p in latest_version.split('.') if p.isdigit()]
            
            if latest_parts > curr_parts:
                UPDATE_AVAILABLE = latest_version
    except Exception:
        pass # Fail silently (e.g., offline, or not installed via PyPI)

def print_header():
    console.print(Text(AGENCY_LOGO, style="bold cyan"))

def check_ollama(model="llama3.2"):
    """Check if Ollama is running and has the model."""
    try:
        subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
    except FileNotFoundError:
        console.print("[red]Error: 'ollama' CLI not found. Please install Ollama from ollama.com[/red]")
        sys.exit(1)
    except subprocess.CalledProcessError:
        console.print("[red]Error: Ollama is not running. Please start the Ollama application.[/red]")
        sys.exit(1)

def install_agency_skills():
    """Bootstrap .agency folder with skills."""
    if AGENCY_DIR.exists():
        console.print("[yellow]The Agency skills are already present in .agency/[/yellow]")
        return True
    
    if not SKILLS_SRC_DIR.exists():
        console.print("[red]Error: 'skills/' directory not found. Are you running this from the root of The Agency repo?[/red]")
        return False

    try:
        shutil.copytree(SKILLS_SRC_DIR, AGENCY_DIR / "skills")
        console.print("[green]Installed skills to .agency/skills/[/green]")
        return True
    except Exception as e:
        console.print(f"[red]Failed to install skills: {e}[/red]")
        return False

def inject_context(tool_name: str, file_path_str: str, instruction: str):
    """Injects Agency instructions into a tool's project memory file."""
    path = Path(file_path_str)
    try:
        if path.exists():
            content = path.read_text(encoding='utf-8')
            if "The Agency" in content:
                console.print(f"[yellow]{tool_name} already configured in {path}.[/yellow]")
                return True
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"\n\n{instruction}")
            console.print(f"[green]Appended Agency instructions to {path}[/green]")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(instruction, encoding='utf-8')
            console.print(f"[green]Created {path} with Agency instructions.[/green]")
        return True
    except Exception as e:
        console.print(f"[red]Failed to configure {tool_name}: {e}[/red]")
        return False

def auto_detect_and_install():
    if not install_agency_skills(): return
    instruction = (
        "## The Agency - Virtual IT Team\n"
        "This project is equipped with 'The Agency' organizational personas.\n"
        "To adopt a specialized skill for a task, read the corresponding persona definition located in the `.agency/skills/<skill_name>/SKILL.md` directory.\n"
        "When creating components, deploying infrastructure, or writing tests, ensure you adopt the relevant persona (e.g., `frontend_developer`, `sre_cloud_architect`, `chief_test_officer`) and strictly adhere to their Core Responsibilities and Workflow Integration rules.\n"
    )
    detected = False
    
    console.print(Panel("Scanning for AI Assistants...", style="cyan"))
    
    # Cursor
    if Path(".cursorrules").exists() or Path(".cursor").exists():
        inject_context("Cursor", ".cursorrules", instruction)
        detected = True
        
    # Roo Code / Cline
    if Path(".clinerules").exists() or Path(".clinerules").is_dir() or Path(".roomodes").exists():
        inject_context("Roo Code", ".clinerules", instruction)
        detected = True
        
    # Gemini
    if Path(".gemini").exists() or Path("GEMINI.md").exists() or Path(".agents").exists():
        inject_context("Gemini", "GEMINI.md", instruction)
        detected = True
        
    # Claude Code
    if Path(".claude").exists() or Path("CLAUDE.md").exists():
        inject_context("Claude", "CLAUDE.md", instruction)
        detected = True
        
    # Aider
    if Path(".aider.conf.yml").exists() or Path(".aider.chat.history.md").exists():
         inject_context("Aider", "CONVENTIONS.md", instruction)
         detected = True
        
    if not detected:
        console.print("[yellow]No popular AI assistant context files detected natively. Try manual installation.[/yellow]")
    else:
        console.print("\n[bold green]Success![/bold green] The Virtual IT team is ready to assist your AI.")

def manual_install():
    if not install_agency_skills(): return
    instruction = (
        "## The Agency - Virtual IT Team\n"
        "This project is equipped with 'The Agency' organizational personas.\n"
        "To adopt a specialized skill for a task, read the corresponding persona definition located in the `.agency/skills/<skill_name>/SKILL.md` directory.\n"
        "When creating components, deploying infrastructure, or writing tests, ensure you adopt the relevant persona (e.g., `frontend_developer`, `sre_cloud_architect`, `chief_test_officer`) and strictly adhere to their Core Responsibilities and Workflow Integration rules.\n"
    )
    choices = [
        questionary.Choice("Cursor (.cursorrules)", value="cursor"),
        questionary.Choice("Roo Code / Cline (.clinerules)", value="roo"),
        questionary.Choice("Gemini CLI (GEMINI.md)", value="gemini"),
        questionary.Choice("Claude Code (CLAUDE.md)", value="claude"),
        questionary.Choice("Aider (CONVENTIONS.md)", value="aider")
    ]
    
    selected = questionary.checkbox(
        "Select AI Assistants to configure:", 
        choices=choices
    ).ask()
    
    if not selected:
         return
         
    for choice in selected:
         if "cursor" == choice: inject_context("Cursor", ".cursorrules", instruction)
         if "roo" == choice: inject_context("Roo Code", ".clinerules", instruction)
         if "gemini" == choice: inject_context("Gemini", "GEMINI.md", instruction)
         if "claude" == choice: inject_context("Claude", "CLAUDE.md", instruction)
         if "aider" == choice: inject_context("Aider", "CONVENTIONS.md", instruction)
         
    console.print("\n[bold green]Success![/bold green] The Virtual IT team is ready to assist your AI.")

def init_agency():
    """Interactive Init Menu"""
    while True:
        console.print(Panel("Initialization Options", style="bold green"))
        choice = questionary.select(
            "How would you like to initialize The Agency?",
            choices=[
                "🔍 Auto-detect AI Assistants & Install (.cursorrules, GEMINI.md, etc.)",
                "🛠️  Manual AI Assistant Selection",
                "🗺️  Initialize Project (Map Digital Twin with Historian)",
                "🔙 Back"
            ]
        ).ask()
        
        if not choice or "Back" in choice:
            break
        elif "Auto-detect" in choice:
            auto_detect_and_install()
        elif "Manual" in choice:
            manual_install()
        elif "Initialize Project" in choice:
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
    flat_skills = [skill for dept in SKILL_CATEGORIES.values() for skill in dept]
    
    skill_choice = questionary.autocomplete(
        'Which skill would you like to employ?',
        choices=flat_skills
    ).ask()
    
    if not skill_choice:
        return
        
    # Check if we are running in the main repo or an initialized repo
    skill_path_main = SKILLS_SRC_DIR / skill_choice / "SKILL.md"
    skill_path_agency = AGENCY_DIR / "skills" / skill_choice / "SKILL.md"
    
    active_path = None
    if skill_path_agency.exists():
        active_path = skill_path_agency
    elif skill_path_main.exists():
        active_path = skill_path_main
        
    if not active_path:
        console.print(f"[red]Could not find SKILL.md for {skill_choice}[/red]")
        return
        
    task_input = questionary.text("Describe the task you want this skill to perform:").ask()
    
    if not task_input:
        return
    
    model = questionary.text("Which local Ollama model?", default="llama3.2").ask()
    
    console.print(f"\n[bold yellow]Dispatching task to {skill_choice}...[/bold yellow]\n")
    
    # Read skill context
    with open(active_path, "r", encoding="utf-8") as f:
        skill_context = f.read()
        
    prompt = f"{skill_context}\n\nTASK: {task_input}"
    
    try:
        # Use subprocess to stream output directly to terminal
        subprocess.run(
            ["ollama", "run", model],
            input=prompt.encode("utf-8"),
            check=True
        )
    except subprocess.CalledProcessError as e:
        console.print(f"\n[red]Ollama pipeline failed: {e}[/red]")

def gather_codebase_context() -> str:
    """Scan the root directory for standard files and capture a directory listing."""
    console.print("[dim]Gathering codebase context (root directory files and listing)...[/dim]")
    context_parts = []
    
    # 1. Directory Listing (top-level only to avoid massive outputs)
    try:
        context_parts.append("### Project Root Directory Listing ###")
        listing = []
        for item in Path('.').iterdir():
            # Skip common ignores
            if item.name in ('.git', '.venv', 'node_modules', '.idea', '__pycache__', '.agency'):
                continue
            item_type = "(DIR)" if item.is_dir() else "(FILE)"
            listing.append(f"{item_type} {item.name}")
        context_parts.append("\n".join(listing))
    except Exception as e:
        context_parts.append(f"Error gathering directory listing: {e}")

    # 2. Key Files
    key_files = [
        "README.md", "README.txt", "README",
        "requirements.txt", "Pipfile", "pyproject.toml", "poetry.lock",
        "package.json", "yarn.lock", "package-lock.json",
        "docker-compose.yml", "Dockerfile",
        "Makefile", "build.gradle", "pom.xml"
    ]
    
    for filename in key_files:
        filepath = Path(filename)
        if filepath.exists() and filepath.is_file():
            try:
                content = filepath.read_text(encoding='utf-8')
                # Truncate extremely large files just in case
                if len(content) > 20000:
                    content = content[:20000] + "\n...[TRUNCATED]..."
                context_parts.append(f"\n### File: {filename} ###\n```\n{content}\n```")
            except Exception as e:
                console.print(f"[yellow]Could not read {filename}: {e}[/yellow]")
    
    return "\n\n".join(context_parts)

def run_agent_to_file(skill_choice: str, model: str, task_input: str, output_file: Path, context: str = ""):
    """Run an agent and redirect stdout to an output file."""
    skill_path_main = SKILLS_SRC_DIR / skill_choice / "SKILL.md"
    skill_path_agency = AGENCY_DIR / "skills" / skill_choice / "SKILL.md"
    
    active_path = None
    if skill_path_agency.exists():
        active_path = skill_path_agency
    elif skill_path_main.exists():
        active_path = skill_path_main
        
    if not active_path:
        console.print(f"[red]Could not find SKILL.md for {skill_choice}[/red]")
        return False
        
    # Read skill context
    with open(active_path, "r", encoding="utf-8") as f:
        skill_context = f.read()
        
    prompt = f"{skill_context}\n\nTASK: {task_input}"
    if context:
         prompt += f"\n\nCODEBASE CONTEXT:\n{context}"
    
    # Ensure directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    console.print(f"\n[bold yellow]Dispatching {skill_choice} to generate {output_file.name}...[/bold yellow]")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as out_f:
            # We don't pipe stderr to file, but we capture output to file
            subprocess.run(
                ["ollama", "run", model],
                input=prompt.encode("utf-8"),
                stdout=out_f,
                check=True
            )
        console.print(f"[green]Successfully generated: {output_file}[/green]")
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"\n[red]Ollama pipeline failed for {skill_choice}: {e}[/red]")
        return False


def map_digital_twin():
    """Automate the mapping of the existing codebase to build the Digital Twin."""
    console.print(Panel("🗺️  Mapping the Digital Twin", style="bold magenta"))
    console.print("This process will read your current repository structure, READMEs, and configuration files.")
    console.print("This will execute the Historian, Solution Architect, and CMO Analyst to build state.\n")
    
    confirm = questionary.confirm("Are you ready to automate your codebase mapping?").ask()
    if not confirm:
        return
        
    model = questionary.text("Which local Ollama model?", default="llama3.2").ask()
    if not model:
        return
        
    # Gather context
    context = gather_codebase_context()
    
    # Define tasks
    historian_task = "Analyze the provided project context (files and structure). Provide a summary of what this project is, its history (if discernible), and its key components. Create a 'historian_context.md' summarizing the current state of the project."
    architect_task = "Review the provided codebase context. Generate a 'system_architecture.md' document outlining your best guess at the system's architecture, technologies used, and deployment structure."
    cmo_task = "Review the provided codebase context and the initial state. Generate a 'cmo_state.md' document. This should act as the master index and starting point for the Digital Twin, defining the infrastructure, architecture, and feature landscape based on your findings."
    
    docs_dir = Path("docs")
    if not docs_dir.exists():
         (docs_dir / "architecture").mkdir(parents=True, exist_ok=True)
         (docs_dir / "features").mkdir(exist_ok=True)
         (docs_dir / "infrastructure").mkdir(exist_ok=True)
    
    # Run Agents
    run_agent_to_file("historian", model, historian_task, docs_dir / "architecture" / "historian_context.md", context)
    run_agent_to_file("solution_architect", model, architect_task, docs_dir / "architecture" / "system_architecture.md", context)
    run_agent_to_file("cmo_analyst", model, cmo_task, docs_dir / "cmo_state.md", context)
    
    console.print("\n[bold green]Digital Twin Mapping Complete![/bold green]")
    console.print("Review the generated files in the 'docs/' directory.")

def main_menu():
    # Start the update check in the background immediately
    threading.Thread(target=check_for_updates, daemon=True).start()
    
    print_header()
    
    while True:
        if UPDATE_AVAILABLE:
            console.print(Panel(
                f"[bold yellow]Update Available![/bold yellow] Version {UPDATE_AVAILABLE} of The Agency is out.\n"
                f"Run [cyan]pipx upgrade the-agency-cli[/cyan] to get the latest skills and tools.", 
                border_style="yellow"
            ))
            
        choice = questionary.select(
            "Welcome to The Agency. How can the IT Team assist you today?",
            choices=[
                "🚀 Initialize / Configure Project (init)",
                "👥 Browse Organization Chart (list)",
                "⚡ Task a specific Skill (run)",
                "❌ Exit"
            ]
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
    if len(sys.argv) > 1:
        # Command line arguments override interactive menu
        cmd = sys.argv[1].lower()
        if cmd == "init":
            init_agency()
        elif cmd == "list":
            browse_skills()
        elif cmd == "run":
            run_skill()
        elif cmd == "twin":
            map_digital_twin()
        else:
            console.print("[red]Unknown command. Run without arguments for interactive menu.[/red]")
    else:
        # Start interactive
        main_menu()
