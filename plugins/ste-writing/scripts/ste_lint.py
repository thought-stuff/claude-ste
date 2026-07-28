#!/usr/bin/env python3
"""Heuristic anti-slop linter -- the machine-checkable subset of ASD-STE100.

Derived from ste-lint.py in https://github.com/woosal1337/blog
(videos/ep01-the-cure-for-ai-slop), MIT (c) 2026 Ege Celebi. See
LICENSE-upstream. Local changes, all marked [MOD] below:

  [MOD 1] UTF-8 file and stdin reads. Upstream calls open(f) with no encoding,
          which resolves to cp1252 on Windows and silently reports zero em
          dashes on a UTF-8 file -- the one marker the whole method leans on.
  [MOD 2] Em dashes are a counted violation, not just a reported marker.
          This is a house rule, NOT part of ASD-STE100, which bans only the
          semicolon. Disable with --no-emdash.
  [MOD 3] --mode flavored drops the contraction and dictionary checks, which
          STE-flavored mode explicitly relaxes. Without this the linter scores
          ordinary prose as slop for having a voice.

Score is violations per 100 words. Lower is cleaner. The absolute number is
noisy; the before/after delta on the same document is the signal.
"""
import re, sys, json, glob, os, argparse

MARKETING = ["seamless","seamlessly","robust","powerful","cutting-edge","effortless","effortlessly",
    "world-class","next-generation","revolutionary","blazing","lightning-fast","elegant","delightful",
    "turnkey","best-in-class","state-of-the-art","game-changing","first-class","battle-tested",
    "enterprise-grade","supercharge","unlock","unleash","empower","empowers"]
BANNED = ["begin","begins","commence","commences","initiate","initiates","originate",
    "utilize","utilizes","utilizing","leverage","leverages","leveraging","facilitate","facilitates",
    "ensure","ensures","ensuring","prior to","subsequent to","obtain","obtains","acquire","acquires",
    "demonstrate","demonstrates","additionally","furthermore","moreover","comprehensive","comprehensively",
    "utilization","aforementioned","henceforth","therein","whilst","amongst","numerous","myriad","plethora",
    "in order to","a variety of","in the event that","due to the fact that","it is important to note"]
PHRASAL = ["spin up","spin down","reach out","dive into","dives into","diving into","kick off","kicks off",
    "roll out","rolls out","tear down","ramp up","circle back","drill down","spun up","reaching out"]
MODAL_HEDGE = ["it is important to note","it should be noted","it is worth noting","please note that",
    "as mentioned","as noted above"]
BE = r"(?:am|is|are|was|were|be|been|being)"
PP_IRREG = r"(?:done|made|sent|read|built|kept|held|set|put|run|written|shown|given|taken|found|got|gotten|seen|known|thrown|drawn)"

# [MOD 3] Rules that STE-flavored mode relaxes. Contractions and the ~900-word
# dictionary are voice, not slop, outside of procedures.
FLAVORED_DROPS = {"contraction", "banned_word"}


def strip_code(t):
    t = re.sub(r"```.*?```", " ", t, flags=re.S)
    t = re.sub(r"`[^`]*`", " ", t)
    return t

def sentences(text):
    out = []
    for line in text.split("\n"):
        s = line.strip()
        if not s: continue
        s = re.sub(r"^\s*#{1,6}\s*", "", s)
        s = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", s)
        if not s: continue
        parts = re.split(r"(?<=[.!?:])\s+(?=[A-Z0-9\"'\-])", s)
        for p in parts:
            p = p.strip()
            if p: out.append(p)
    return out

