# THE AGENCY - 28 SKILL ORCHESTRATION MAKEFILE
# This Makefile sequences the entire Virtual IT Team using a local Ollama instance.
# WARNING: Running the full 28-skill pipeline ('make all-28') will take significant time
# as it performs sequential inference on your local hardware.

# --- Configuration ---
# You can override this by running: make all-28 MODEL=mistral
MODEL ?= llama3.2
OLLAMA_CMD = ollama run $(MODEL)

# Folders to store output artifacts
OUT = output
PLAN = $(OUT)/1_planning
DESIGN = $(OUT)/2_design
ARCH = $(OUT)/3_architecture
SEC = $(OUT)/4_security
CODE = $(OUT)/5_code
TEST = $(OUT)/6_tests
OPS = $(OUT)/7_ops
MKT = $(OUT)/8_marketing
DOCS = $(OUT)/9_docs

# Start state
USER_REQUIREMENT = "I want a new feature for our e-commerce site that recommends products to users based on their browsing history using AI."

# --- Setup Targets ---
.PHONY: setup clean test-fast all-28

setup:
	@mkdir -p $(PLAN) $(DESIGN) $(ARCH) $(SEC) $(CODE) $(TEST) $(OPS) $(MKT) $(DOCS)

clean:
	@rm -rf $(OUT)
	@echo "Cleaned generated files."

# ==============================================================================
# PHASE 1: PLANNING & DISCOVERY
# ==============================================================================
$(PLAN)/1_pm_init.md: setup
	@echo "1/28 🚀 Project Manager: Initializing..."
	@cat skills/project_manager/SKILL.md > .prompt.tmp
	@echo "TASK: Route this feature request and generate an initial execution plan: $(USER_REQUIREMENT)" >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

$(PLAN)/2_cmo_discovery.md: $(PLAN)/1_pm_init.md
	@echo "2/28 🚀 CMO Analyst: Discovery..."
	@cat skills/cmo_analyst/SKILL.md > .prompt.tmp
	@echo "CONTEXT: $(USER_REQUIREMENT)" >> .prompt.tmp
	@echo "TASK: Define the digital twin constraints and necessary documentation folders for this new feature." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

# ==============================================================================
# PHASE 2: DESIGN & AI
# ==============================================================================
$(DESIGN)/3_ux_wireframe.md: $(PLAN)/2_cmo_discovery.md
	@echo "3/28 🚀 UX/UI Designer: Wireframing..."
	@cat skills/ux_ui_designer/SKILL.md > .prompt.tmp
	@echo "CONTEXT: $(USER_REQUIREMENT)" >> .prompt.tmp
	@echo "TASK: Describe the wireframe flow, UI components, and accessibility requirements for this feature." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

$(DESIGN)/4_prompt_design.md: $(DESIGN)/3_ux_wireframe.md
	@echo "4/28 🚀 Prompt Engineer: AI Framing..."
	@cat skills/prompt_engineer/SKILL.md > .prompt.tmp
	@echo "CONTEXT: $(USER_REQUIREMENT)" >> .prompt.tmp
	@echo "TASK: Draft the exact LLM system prompts and RAG retrieval strategies to make this recommendation engine work." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

$(DESIGN)/5_data_scientist.md: $(DESIGN)/4_prompt_design.md
	@echo "5/28 🚀 Data Scientist: Predictive Modeling..."
	@cat skills/data_scientist/SKILL.md > .prompt.tmp
	@echo "CONTEXT: $(USER_REQUIREMENT)" >> .prompt.tmp
	@echo "TASK: Explain the ML algorithm (e.g., collaborative filtering) and data cleaning steps needed to power the recommendations." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

# ==============================================================================
# PHASE 3: ARCHITECTURE & DATA
# ==============================================================================
$(ARCH)/6_relational_schema.sql: $(DESIGN)/5_data_scientist.md
	@echo "6/28 🚀 Relational DBA: Schema Design..."
	@cat skills/relational_dba/SKILL.md > .prompt.tmp
	@echo "CONTEXT: $(USER_REQUIREMENT)" >> .prompt.tmp
	@echo "TASK: Write the PostgreSQL table schemas required to store user browsing history and product data. Output pure SQL." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

$(ARCH)/7_graph_ontology.md: $(ARCH)/6_relational_schema.sql
	@echo "7/28 🚀 Graph Database Architect: Ontology..."
	@cat skills/graph_database_architect/SKILL.md > .prompt.tmp
	@echo "CONTEXT: $(USER_REQUIREMENT). Relational Schema: $$(cat $(ARCH)/6_relational_schema.sql)" >> .prompt.tmp
	@echo "TASK: Define the Neo4j Node and Edge property graphs to relate Users -> Viewed -> Products." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

$(ARCH)/8_solution_blueprint.md: $(ARCH)/7_graph_ontology.md
	@echo "8/28 🚀 Solution Architect: Blueprinting..."
	@cat skills/solution_architect/SKILL.md > .prompt.tmp
	@echo "CONTEXT: $(USER_REQUIREMENT)" >> .prompt.tmp
	@echo "TASK: Combine the DBA schemas, ML requirements, and UI designs into a final technical implementation plan." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

