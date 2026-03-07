import os
import sys
import shutil
import subprocess
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
SKILLS_SRC_DIR = Path("skills")

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

def init_agency():
    """Bootstrap .agency folder."""
    console.print(Panel("Initializing The Agency...", style="bold green"))
    
    if AGENCY_DIR.exists():
        console.print("[yellow]The Agency is already initialized in this repository (.agency/ exists).[/yellow]")
        return
    
    if not SKILLS_SRC_DIR.exists():
        console.print("[red]Error: 'skills/' directory not found. Are you running this from the root of The Agency repo?[/red]")
        return

    try:
        shutil.copytree(SKILLS_SRC_DIR, AGENCY_DIR / "skills")
        # Setup Digital Twin folders
        docs_dir = Path("docs")
        if not docs_dir.exists():
            (docs_dir / "architecture").mkdir(parents=True)
            (docs_dir / "features").mkdir()
            (docs_dir / "infrastructure").mkdir()
            console.print("[green]Created Digital Twin documentation folders at ./docs/[/green]")
            
        console.print("[bold green]Success![/bold green] The Agency has been installed in .agency/")
        console.print("You can now safely commit your project. The Virtual IT team is ready to assist.")
    except Exception as e:
        console.print(f"[red]Failed to initialize: {e}[/red]")

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

def map_digital_twin():
    """Guide the user to map their existing codebase."""
    console.print(Panel("🗺️  Mapping the Digital Twin", style="bold magenta"))
    console.print("Before asking The Agency to write new code, the AI needs to understand your *existing* codebase.")
    console.print("This process will ask the Historian, Architect, and CMO Analyst to read your repo.\n")
    
    confirm = questionary.confirm("Are you ready to map your codebase?").ask()
    if not confirm:
        return
        
    console.print("[yellow]Notice: Full automated codebase mapping requires parsing multiple files into context.[/yellow]")
    console.print("For this V1 CLI, we recommend navigating to the CLI and running specific commands.")
    console.print("Try running: [cyan]agency.py run historian[/cyan] and pasting your README.")

def main_menu():
    print_header()
    
    while True:
        choice = questionary.select(
            "Welcome to The Agency. How can the IT Team assist you today?",
            choices=[
                "🚀 Initialize The Agency in this Project (init)",
                "👥 Browse Organization Chart (list)",
                "🗺️  Map Digital Twin for Existing Project (twin)",
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
        elif "twin" in choice:
            map_digital_twin()
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
        else:
            console.print("[red]Unknown command. Run without arguments for interactive menu.[/red]")
    else:
        # Start interactive
        main_menu()
