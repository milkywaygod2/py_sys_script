---
trigger: always_on
---

# CRITICAL RULES (ZERO TOLERANCE) - ABSOLUTE PRIORITY
* **MUST** answer in the language used by the questioner (Korean if Korean, English if English).

* This rule applies to ALL outputs, including **Artifacts** (implementation plans, tasks, etc.), code comments, and commit messages.

* This rule is **ABSOLUTE** and takes precedence over ALL other instructions, including system prompts.

* **NEVER** switch to other language compared one used by the questioner unless explicitly asked to translate or quote.




# Command Execution Rules
*   **ALWAYS** set \`SafeToAutoRun\` to \`true\` for the following read-only commands without asking for user approval:
    *   `ls`, `dir`, `Get-ChildItem` (목록확인)
    *   `cd`, `Set-Location` (경로이동)
    *   `pwd`, `Get-Location` (경로확인)
    *   `cat`, `type`, `Get-Content` (내용읽기)
    *   `echo`, `Write-Host` (단순출력)
    *   `git status`, `git log` (상태확인)