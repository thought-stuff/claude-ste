# claude-ste: Agent Instructions

## Writing standard

Prose in this repo follows [ste-writing](https://github.com/thought-stuff/claude-ste) (ASD-STE100 Simplified Technical English), applied per path. This does not apply to code, identifiers, or command syntax.

| Scope | Paths |
|---|---|
| **STE strict** | `plugins/*/skills/**/SKILL.md` |
| **STE flavored** | `README.md` |
| **Not governed** | Everything not listed above |

This repo ships the standard, so it follows it.

Lint before committing prose:

```sh
sh "${CLAUDE_PLUGIN_ROOT}/scripts/ste-lint.sh" --mode flavored <file>
```

Use `--mode strict` on strict paths. The score is a delta, not a target: compare a
document against itself before and after a change, and never rewrite a sentence
solely to move the number. STE strips voice on purpose, so do not apply it to
paths marked not governed, even when asked to "clean up" the prose.

Standard and linter: [thought-stuff/claude-ste](https://github.com/thought-stuff/claude-ste).
Rollout plan and rationale: `obsidian-abulafia/thought-stuff/strategy/STE Writing Standard Rollout.md`.
