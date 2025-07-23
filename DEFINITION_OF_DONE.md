# Definition of Done (DoD)

This document outlines the criteria that must be met for any new feature or change to be considered complete. It serves as a quality gate to ensure consistency, correctness, and maintainability.

A feature is considered **DONE** only when all the following criteria are met:

1.  **Feature Brief Complete:** The feature is implemented as described in its corresponding `Feature Brief` document.
2.  **Code Implemented:** All required code has been written and adheres to the project's existing style and conventions.
3.  **Tests Pass:** All existing and new unit/integration tests pass successfully.
4.  **New Tests Written:** New tests covering the core logic of the new feature have been added.
5.  **Documentation Updated:** The `README.md` and any other relevant documentation are updated to reflect the new changes.
6.  **TODO List Updated:** The `todo.txt` file is updated to mark the feature as complete.
7.  **Session State Cleared:** The `session.md` is updated to reflect the completion of the task and outline the next steps.
8.  **Code Committed:** All related changes are committed to Git with a conventional commit message (e.g., `feat:`, `fix:`, `docs:`).
9.  **Watchdog Compliance:** The implementation process did not trigger the Cyclic Error Watchdog. If it did, the final, successful approach is documented.
