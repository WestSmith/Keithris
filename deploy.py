#!/usr/bin/env python3
"""Deploy files to GitHub via the Contents API.

Token is read ONLY from the GITHUB_TOKEN environment variable.
Never write the token into this file or any file in this folder.

Usage:
  GITHUB_TOKEN=<token> python3 deploy.py status
  GITHUB_TOKEN=<token> python3 deploy.py push -m "vNN: message" index.html [more files...]
"""
import base64
import json
import os
import re
import sys
import urllib.request

REPO = "WestSmith/Keithris"
BRANCH = "main"
API = "https://api.github.com"
# Matches real token shapes (prefix + long body), not the bare prefix strings here.
TOKEN_RE = re.compile(rb"(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}")


def req(method, url, data=None):
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN env var not set")
    r = urllib.request.Request(url, method=method)
    r.add_header("Authorization", f"Bearer {token}")
    r.add_header("Accept", "application/vnd.github+json")
    if data is not None:
        r.data = json.dumps(data).encode()
    try:
        with urllib.request.urlopen(r) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        sys.exit(f"{method} {url} failed: HTTP {e.code} {e.read().decode()[:300]}")


def leak_check(path):
    with open(path, "rb") as f:
        content = f.read()
    if TOKEN_RE.search(content):
        sys.exit(f"ABORT: {path} appears to contain a GitHub token")
    return content


def status():
    repo = req("GET", f"{API}/repos/{REPO}")
    if repo is None:
        sys.exit(f"Repo {REPO} not found")
    commit = req("GET", f"{API}/repos/{REPO}/commits/{BRANCH}")
    if commit:
        print(f"{REPO}@{BRANCH}: {commit['sha'][:7]} \"{commit['commit']['message']}\"")
    tree = req("GET", f"{API}/repos/{REPO}/contents/?ref={BRANCH}")
    for item in tree or []:
        print(f"  {item['type']:4} {item['path']}")


def push(message, files):
    for path in files:
        content = leak_check(path)
        url = f"{API}/repos/{REPO}/contents/{path}"
        existing = req("GET", f"{url}?ref={BRANCH}")
        payload = {
            "message": message,
            "content": base64.b64encode(content).decode(),
            "branch": BRANCH,
        }
        if existing and "sha" in existing:
            payload["sha"] = existing["sha"]
        result = req("PUT", url, payload)
        print(f"pushed {path} -> {result['commit']['sha'][:7]}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["status"]:
        status()
    elif args[:1] == ["push"] and len(args) >= 4 and args[1] == "-m":
        push(args[2], args[3:])
    else:
        sys.exit(__doc__)
