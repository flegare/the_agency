--- Context from: ../.gemini/GEMINI.md ---
## Gemini Added Memories
- When starting a long-running server process like the Firebase emulator, do not run it directly in the foreground as it will block further interaction. Use a backgrounding method like a shell script with 'nohup' and '&'. Always verify the process is running with 'ps' and check logs before assuming it has failed. When troubleshooting network connections to a local server, if the server appears to be running on 0.0.0.0 but is still inaccessible from the network, the issue is likely with the user's network environment or firewall, and I should guide the user to check those settings rather than repeatedly trying to restart the server.
- This project's goal is to create a collection of specialized, independent agents that extend the Gemini CLI's capabilities.
- When using `run_shell_command` with `curl` to interact with agents, always include the `-s` (silent) flag to suppress progress meters and other diagnostic output, ensuring cleaner interaction and saving tokens.

py`, `new_agent/requirements.txt`).
- This project uses a PO, Architect, Coder, and Tester workflow.
--- End of Context from: ../.gemini/GEMINI.md ---
