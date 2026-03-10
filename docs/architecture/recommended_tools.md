# Recommended Agency Tools

To maximize the effectiveness of the "Virtual IT Team" within premium agentic execution environments (like Gemini CLI, Cursor, or Roo Code), you should ensure the underlying host machine (or Docker container) has the following CLI tools installed and accessible on the `$PATH`.

When these tools are available, the respective personas will naturally invoke them via their `run_command` capabilities to perform their jobs.

## Quality Assurance & Security Division
Equip the QA and Security team with the tools to perform actual automated testing and static analysis.

| Persona / Skill | Recommended Tool | Purpose | Example Invocation |
| :--- | :--- | :--- | :--- |
| `application_security_engineer` | **Semgrep** (`semgrep`) | Static Application Security Testing (SAST). | `semgrep scan --config=auto` |
| `application_security_engineer` | **Trufflehog** (`trufflehog`) | Secret scanning and credential detection. | `trufflehog git file:///app` |
| `e2e_journey_tester` | **Playwright** (`npx playwright`) | Headless browser execution for E2E tests. | `npx playwright test` |
| `sre_cloud_architect` | **k6** (`k6`) | Load testing API endpoints. | `k6 run load_test.js` |

## Database & Architecture Division
Empower the architects and DBAs to manipulate infrastructure and schemas directly.

| Persona / Skill | Recommended Tool | Purpose | Example Invocation |
| :--- | :--- | :--- | :--- |
| `solution_architect` | **Mermaid CLI** (`mmdc`) | Compiling `.mermaid` markdown into PNG/SVG diagrams. | `mmdc -i architecture.mermaid -o diagram.png` |
| `relational_dba` | **Prisma CLI** (`npx prisma`) | Database schema management and migrations (Node/Typescript). | `npx prisma migrate dev` |
| `relational_dba` | **Alembic** (`alembic`) | Database migrations for Python ecosystems. | `alembic upgrade head` |
| `sre_cloud_architect` | **Docker** (`docker`, `docker-compose`) | Spinning up local test environments. | `docker-compose up -d redis` |
| `sre_cloud_architect` | **Terraform** (`terraform`) | Validating Infrastructure as Code (IaC) syntax and plans. | `terraform plan` |

## Management & Marketing Division
Give the organization leaders visibility into external systems.

| Persona / Skill | Recommended Tool | Purpose | Example Invocation |
| :--- | :--- | :--- | :--- |
| `project_manager` | **GitHub CLI** (`gh`) | Reading issues, translating them into tasks, opening PRs. | `gh issue view 123` |
| `cmo_analyst` | **Lighthouse CI** (`lhci`) | Ensuring the frontend meets performance, SEO, and accessibility constraints. | `lhci autorun` |

---

## Custom Tools via `Tool Smith`
If a skill requires a tool that doesn't exist as a neat, open-source CLI, invoke the `tool_smith` meta-skill to write a custom wrapper script (e.g., a Python script that calls a proprietary internal API) that can be consumed by the rest of the agency.
