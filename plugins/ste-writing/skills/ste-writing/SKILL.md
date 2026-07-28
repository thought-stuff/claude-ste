---
name: ste-writing
description: Rewrite prose (docs, READMEs, PR descriptions, error messages, release notes, comments — never code) into ASD-STE100 Simplified Technical English to remove "AI slop". Use when asked to make writing not sound like AI, make docs clear or plain, enforce a controlled writing style, or write technical documentation that reads human. Two modes — strict (procedures/safety) and STE-flavored (general prose).
---

# ste-writing

Write prose in ASD-STE100 Simplified Technical English. This applies to documentation, READMEs, pull-request text, error messages, release notes, and comments. It does not apply to code, identifiers, or command syntax. It is not for marketing copy, essays, or anything that needs a voice — STE strips voice on purpose.

**Check the repo's `CLAUDE.md` before applying this.** Repos declare which paths are governed and in which mode. Creative and narrative work is exempt by design; do not apply the standard there even if asked to "clean up" the prose.

## Rules

WORDS
- Use one name for one thing. Do not call the same item by two different names.
- Use the short common word: start (not begin/commence/initiate), use (not utilize/leverage), help (not facilitate), make sure (not ensure), before (not prior to), after (not subsequent to), about (not regarding/concerning), get (not obtain/acquire), show (not demonstrate), also (not additionally/furthermore/moreover).
- Give each word one meaning. "fall" means to move down, not to decrease.
- No marketing adjectives: seamless, robust, powerful, cutting-edge, effortless, world-class, next-generation, revolutionary.
- American spelling.

VERBS
- Active voice. "the parser reads the file", not "the file is read by the parser".
- Use a verb for an action. "analyze the log", not "perform an analysis of the log".
- No stacked auxiliaries. Not "it is important to note that this may help to improve". Write "this improves X".
- No "-ing" main verb where a simple tense works.

SENTENCES
- One instruction per sentence. Max 20 words (instruction), max 25 (descriptive).
- No contractions. Use articles: a, an, the, this, these.

PUNCTUATION
- No semicolons. Write two sentences.
- **No em dashes or en dashes.** Rewrite as two sentences, or use a comma, colon, or parentheses. *(House rule. ASD-STE100 bans only the semicolon. Adopted because em dashes are the most visible tell in this portfolio's generated prose.)*

STRUCTURE
- One topic per paragraph, max six sentences. For steps, use a numbered vertical list, one action per item, imperative form. Put a condition before its command.

Write only the requested text. No preamble, no summary, no closing remarks.

## Modes

- **strict** — procedures, runbooks, safety text, gate criteria, error messages: apply every rule and both length caps.
- **STE-flavored** — general prose (READMEs, PR descriptions, docs): apply the sentence, paragraph, active-voice, no-phrasal-verb, and no-em-dash discipline. Relax the contraction rule and the ~900-word dictionary lockdown so the text keeps enough range to read naturally.

Contractions and the dictionary are the two rules that strip voice fastest. That is correct in a runbook and wrong in a README. When in doubt, use flavored.

## Self-lint (run before returning text)

Run the linter on what you wrote:

```sh
"${CLAUDE_PLUGIN_ROOT}/scripts/ste-lint.sh" --mode flavored path/to/file.md
```

Use `--mode strict` for procedures. Add `--json` for the per-category breakdown. Reading from stdin also works.

Then fix what it flags:

1. Any sentence over 20 words? Split it.
2. Any semicolon? Replace with a period.
3. Any em dash or en dash? Rewrite.
4. Any contraction? Expand it — strict mode only.
5. Any passive voice with a known actor? Make it active.
6. Any "-ing" main verb, nominalization ("perform an analysis"), or phrasal verb ("spin up")? Replace with a plain verb.
7. Same thing named two ways? Pick one name.

**The score is a delta, not a target.** The absolute number is noisy — `long_paragraph` penalizes STE's own short sentences, and `passive_voice` is a regex that flags "is interested". Compare before and after on the same document. Never rewrite a sentence solely to move the number.

## What this does not do

The mechanical rules above are lintable and are what removes slop. Full STE also needs human judgment (the right technical noun, whether a sentence "makes good sense") — a checker cannot certify that, and slop is not about that.

This skill fixes the FORM of slop. It cannot make a hollow paragraph true. A clean, confident, well-punctuated hollow paragraph is still hollow, and the standard will make it read as finished. Do not let it stand in for having something to say.

## Provenance

Distilled from ASD-STE100 Issue 9, free at https://asd-ste100.org — copyrighted, so do not paste it in full.

This skill and the linter derive from the ep01 kit in https://github.com/woosal1337/blog, MIT © 2026 Ege Çelebi. See `LICENSE-upstream` at the repo root. Local changes: the em-dash rule, the mode-aware linter, UTF-8 handling, and the cross-platform launcher.
