# Sentinel 🛡️ - Security Journal

This journal records CRITICAL security learnings for the Satya project.

## 2025-01-24 - [Command Injection in Completion Criteria]
**Vulnerability:** The `CompletionChecker.check` method used `subprocess.run(shell=True)` on a `test_command` string retrieved from task metadata. This allowed an AI agent (or anyone with access to task creation) to execute arbitrary shell commands by crafting a malicious `test_command` (e.g., using `;`, `&&`, or redirection).
**Learning:** Even if a feature is intended for automation by agents, executing strings as shell commands is a high-risk pattern. The application data model allows for complex task metadata that could be exploited if not handled defensively.
**Prevention:** Always use `shell=False` and `shlex.split()` to execute commands in Python. This treats the input as a command and its arguments, rather than as a single shell command string, preventing the use of shell-specific control characters and operators.