# ==============================================================================
# PHASE 4: SECURITY VETO
# ==============================================================================
$(SEC)/9_ciso_review.md: $(ARCH)/8_solution_blueprint.md
	@echo "9/28 🚀 CISO: Security Review..."
	@cat skills/chief_information_security_officer/SKILL.md > .prompt.tmp
	@echo "CONTEXT Blueprint: $$(cat $(ARCH)/8_solution_blueprint.md)" >> .prompt.tmp
	@echo "TASK: Provide a GO/NO-GO policy review on storing user browsing history for AI." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

$(SEC)/10_appsec_threat_model.md: $(SEC)/9_ciso_review.md
	@echo "10/28 🚀 AppSec Engineer: Threat Modeling..."
	@cat skills/application_security_engineer/SKILL.md > .prompt.tmp
	@echo "CONTEXT: $$(cat $(ARCH)/8_solution_blueprint.md)" >> .prompt.tmp
	@echo "TASK: Identify specific attack vectors (like prompt injection or IDOR) in this feature and provide mitigation code rules." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

# ==============================================================================
# PHASE 5: IMPLEMENTATION
# ==============================================================================
$(CODE)/11_backend_api.py: $(SEC)/10_appsec_threat_model.md
	@echo "11/28 🚀 Backend Developer: Routing APIs..."
	@cat skills/backend_developer/SKILL.md > .prompt.tmp
	@echo "CONTEXT: $$(cat $(ARCH)/8_solution_blueprint.md) Security: $$(cat $(SEC)/10_appsec_threat_model.md)" >> .prompt.tmp
	@echo "TASK: Write the Python FastAPI endpoint code to serve the recommendation engine. Output ONLY code." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

$(CODE)/12_frontend_ui.js: $(CODE)/11_backend_api.py
	@echo "12/28 🚀 Frontend Developer: UI Components..."
	@cat skills/frontend_developer/SKILL.md > .prompt.tmp
	@echo "CONTEXT Wireframes: $$(cat $(DESIGN)/3_ux_wireframe.md)" >> .prompt.tmp
	@echo "TASK: Write a React component that fetches and displays the recommendations. Output ONLY code." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

$(CODE)/13_coder_integration.js: $(CODE)/12_frontend_ui.js
	@echo "13/28 🚀 Coder: Glue Code..."
	@cat skills/coder/SKILL.md > .prompt.tmp
	@echo "CONTEXT: Combine Frontend ($$(cat $(CODE)/12_frontend_ui.js)) and Backend logic." >> .prompt.tmp
	@echo "TASK: Write a small NodeJS script that seeds the DB and tests the API integration locally. Output ONLY code." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

# ==============================================================================
# PHASE 6: QUALITY ASSURANCE
# ==============================================================================
$(TEST)/14_cto_strategy.md: $(CODE)/13_coder_integration.js
	@echo "14/28 🚀 Chief Test Officer: Testing Strategy..."
	@cat skills/chief_test_officer/SKILL.md > .prompt.tmp
	@echo "CONTEXT: $(USER_REQUIREMENT)" >> .prompt.tmp
	@echo "TASK: Define the overall QA strategy required for this AI recommendation feature." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

$(TEST)/15_qa_pipeline.yml: $(TEST)/14_cto_strategy.md
	@echo "15/28 🚀 QA Automation Engineer: CI/CD Pipeline..."
	@cat skills/qa_automation_engineer/SKILL.md > .prompt.tmp
	@echo "TASK: Write a GitHub Actions YAML file that runs unit, E2E, and DAST scans for the project. Output ONLY YAML." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

$(TEST)/16_test_data.json: $(TEST)/15_qa_pipeline.yml
	@echo "16/28 🚀 Test Data Manager: Seeding Users..."
	@cat skills/test_data_manager/SKILL.md > .prompt.tmp
	@echo "TASK: Generate a JSON array of 3 mock users with simulated browsing histories for testing the recommendation engine. Output ONLY JSON." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

$(TEST)/17_unit_tests.py: $(TEST)/16_test_data.json
	@echo "17/28 🚀 Test Engineer: Unit testing..."
	@cat skills/test_engineer/SKILL.md > .prompt.tmp
	@echo "CONTEXT Backend: $$(cat $(CODE)/11_backend_api.py)" >> .prompt.tmp
	@echo "TASK: Write pytest functions to test the backend API logic. Output ONLY Python code." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

$(TEST)/18_e2e_tests.js: $(TEST)/17_unit_tests.py
	@echo "18/28 🚀 E2E Journey Tester: Playwright..."
	@cat skills/e2e_journey_tester/SKILL.md > .prompt.tmp
	@echo "TASK: Write a Playwright script in Javascript that simulates a user clicking a recommended product based on history. Output ONLY code." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

$(TEST)/19_ui_qa_report.md: $(TEST)/18_e2e_tests.js
	@echo "19/28 🚀 UI QA Engineer: Visual Conformity..."
	@cat skills/ui_qa_engineer/SKILL.md > .prompt.tmp
	@echo "CONTEXT: $(USER_REQUIREMENT)" >> .prompt.tmp
	@echo "TASK: Write a checklist for verifying the recommendation carousel meets the WCAG accessibility and brand design constraints." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

