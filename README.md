# claude-ste

A Claude Code marketplace carrying one plugin: **ste-writing**, a distilled
ASD-STE100 Simplified Technical English standard plus a machine-checkable
anti-slop linter.

The point is not the aerospace standard. It is that a writing system a script
can check beats a list of banned words. Give the model a system and slop drops
by half or more; ban tokens one at a time and you get a slop paragraph with no
em dashes in it.

## Install

On each machine, once. Add the marketplace to `~/.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "thought-stuff": {
      "source": { "source": "github", "repo": "thought-stuff/claude-ste" }
    }
  }
}
```

Then install the plugin:

```
/plugin install ste-writing@thought-stuff
```

Updates arrive by pulling the marketplace. There is one canonical copy of the
skill and the linter, versioned here, rather than a hand-placed copy per
machine.

## Use

The skill triggers on requests like "make this not sound like AI" or "write
docs that read human". It costs no context until invoked.

Run the linter directly:

```sh
"${CLAUDE_PLUGIN_ROOT}/scripts/ste-lint.sh" --mode flavored docs/*.md
```

| Flag | Effect |
|---|---|
| `--mode strict` | Every rule and both length caps. Procedures, runbooks, error messages. Default. |
| `--mode flavored` | Drops the contraction and dictionary checks. Everything else. |
| `--no-emdash` | Stop counting em dashes, which ASD-STE100 does not actually ban. |
| `--json` | Full per-category report. |

Score is violations per 100 words. **Lower is cleaner, but the absolute number
is noisy — the before/after delta on the same document is the signal.** Do not
set a threshold and do not rewrite a sentence solely to move the number.

## Modes exist for a reason

Run in strict mode, this linter scores ordinary prose as slop for having a
voice. Measured across 24 repos, one worldbuilding repo ranked 4th sloppiest on
the strict score and 22nd on the flavored score — nearly all of the difference
was contractions. Contractions and the ~900-word dictionary are the two rules
that strip voice fastest. That is correct in a runbook and wrong in a README.

Never run strict mode over creative work.

## What it does not do

STE fixes the form of slop, not the substance. It turns a hollow paragraph into
a clean, well-punctuated hollow paragraph. No linter can tell you whether a
sentence is true or worth writing.

## Credits

Derived from the ep01 kit in [woosal1337/blog](https://github.com/woosal1337/blog/tree/main/videos/ep01-the-cure-for-ai-slop),
MIT © 2026 Ege Çelebi — see `LICENSE-upstream`. Local changes: the em-dash rule
(a house addition, not part of the standard), mode-aware linting, UTF-8
handling, and a cross-platform launcher.

The standard itself is ASD-STE100 Issue 9, free at https://asd-ste100.org. It
is copyrighted; this repo carries a distillation, not the text.
