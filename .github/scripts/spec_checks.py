"""Checks the spec's data and conventions. Standard library only; no other repo's code.

Usage: spec_checks.py [BASE_REF]. With BASE_REF (a pull request's base), the diff checks run too.
"""

import glob
import json
import os
import re
import subprocess
import sys

errors = []


def fail(msg):
    errors.append(msg)


def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def check_json():
    for path in sorted(glob.glob("**/*.json", recursive=True)):
        try:
            with open(path, encoding="utf-8") as f:
                json.load(f)
        except (ValueError, UnicodeDecodeError) as e:
            fail(f"{path}: invalid JSON: {e}")


def check_vector_names():
    for path in sorted(glob.glob("vectors/**/*.json", recursive=True)):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except ValueError:
            continue  # reported by check_json
        if not isinstance(data, dict):
            fail(f"{path}: a vector file is a JSON object")
            continue
        if "description" not in data and "name" not in data:
            fail(f"{path}: a vector has a `name` or a `description`")
        stem = os.path.splitext(os.path.basename(path))[0]
        if "name" in data and data["name"] != stem:
            fail(f"{path}: `name` is {data['name']!r}, the filename says {stem!r}")


# Relative Markdown links, and backticked paths under the spec's own directories.
# Bare filenames are skipped: many name a platform repo's file, such as `defaults.override.json`.
LINK = re.compile(r"\]\(([^)\s#]+)(?:#[^)]*)?\)")
EXTERNAL_LINK = re.compile(r"\[[^\]]*\]\([a-z]+:[^)]*\)")
TICKED = re.compile(r"`((?:rules|vectors|docs|fixtures|tokens|brand)/[^`\s]*)`")


def check_links():
    files = ["README.md", "CLAUDE.md", "CONTEXT.md"] + glob.glob("rules/*.md") + glob.glob("docs/*.md")
    for path in files:
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        here = os.path.dirname(path)
        for target in LINK.findall(text):
            if re.match(r"[a-z]+:", target):
                continue
            if not os.path.exists(os.path.normpath(os.path.join(here, target))):
                fail(f"{path}: link to missing {target}")
        # A path inside an external link's label names a file in that other repo.
        for target in TICKED.findall(EXTERNAL_LINK.sub("", text)):
            if not glob.glob(target.rstrip("/")):
                fail(f"{path}: names missing `{target}`")


def strip_descriptions(o):
    if isinstance(o, dict):
        return {k: strip_descriptions(v) for k, v in o.items() if k != "description"}
    if isinstance(o, list):
        return [strip_descriptions(v) for v in o]
    return o


# release-please reads each commit (the repo rebase-merges), so the marker must be on a commit.
BREAKING = re.compile(r"^\w+(\([^)]*\))?!:|^BREAKING[ -]CHANGE:", re.M)


def check_breaking(base):
    changed = []
    for line in git("diff", "--name-status", f"{base}...HEAD", "--", "vectors").splitlines():
        status, path = line.split("\t")[0], line.split("\t")[-1]
        if status.startswith("A") or not path.endswith(".json"):
            continue
        before = json.loads(git("show", f"{base}:{line.split(chr(9))[1]}"))
        after = None
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                after = json.load(f)
        if after is None or strip_descriptions(before) != strip_descriptions(after):
            changed.append(path)
    if not changed:
        return
    messages = git("log", "--format=%B%x00", f"{base}..HEAD").split("\0")
    if not any(BREAKING.search(m.strip()) for m in messages):
        fail(
            "vectors changed or removed: " + ", ".join(changed) + ". Vectors have no common shape, so any change "
            "besides `description` counts as altering `expected`; mark a commit breaking (`feat!:` or a "
            "`BREAKING CHANGE:` footer) so release-please cuts a major release."
        )


SESSION = re.compile(r"claude\.ai/code/session")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
ALLOWED_EMAIL = re.compile(r"^noreply@anthropic\.com$|noreply\.github\.com$")


def check_private(base):
    added = [l[1:] for l in git("diff", "-U0", f"{base}...HEAD").splitlines() if l.startswith("+") and not l.startswith("+++")]
    for i, msg in enumerate(git("log", "--format=%B%x00", f"{base}..HEAD").split("\0")):
        added += [f"(commit message) {l}" for l in msg.splitlines()]
    for line in added:
        if SESSION.search(line):
            fail(f"session link: {line.strip()[:120]}")
        for email in EMAIL.findall(line):
            if not ALLOWED_EMAIL.search(email):
                fail(f"email address: {line.strip()[:120]}")


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else None
    check_json()
    check_vector_names()
    check_links()
    if base:
        check_breaking(base)
        check_private(base)
    for e in errors:
        print(f"::error::{e}")
    print(f"{len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
