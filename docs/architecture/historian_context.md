This is a Makefile for managing the development and deployment of an AI-powered shopping experience. It consists of 28 tasks, each representing a step in the pipeline. Here's a breakdown of the tasks:

**Phase 1: Project Initialization**

1. `28_historian_archive.md`: The final step, which summarizes the completion of the project.
2. `27_triage_sop.md`: An SOP for level 1 support, indicating how to respond to users who say "The recommendations are completely wrong!".
3. `26_tech_writer_api.md`: API documentation for the new Recommendation APIs.
4. `25_copywriter_assets.md`: Copywriting assets for the email newsletter announcing the new AI-powered shopping experience.
5. `24_pmm_positioning.md`: Messaging pillars for the AI recommendation feature.

**Phase 2: Marketing and GTM**

6. `23_hom_strategy.md`: GTM strategy for the AI feature, defining target audiences and channels.
7. `22_ssdlc_deploy.sh`: Deployment pipeline script that applies Terraform and waits for health checks.
8. `21_sre_topology.tf`: Terraform blueprint describing an AWS ALB, Auto-Scaling Group, and RDS instance.
9. `20_soc_monitoring.yml`: Prometheus/Alertmanager YAML configuration for monitoring and alerts.
10. `19_ui_qa_report.md`: UI QA report, outlining the checklist for verifying the recommendation carousel meets WCAG accessibility and brand design constraints.

**Phase 3: Quality Assurance**

11. `18_e2e_tests.js`: Playwright script simulating a user clicking a recommended product based on history.
12. `17_unit_tests.py`: Pytest functions for testing the backend API logic.
13. `16_test_data.json`: JSON array of 3 mock users with simulated browsing histories for testing the recommendation engine.
14. `15_qa_pipeline.yml`: GitHub Actions YAML configuration for running unit, E2E, and DAST scans.

**Phase 4: Testing**

15. `14_cto_strategy.md`: CTO strategy outlining the testing strategy required for the AI feature.
16. `13_ui_qa_report.md`: UI QA report, outlining the checklist for verifying the recommendation carousel meets WCAG accessibility and brand design constraints.
17. `12_e2e_tests.py`: Pytest functions for testing the E2E journey.
18. `11_unit_tests.py`: Pytest functions for testing the backend API logic.
19. `10_cto_strategy.md`: CTO strategy outlining the testing strategy required for the AI feature.

**Phase 5: Deployment**

20. `9_ssdlc_deploy.sh`: Deployment pipeline script that applies Terraform and waits for health checks.
21. `8_sre_topology.tf`: Terraform blueprint describing an AWS ALB, Auto-Scaling Group, and RDS instance.
22. `7_ssdlc_deploy.sh`: Deployment pipeline script that applies Terraform and waits for health checks.
23. `6_sre_topology.tf`: Terraform blueprint describing an AWS ALB, Auto-Scaling Group, and RDS instance.
24. `5_sre_topology.tf`: Terraform blueprint describing an AWS ALB, Auto-Scaling Group, and RDS instance.

**Phase 6: Testing and Debugging**

25. `4_sre_topology.tf`: Terraform blueprint describing an AWS ALB, Auto-Scaling Group, and RDS instance.
26. `3_sre_topology.tf`: Terraform blueprint describing an AWS ALB, Auto-Scaling Group, and RDS instance.
27. `2_sre_topology.tf`: Terraform blueprint describing an AWS ALB, Auto-Scaling Group, and RDS instance.
28. `1_sre_topology.tf`: Terraform blueprint describing an AWS ALB, Auto-Scaling Group, and RDS instance.

**Macros**

The following macros are defined:

* `all-28`: Runs the full 28 steps.
* `test-fast`: Runs a very fast test of just the first 3 steps to verify Ollama is working.

**Makefile Targets**

The following targets are defined:

* `28_historian_archive.md`: Runs the final step of the project.
* `27_triage_sop.md`: Runs the SOP for level 1 support.
* `26_tech_writer_api.md`: Runs the API documentation for the new Recommendation APIs.
* `25_copywriter_assets.md`: Runs the copywriting assets for the email newsletter.
* `24_pmm_positioning.md`: Runs the messaging pillars for the AI recommendation feature.
* `23_hom_strategy.md`: Runs the GTM strategy for the AI feature.
* `22_ssdlc_deploy.sh`: Runs the deployment pipeline script.
* `21_sre_topology.tf`: Runs the Terraform blueprint for the AWS ALB, Auto-Scaling Group, and RDS instance.
* `20_soc_monitoring.yml`: Runs the Prometheus/Alertmanager YAML configuration.
* `19_ui_qa_report.md`: Runs the UI QA report.
* `18_e2e_tests.js`: Runs the Playwright script simulating a user clicking a recommended product based on history.
* `17_unit_tests.py`: Runs the Pytest functions for testing the backend API logic.
* `16_test_data.json`: Runs the JSON array of 3 mock users with simulated browsing histories.
* `15_qa_pipeline.yml`: Runs the GitHub Actions YAML configuration for running unit, E2E, and DAST scans.
* `14_cto_strategy.md`: Runs the CTO strategy outlining the testing strategy required for the AI feature.
* `13_ui_qa_report.md`: Runs the UI QA report.
* `12_e2e_tests.py`: Runs the Pytest functions for testing the E2E journey.
* `11_unit_tests.py`: Runs the Pytest functions for testing the backend API logic.
* `10_cto_strategy.md`: Runs the CTO strategy outlining the testing strategy required for the AI feature.
* `9_ssdlc_deploy.sh`: Runs the deployment pipeline script.
* `8_sre_topology.tf`: Runs the Terraform blueprint for the AWS ALB, Auto-Scaling Group, and RDS instance.
* `7_ssdlc_deploy.sh`: Runs the deployment pipeline script.
* `6_sre_topology.tf`: Runs the Terraform blueprint for the AWS ALB, Auto-Scaling Group, and RDS instance.
* `5_sre_topology.tf`: Runs the Terraform blueprint for the AWS ALB, Auto-Scaling Group, and RDS instance.
* `4_sre_topology.tf`: Runs the Terraform blueprint for the AWS ALB, Auto-Scaling Group, and RDS instance.
* `3_sre_topology.tf`: Runs the Terraform blueprint for the AWS ALB, Auto-Scaling Group, and RDS instance.
* `2_sre_topology.tf`: Runs the Terraform blueprint for the AWS ALB, Auto-Scaling Group, and RDS instance.
* `1_sre_topology.tf`: Runs the Terraform blueprint for the AWS ALB, Auto-Scaling Group, and RDS instance.
* `test-fast`: Runs a very fast test of just the first 3 steps to verify Ollama is working.
* `all-28`: Runs the full 28 steps.

