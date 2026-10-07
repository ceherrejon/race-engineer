<!-- Template: delete sections that do not apply. "Commands" and "Done means" are required: if data is missing, ask for it. -->
# <Project name>

<What it is, who it is for and what matters most, in 2–4 lines. This is context the agent cannot infer from the code.>

## Structure

- `<folder>/`: <what lives there>
- `<folder>/`: <what lives there>

## Commands

- Install dependencies: `<command>`
- Run locally: `<command>`
- All tests: `<command>`
- A single test: `<command with example>`
- Lint / format / types: `<command>`

## Conventions

<Only what is not obvious from reading the code, with its reason. For example: "Dates are stored in UTC because the server and the app run in different time zones".>

## Constraints

<What must not be done and why. For example: "Do not add dependencies without asking: each one adds weight to the binary".>

## Done means

- <files or results that must exist>
- <tests or checks that must pass, with the command>
- The final report lists the changed paths and the result of each check.

## Autonomy

When a step does not need my decision, keep going: put status notes next to your next action, not in a separate turn. Stop and ask only when you cannot move forward without me, or before anything destructive or hard to undo: deleting data, rewriting git history, publishing or deploying, touching files outside this repository.

End every task with three sections: **Blocked on me** (what needs my decision), **Changed** and **Found** (what you noticed outside the task; report it, do not fix it).

## Where each explanation goes

Each kind of information lives in one place, so it does not contradict itself or go stale:

- **How it works:** the code itself says it, with clear names and small functions. Do not write comments that narrate what the next line already says.
- **What it must do:** the tests say it; each test name describes the expected behaviour.
- **Why the change was made:** the commit message (context, reason, alternatives discarded).
- **Code comments:** only for what the code cannot express and will stay true as long as the code exists: why the obvious approach was not used, an external constraint, or a workaround (with its reference).

Always kept: public API documentation, tool directives (`# noqa`, `// eslint-disable-next-line`, `@Suppress`…) and legal notices. Do not leave commented-out code: git keeps it. Do not clean up comments outside the scope of the task.

## Verification

Before accepting a deliverable, yours or another agent's, run it past the project reviewer (the `revisor` subagent, or `reviewer` if you rename it) and check its evidence in the files, not in its report.

## Agent setup

The secrets guard (`.agents/hooks/guardia.py`) checks every action. If a read of a secret is **not** blocked, tell the user: a step from `docs/agentes/INCORPORACION.md` is probably missing on their machine.

## Long tasks

For tasks that span several sessions, copy `docs/agentes/plantillas/progress.md` next to the task and update it after each stage: a new session must be able to continue by reading only that file. Large assignments follow `docs/agentes/plantillas/tarea.md`.