def wc(s):
    return len([w for w in re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-/]*", s)])

def count_ci(text, phrases):
    n = 0; hits = []
    low = text.lower()
    for ph in phrases:
        for m in re.finditer(r"(?<![a-z])" + re.escape(ph) + r"(?![a-z])", low):
            n += 1; hits.append(ph)
    return n, hits


def lint(text, mode="strict", emdash=True):
    raw = text
    text = strip_code(text)
    sents = sentences(text)
    words = sum(wc(s) for s in sents) or 1
    v = {}
    longs = [(wc(s), s) for s in sents if wc(s) > 20]
    v["long_sentence(>20w)"] = len(longs)
    v["semicolon"] = text.count(";")
    v["contraction"] = len(re.findall(r"\b\w+['’](?:t|re|ve|ll|d|s|m)\b", text))
    v["passive_voice"] = len(re.findall(rf"\b{BE}\s+(?:\w+ed|{PP_IRREG})\b", text, re.I))
    v["ing_main_verb"] = len(re.findall(rf"\b{BE}\s+\w+ing\b", text, re.I))
    v["nominalization"] = len(re.findall(r"\b(?:perform(?:s|ed)?|conduct(?:s|ed)?|provide(?:s|d)?|carry out|carries out|make use of|makes use of)\b", text, re.I)) + len(re.findall(r"\b\w{4,}(?:tion|ment|ance|ence)\s+of\b", text, re.I))
    v["phrasal_verb"], _ = count_ci(text, PHRASAL)
    v["banned_word"], bh = count_ci(text, BANNED)
    v["marketing_adjective"], mh = count_ci(text, MARKETING)
    v["modal_hedge"], _ = count_ci(text, MODAL_HEDGE)
    paras = [p for p in re.split(r"\n\s*\n", raw) if p.strip()]
    v["long_paragraph(>6s)"] = sum(1 for p in paras if len(sentences(strip_code(p))) > 6)

    # [MOD 2] Counted from code-stripped text so em dashes inside fenced blocks
    # and inline code do not score. The raw count stays as a reported marker.
    em_prose = text.count("—") + text.count("–")
    em_raw = raw.count("—") + raw.count("–")
    if emdash:
        v["em_dash"] = em_prose

    # [MOD 3]
    if mode == "flavored":
        for k in FLAVORED_DROPS:
            v.pop(k, None)

    total = sum(v.values())
    return {
        "mode": mode,
        "words": words, "sentences": len(sents),
        "violations": v, "total": total,
        "total_per100w": round(total * 100.0 / words, 2),
        "em_dash_raw(marker)": em_raw,
        "longest_sentence_words": (max(longs)[0] if longs else max((wc(s) for s in sents), default=0)),
        "sample_marketing": list(dict.fromkeys(mh))[:6],
        "sample_banned": list(dict.fromkeys(bh))[:6] if mode != "flavored" else [],
    }


def read_text(path):
    # [MOD 1]
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def main():
    ap = argparse.ArgumentParser(description="Heuristic anti-slop linter (ASD-STE100 subset).")
    ap.add_argument("files", nargs="*", help="files or globs; omit to read stdin")
    ap.add_argument("--mode", choices=["strict", "flavored"], default="strict",
                    help="flavored drops contraction and dictionary checks (default: strict)")
    ap.add_argument("--json", action="store_true", help="full JSON report per file")
    ap.add_argument("--no-emdash", action="store_true",
                    help="do not count em dashes as violations (they are not banned by ASD-STE100)")
    a = ap.parse_args()
    emdash = not a.no_emdash

    if not a.files:
        # [MOD 1]
        try:
            sys.stdin.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
        print(json.dumps(lint(sys.stdin.read(), a.mode, emdash), indent=2))
        return 0

    exp = []
    for f in a.files:
        exp += sorted(glob.glob(f, recursive=True)) if any(c in f for c in "*?[") else [f]
    if not exp:
        print("no files matched", file=sys.stderr)
        return 1

    for f in exp:
        try:
            r = lint(read_text(f), a.mode, emdash)
        except OSError as e:
            print(f"{os.path.basename(f):32} ERROR {e}", file=sys.stderr)
            continue
        if a.json:
            print(json.dumps({"file": f, **r}, indent=2))
        else:
            print(f"{os.path.basename(f):32} mode={r['mode']:8} words={r['words']:5d} "
                  f"total={r['total']:4d} per100w={r['total_per100w']:6.2f} "
                  f"em_dash={r['violations'].get('em_dash', r['em_dash_raw(marker)']):3d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
