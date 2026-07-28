#!/bin/sh
# Cross-platform launcher for ste_lint.py.
#
# The interpreter name differs by platform and cannot be assumed:
#   macOS / Linux : python3 works, `python` is often absent
#   Windows       : `python` works; `python3` is a Microsoft Store stub that
#                   prints an install advert and exits non-zero
# Resolve at run time rather than hardcoding either one.
#
# Windows runs this under Git Bash, which ships with Claude Code's Bash tool.

set -e

DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

resolve_python() {
    for candidate in python3 python py; do
        if command -v "$candidate" >/dev/null 2>&1; then
            # The Store stub answers `command -v` but fails --version.
            if "$candidate" --version >/dev/null 2>&1; then
                echo "$candidate"
                return 0
            fi
        fi
    done
    return 1
}

PY=$(resolve_python) || {
    echo "ste-lint: no working Python 3 found (tried python3, python, py)" >&2
    exit 127
}

exec "$PY" "$DIR/ste_lint.py" "$@"
