# Collaboration Protocol

This project can be worked on by multiple active sessions safely if everyone follows a lock-first workflow.

## Rules
1. Claim lock(s) before editing any file.
2. One owner per file path at a time.
3. Keep lock TTL short (default 90 minutes); renew if needed.
4. Release lock(s) immediately after handoff/merge.
5. Write handoff notes to `state/session_handoff.md`.

## Commands
- Claim lock:
  `powershell -ExecutionPolicy Bypass -File .\tools\collab\Lock-File.ps1 -Owner "session-a" -Path "evopyramid-v2/src/App.tsx" -Task "UI sync button"`
- Release lock:
  `powershell -ExecutionPolicy Bypass -File .\tools\collab\Unlock-File.ps1 -Owner "session-a" -Path "evopyramid-v2/src/App.tsx"`
- List active locks:
  `powershell -ExecutionPolicy Bypass -File .\tools\collab\List-Locks.ps1`

## Suggested ownership split
- Session A: UI/UX and `evopyramid-v2/*`
- Session B: API/core and `β_Pyramid_Functional/*`

Adjust split per sprint, but keep lock discipline strict.
