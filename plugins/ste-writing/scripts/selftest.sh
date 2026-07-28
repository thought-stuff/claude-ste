#!/bin/sh
# Verify an ste-writing install on this machine.
#
# Run after installing the plugin on a new machine:
#   sh "${CLAUDE_PLUGIN_ROOT}/scripts/selftest.sh"
#
# Checks the things that actually differ per platform: which Python exists,
# whether the launcher is executable, whether line endings survived the clone,
# and whether UTF-8 reads correctly. Exits non-zero if any check fails.

DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
LAUNCHER="$DIR/ste-lint.sh"
FAIL=0
TMP=${TMPDIR:-/tmp}/ste-selftest.$$

cleanup() { rm -f "$TMP"; }
trap cleanup EXIT INT TERM

pass() { printf '  PASS  %s\n' "$1"; }
fail() { printf '  FAIL  %s\n' "$1"; FAIL=$((FAIL + 1)); }
info() { printf '        %s\n' "$1"; }

printf '\nste-writing selftest\n'
printf 'plugin dir: %s\n' "$DIR"
printf 'uname:      %s\n' "$(uname -s 2>/dev/null || echo unknown)"
printf 'shell:      %s\n\n' "${SHELL:-unknown}"

# --- 1. launcher present and executable -------------------------------------
if [ -f "$LAUNCHER" ]; then
    pass "launcher present"
else
    fail "launcher missing at $LAUNCHER"
    printf '\n%d check(s) failed.\n' "$FAIL"
    exit 1
fi

if [ -x "$LAUNCHER" ]; then
    pass "launcher is executable"
else
    fail "launcher is not executable (git mode should be 100755)"
    info "fix: chmod +x '$LAUNCHER'"
fi

# --- 2. no CR bytes (a CRLF .sh dies with 'bad interpreter: /bin/sh^M') ------
CR=$(tr -dc '\r' < "$LAUNCHER" | wc -c | tr -d ' ')
if [ "$CR" = "0" ]; then
    pass "launcher has LF line endings (0 CR bytes)"
else
    fail "launcher contains $CR CR bytes -- will fail on macOS and Linux"
    info "fix: check .gitattributes pins *.sh to eol=lf, then re-clone"
fi

# --- 3. interpreter resolution ----------------------------------------------
RESOLVED=""
for c in python3 python py; do
    if command -v "$c" >/dev/null 2>&1 && "$c" --version >/dev/null 2>&1; then
        RESOLVED=$c
        break
    fi
done
if [ -n "$RESOLVED" ]; then
    pass "python resolves to '$RESOLVED' ($("$RESOLVED" --version 2>&1))"
else
    fail "no working Python 3 found (tried python3, python, py)"
fi

# --- 4. UTF-8 em dash counting ----------------------------------------------
# The regression that matters: a bare open() reads cp1252 on Windows and
# reports zero em dashes on a UTF-8 file. Fixture has exactly two.
printf 'The parser reads the file \342\200\224 then it stops.\n\nIt is seamless \342\200\224 truly robust.\n' > "$TMP"

OUT=$(sh "$LAUNCHER" "$TMP" 2>&1) || {
    fail "launcher failed to run"
    info "$OUT"
    printf '\n%d check(s) failed.\n' "$FAIL"
    exit 1
}
pass "launcher runs"

EM=$(printf '%s\n' "$OUT" | sed -n 's/.*em_dash= *\([0-9][0-9]*\).*/\1/p')
if [ "$EM" = "2" ]; then
    pass "UTF-8 em dashes counted correctly (2)"
elif [ "$EM" = "0" ]; then
    fail "em dashes read as 0 -- UTF-8 decoding is broken"
    info "the file has 2; this is the upstream cp1252 bug"
else
    fail "em dash count was '$EM', expected 2"
fi

# --- 5. strict vs flavored --------------------------------------------------
S=$(sh "$LAUNCHER" --mode strict   "$TMP" | sed -n 's/.*total= *\([0-9][0-9]*\).*/\1/p')
F=$(sh "$LAUNCHER" --mode flavored "$TMP" | sed -n 's/.*total= *\([0-9][0-9]*\).*/\1/p')
if [ -n "$S" ] && [ -n "$F" ]; then
    pass "both modes run (strict total=$S, flavored total=$F)"
else
    fail "mode switching failed (strict='$S' flavored='$F')"
fi

# --- 6. --no-emdash reversal ------------------------------------------------
N=$(sh "$LAUNCHER" --no-emdash "$TMP" | sed -n 's/.*total= *\([0-9][0-9]*\).*/\1/p')
if [ -n "$N" ] && [ -n "$S" ] && [ "$N" -lt "$S" ]; then
    pass "--no-emdash lowers the score ($S -> $N)"
else
    fail "--no-emdash did not lower the score (strict=$S no-emdash=$N)"
fi

# --- 7. stdin ---------------------------------------------------------------
if printf 'It is important to note that the file is read by the parser.\n' \
    | sh "$LAUNCHER" 2>/dev/null | grep -q 'total_per100w'; then
    pass "stdin path works"
else
    fail "stdin path failed"
fi

# --- 8. skill file present --------------------------------------------------
if [ -f "$DIR/../skills/ste-writing/SKILL.md" ]; then
    pass "SKILL.md present"
else
    fail "SKILL.md not found next to scripts/"
fi

printf '\n'
if [ "$FAIL" -eq 0 ]; then
    printf 'All checks passed. Install is good on this machine.\n\n'
    exit 0
fi
printf '%d check(s) failed.\n\n' "$FAIL"
exit 1
