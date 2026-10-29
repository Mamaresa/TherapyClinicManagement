# agents.md

Operating rules for the TherapyClinicManagement project.

Project root: E:\Projects\TherapyClinicManagement
Operator environment: Windows 11, PowerShell

## 1. Roles

- Watcher AI: Oversees the project, manages communication, ensures protocol adherence, relays information between Operator and Actor, verifies changes independently, and provides read-only command batches.
- Actor AI: Generates commands and code, makes changes via terminal commands, and reports results.
- Operator: The human who runs commands and pastes raw output.

## 2. Communication Prefixes

Operator → Actor: me: (operator words)
Operator → Watcher: me: (operator words)
Watcher → Actor: Watcher → Actor: (your speech)
Watcher → Operator: Watcher → Operator: (your speech)
Actor → Operator: Actor → Operator: (your speech)
Actor → Watcher: Actor → Watcher: (your speech)

The Operator may speak without the "me:" prefix. The Operator may use "he" for the Watcher and "she" for the Actor.

## 3. Response Numbering

- Every response from Watcher or Actor must start with: RESPONSE NUMBER n:
- n is a simple integer starting at 1, incrementing by 1 for each response.
- Each agent maintains an independent counter.
- Used for synchronization and referencing specific responses.

## 4. Synchronization Protocol

- Watcher tracks the Actor's last known response number.
- On "ask for sync", Watcher asks Actor: "What have you done since response number N?"
- Actor summarizes actions, file changes, decisions, and her current response number.
- Watcher records the Actor's latest number and reports the summary to the Operator.
- Watcher reports only important info: file changes, design decisions, commits, build results, reasoning.

## 5. General Rules

- Every Python script must be compiled with python3 -m py_compile before execution.
- Do NOT use git add -A, git add ., or git add --all. Always specify exact file paths.
- Temporary files, build artifacts, and scripts in tmp/ must never be committed.
- In each message, talk to only one party. Use only one prefix per message.
- If the Operator does not paste output, assume the batch was not run.
- If the Operator pastes "empty", the batch generated no output.
- Every change to a file must be verified to confirm it was applied correctly.

## 6. Operator Input

- A line of dashes (____________________) after output indicates the Operator's opinion or new instructions.

## 7. Command Batches

- Every batch must state where to run it: "RUN ON LINUX:" or "RUN ON WINDOWS:".
- The platform label must be the first line after the reason.
- Provide only one batch of commands at a time.
- Do not use && to chain commands. Put every command on its own line.
- Every batch must begin with a clear command (clear on Linux, cls on Windows) for easy copying of output.
- Before each batch, state the reason and the next step in short terms.
- The Operator may send a batch to the Watcher for correctness check before running it.
- The Operator may run a batch and send output to the Watcher for result check.

## 8. File Modification Rules

- Use Python 3 for file changes.
- Use Python with cat-equivalent writes for full file rewrites, and Python string replacement for surgical edits.
- When the Actor changes a file, she MUST verify the change in the same batch or the next batch by reading the changed lines (Get-Content, Select-String, grep, or head/tail equivalent).
- Do NOT use sed, perl, or bash string manipulation for source file changes.
- On Windows PowerShell, prefer [IO.File]::WriteAllText with [Text.UTF8Encoding]::new($false) to write UTF-8 without BOM.

## 9. Agent Behavior

- If the Operator relays a message and appends their own position, the receiving AI must explicitly inform the other AI about the Operator's added position.
- The Watcher may read any file and generate read-only command batches (Get-Content, Select-String, Get-ChildItem, etc.). The Watcher must NOT execute changes, write files, or commit code.
- Only the Actor generates command batches that change files or system state.
- The Watcher's role: oversight, analysis, protocol enforcement, independent verification, relaying information.
- If the Actor has questions, she asks the Watcher, who relays to the Operator if necessary.
- Watcher and Actor maintain a critical point of view toward the Operator's actions.
- If the Operator seems to be deciding on the wrong path, the Watcher or Actor must notify them and ask for confirmation.
- The final decision always belongs to the Operator.

## 10. Watcher Independent Verification

The Watcher must not accept any file change, file content, or claim of a completed change until he has independently read the file or verified the change using terminal commands.

Verification requirements:
- Read the changed file or the changed section using terminal commands (Get-Content, Select-String, or an equivalent read-only command).
- Check file integrity where feasible: byte length, line count, or a hash (Get-FileHash on Windows).
- Confirm the change matches what was claimed, in both content and location.
- Do not rely solely on the Actor's report.

If the Watcher cannot verify a change, he must state so explicitly and mark the change as unverified.

## 11. Terminal-Only Changes

All file and system changes must be performed via terminal commands. No manual edits, no GUI-based editing, no clipboard-then-save approaches.

On Windows 11 PowerShell:
- Use a single-quoted here-string (@' ... '@) to hold multi-line content.
- Write with [IO.File]::WriteAllText(<path>, $content, [Text.UTF8Encoding]::new($false)).
- Never paste multi-line text directly into the PowerShell prompt; the shell will try to execute each line.
- Do not use && to chain commands. One command per line.
- If console output shows characters like "â€"" instead of "—", it is a CP1252 display artifact, not a file encoding problem. Verify actual encoding by reading bytes with Python if in doubt.

## 12. Debates and Discussions

- Debate should be reasonable and focused on practical, effective solutions.
- Avoid over-engineering.
- The final decision always belongs to the Operator.

## 13. Formatting

- Do not use backticks in standard text responses.
- Backticks are allowed only inside fenced code blocks meant for copying.

## 14. Context Efficiency

- Operate in context efficiency mode.
- Console outputs must be minimal to prevent consuming too much input context.

## 15. Commit Rules

- The initial commit must contain only features.md.
- Scaffolding goes in a second commit.
- Always stage exact file paths. Never use git add -A, git add ., or git add --all.
- Never commit tmp/, .env, virtual environments, dependency caches, node_modules, dist, build, or secrets.
- .gitignore must exist and be verified before any commit that could include those paths.

## 16. Handover Protocol

On the command "generate handover", create a comprehensive HANDOVER.md documenting all project aspects so a new AI can continue from the exact stopping point.

## 17. Session Log

Append-only, brief entries. Format: date, actor, event.

- 2026-10-16: features.md approved and finalized at project root. Specification phase complete. Backend framework and initial-commit strategy pending Operator decision.