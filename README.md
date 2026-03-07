# The Agency

## The Virtual IT Team in Your Pocket 🏢

"The Agency" is an open-source framework that models a complete, 28-person Enterprise Software Development Organization using specialized AI Personas (Skills).

Unlike traditional orchestration frameworks (like CrewAI, AutoGen, or LangGraph) that just provide the *code* to connect agents, `The Agency` provides the actual **Domain Knowledge, Organizational Chart, and Standard Operating Procedures (SOPs)** required to build robust software.

Simply inject these personas into your favorite AI tool (Cursor, Roo Code, Gemini CLI, or a local instance of Ollama) and watch the Virtual IT Team design, develop, secure, test, and market your application.

---

## 👥 The Organization Chart

The Virtual IT Team comprises specialized "Skills", mapped precisely to a modern tech enterprise:

- **Management:** `project_manager`, `historian`, `workspace_manager`
- **Architecture:** `solution_architect`, `cmo_analyst` (Digital Twin Owner), `sre_cloud_architect`
- **Development:** `backend_developer`, `frontend_developer`, `coder`
- **Design:** `ux_ui_designer`
- **Data Engineering:** `relational_dba`, `graph_database_architect`, `data_scientist`
- **Quality Assurance:** `chief_test_officer`, `qa_automation_engineer`, `test_engineer`, `e2e_journey_tester`, `test_data_manager`, `ui_qa_engineer`
- **Security:** `chief_information_security_officer`, `application_security_engineer`, `security_operations_analyst`
- **Deployment:** `ssdlc_manager`
- **Marketing & Comms:** `head_of_marketing`, `product_marketing_manager`, `content_copywriter`, `technical_writer`
- **Support & AI Ops:** `customer_support_triage`, `prompt_engineer`, `makefile_orchestrator`

*(Read each `SKILL.md` inside the `skills/` folder to review the specific heuristics and constraints of that role).*

---

## 🚀 How to Use "The Agency"

Because The Agency defines *logic* and *processes* rather than hard-coded python scripts, you can use it conceptually within any environment.

### 1. The Interactive Agency CLI (Recommended)
You can directly bootstrap and interact with the 28 agentic personas via our free, local CLI wrapper which leverages `Ollama`.

```bash
# 1. Install UI dependencies
pip install -r requirements.txt

# 2. Launch the Interactive Agency
python agency.py
```

The graphical menu will guide you through:
- **Initialize:** Easily copy the IT team into a hidden `.agency/` folder inside any existing codebase you own.
- **Browse Skills:** View the beautiful organization chart and understand what every department does.
- **Run Skill:** Choose a specific skill (e.g., `frontend_developer`), paste a task, and let your local Ollama model instantly code it for you.

### 2. In Premium Agentic Tools (Cursor, Roo Code, Copilot Workspaces)
Point your AI assistant at the specific `SKILL.md` you want it to embody. 
For example, tell Cursor: *"Embody the role defined in `skills/frontend_developer/SKILL.md` and complete this task."*

### 3. Pure Makefiles & Terminal Piping
If you prefer raw execution, you can completely ignore `.agency.py` and run sequential generation using the `Makefile` pattern.

**See the example `Makefile` in the root directory for a proof-of-concept pipeline.**

```bash
# Example: Generate an application schema using a local 8B model
make build-schema 
```

---

## 📦 Integrating into an Existing Project

If you are not starting from scratch, you can easily drop "The Agency" into a mature, existing repository to help you maintain it.

**1. Clone the Skills**
Clone this repository into a `.agency/` or `.skills/` hidden folder at the root of your existing project, or simply copy the `skills/` directory over.

**2. Initialize the "Digital Twin" (The Most Important Step)**
AI agents hallucinate when they don't know your existing architecture. Before asking the Agency to write new code for your existing app, you must map your current state:
*   **Call the `historian`:** Ask it to read your commit history and existing `README.md` to summarize the project's purpose.
*   **Call the `solution_architect`:** Ask it to analyze your `src/` directory and generate a `docs/architecture/system_diagram.mermaid` and a `data_models.md` file.
*   **Call the `cmo_analyst`:** Ask it to review the Architect's output and establish the official "Digital Twin" documentation rules for the project.

**3. Resume Normal Operations**
Once the `docs/` folder accurately reflects your existing application, you can initiate the `project_manager` with a new feature request. The PM will naturally consult the CMO Analyst, who will read your new Digital Twin, ensuring all new code injected by the Agency perfectly matches your existing styles and schemas!

---

## 🏗️ The Project Lifecycle

If you elect to use the full agency, follow the routing lifecycle governed by the `project_manager`:

1. **Discovery:** `cmo_analyst` checks the system's "Digital Twin" constraints (`docs/`).
2. **Design Blueprint:** `ux_ui_designer` maps the wireframes; `prompt_engineer` maps the LLM context flow.
3. **Architecture:** `solution_architect` defines the data models and component structure.
4. **Security Check:** `ciso` reviews the architecture for vulnerabilities. *(Must pass before coding).*
5. **Implementation:** Specialized `backend_developer` and `frontend_developer` write the code.
6. **Testing:** `chief_test_officer` coordinates unit, integration, and E2E tests.
7. **Deployment:** `sre_cloud_architect` dictates topology, and `ssdlc_manager` routes it to production.
8. **Launch:** The Marketing division generates go-to-market copy while the `technical_writer` builds the public APIs.

---

## 📜 Legacy Assets
Older, hard-coded Python SDK variants of this agentic framework have been archived in the `legacy/` folder for historical reference. The future of The Agency is agnostic, prompt-driven markdown injected into powerful local or cloud execution layers.

## Contributing
Want to add a new role to the IT Team? 
1. Copy an existing `SKILL.md`.
2. Define their Core Responsibilities and Workflow Integration.
3. Submit a PR.