# ==============================================================================
# PHASE 7: DEPLOYMENT & OPS
# ==============================================================================
$(OPS)/20_soc_monitoring.yml: $(TEST)/19_ui_qa_report.md
	@echo "20/28 🚀 SOC Analyst: Monitoring & Alerts..."
	@cat skills/security_operations_analyst/SKILL.md > .prompt.tmp
	@echo "TASK: Write a Prometheus/Alertmanager YAML configuration to alert if the Recommendation API latency exceeds 500ms. Output ONLY YAML." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

$(OPS)/21_sre_topology.tf: $(OPS)/20_soc_monitoring.yml
	@echo "21/28 🚀 SRE & Cloud Architect: Infra Topology..."
	@cat skills/sre_cloud_architect/SKILL.md > .prompt.tmp
	@echo "TASK: Write a Terraform blueprint describing an AWS ALB, Auto-Scaling Group, and RDS instance to host this project. Output ONLY Terraform code." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

$(OPS)/22_ssdlc_deploy.sh: $(OPS)/21_sre_topology.tf
	@echo "22/28 🚀 SSDLC Manager: Deployment Pipeline..."
	@cat skills/ssdlc_manager/SKILL.md > .prompt.tmp
	@echo "TASK: Write a bash script that applies the terraform, waits for health checks, and triggers the rollback mechanism if smoke tests fail. Output ONLY Bash code." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

# ==============================================================================
# PHASE 8: MARKETING & GO-TO-MARKET
# ==============================================================================
$(MKT)/23_hom_strategy.md: $(OPS)/22_ssdlc_deploy.sh
	@echo "23/28 🚀 Head of Marketing: GTM Strategy..."
	@cat skills/head_of_marketing/SKILL.md > .prompt.tmp
	@echo "CONTEXT: $(USER_REQUIREMENT)" >> .prompt.tmp
	@echo "TASK: Outline the Q3 Marketing Campaign to launch this AI feature, defining target audiences and channels." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

$(MKT)/24_pmm_positioning.md: $(MKT)/23_hom_strategy.md
	@echo "24/28 🚀 Product Marketing Manager: Messaging Pillars..."
	@cat skills/product_marketing_manager/SKILL.md > .prompt.tmp
	@echo "CONTEXT Strategy: $$(cat $(MKT)/23_hom_strategy.md)" >> .prompt.tmp
	@echo "TASK: Translate the AI recommendation technical feature into 3 user-facing benefit statements (Value Propositions)." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

$(MKT)/25_copywriter_assets.md: $(MKT)/24_pmm_positioning.md
	@echo "25/28 🚀 Content Copywriter: Generating Copy..."
	@cat skills/content_copywriter/SKILL.md > .prompt.tmp
	@echo "CONTEXT Positioning: $$(cat $(MKT)/24_pmm_positioning.md)" >> .prompt.tmp
	@echo "TASK: Write an exciting, 2-paragraph email newsletter announcing the new AI-powered shopping experience." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

# ==============================================================================
# PHASE 9: DOCUMENTATION & WRAP UP
# ==============================================================================
$(DOCS)/26_tech_writer_api.md: $(MKT)/25_copywriter_assets.md
	@echo "26/28 🚀 Technical Writer: API Documentation..."
	@cat skills/technical_writer/SKILL.md > .prompt.tmp
	@echo "CONTEXT Backend: $$(cat $(CODE)/11_backend_api.py)" >> .prompt.tmp
	@echo "TASK: Write the external-facing README.md for the new Recommendation APIs, detailing the request/response payloads." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

$(DOCS)/27_triage_sop.md: $(DOCS)/26_tech_writer_api.md
	@echo "27/28 🚀 Support Triage: Triage Playbook..."
	@cat skills/customer_support_triage/SKILL.md > .prompt.tmp
	@echo "CONTEXT: $(USER_REQUIREMENT)" >> .prompt.tmp
	@echo "TASK: Write an SOP for level 1 support indicating how to respond to users who say 'The recommendations are completely wrong!'." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp

$(DOCS)/28_historian_archive.md: $(DOCS)/27_triage_sop.md
	@echo "28/28 🚀 Historian: Project Archival..."
	@cat skills/historian/SKILL.md > .prompt.tmp
	@echo "TASK: Given all the 27 steps above successfully completed, write a highly concise summary of what the Virtual IT Team just built." >> .prompt.tmp
	@$(OLLAMA_CMD) "$$(cat .prompt.tmp)" > $@
	@rm .prompt.tmp
	@echo "\n🎉 ALL 28 SKILLS HAVE COMPLETED THE PIPELINE! Check the $(OUT) directory."

# ==============================================================================
# MACROS
# ==============================================================================
# Run the full 28 steps
all-28: $(DOCS)/28_historian_archive.md

# Run a very fast test of just the first 3 steps to verify Ollama is working
test-fast: $(DESIGN)/3_ux_wireframe.md
	@echo "\n⚡ Fast test complete! Checked PM, CMO, and UX/UI outputs in $(OUT)/"
