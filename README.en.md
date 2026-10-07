# Race Engineer

[![Tests](https://github.com/ceherrejon/race-engineer/actions/workflows/pruebas.yml/badge.svg)](https://github.com/ceherrejon/race-engineer/actions/workflows/pruebas.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Set up or audit any project for Claude Code and Codex**, with a skill that puts each piece in the format each tool reads and checks it live.

Like the race engineer of an F1 team with two drivers: it sets up each car (Claude and Codex), reads the project's telemetry and proposes changes, but touches nothing without your sign-off.

[Español](README.md) · The skill works in your team's language. Its templates are in Spanish, and `AGENTS.md` is also available in English.

## What it does

`race-engineer` has two modes:

- **New project:** generates `AGENTS.md` (plus `CLAUDE.md` only when needed), permissions and hooks for Claude Code (`.claude/settings.json`) and Codex (`.codex/config.toml`), a **secrets guard** shared by both tools, a reviewer subagent, state templates for long tasks, and an onboarding guide for each team member.
- **Existing project:** audits its setup across 9 layers (instructions, procedures, external sources, action rules, verification, model and effort, state, code and commits, agent teams) and delivers a prioritized, evidence-backed report plus a change proposal that is only applied with your approval.

Both modes start with a read-only inventory, then propose, wait for approval, apply and verify.

### Why the official tools are not enough

It runs them (`prompt-audit` from the `claude-api` skill, `/doctor prompt-audit`, `/skill-doctor`) and folds in their results. None of them covers:

- **Claude and Codex sharing a repository** (who reads `AGENTS.md`, what a `CLAUDE.local.md` breaks, config equivalences);
- the actual **hooks and permissions**, including silent traps such as Codex on Windows turning a hook's block into "hook failed", which lets the action through;
- **secrets** depending on the OS (native Windows has no sandbox for Claude's shell);
- verification, long-task state and agent teams.

### Example

[An audit of this very repository](pruebas/este-proyecto/auditoria.md), made with the skill (in Spanish).

## Installation

### Claude Code (plugin)

```text
/plugin marketplace add ceherrejon/race-engineer
/plugin install race-engineer@race-engineer
```

Optional helper skill that cleans up comments in existing code:

```text
/plugin install limpiar-comentarios@race-engineer
```

### Codex (or Claude Code without the plugin)

Clone the repository and link the skill folder into your user skills folder, so updates arrive with `git pull`:

```bash
git clone https://github.com/ceherrejon/race-engineer.git
```

```bash
ln -s "$PWD/race-engineer/skill/race-engineer" ~/.agents/skills/race-engineer
```

On Windows, use a directory junction instead (no admin rights needed). Commands for every OS and for Claude Code are in [skill/README.md](skill/README.md).

## Usage

- **Claude Code:** `/race-engineer:race-engineer` when installed as a plugin (`/race-engineer` when linked by hand), or just ask: "review this project's agent setup", "prepare this project for Claude and Codex".
- **Codex:** `$race-engineer` or the same request in plain language.

## Requirements

- Python 3.11+ (standard library only) and git.
- Claude Code 2.1.277+ for native `AGENTS.md` loading; 2.1.283+ for `/doctor prompt-audit`.

## Status

- **v1.1.** Tested live on Windows 11 with Claude Code 2.1.289 and Codex 0.160: new project, audit of a real project, and secret barriers verified in both tools.
- Automated tests for the scripts run on Linux, macOS and Windows on every change. A live run with the agents on macOS and Linux is still pending.
- The secrets guard is a **guardrail against accidents, not a security boundary**: an obfuscated command gets past it.

## How it was built

Every check in the skill cites a practice from the knowledge base (`conocimiento/`), and every practice cites its sources (`fuentes/`): official documentation, articles, and our own tests.

## Contributing

New sources follow the protocol in [AGENTS.md](AGENTS.md). Run the tests before proposing a change:

```bash
python -m unittest discover -s tests
```

## License

[MIT](LICENSE).
