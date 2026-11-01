#!/usr/bin/env python3
"""Create bare mirrors (git clone --mirror) of every repo in a GitHub account.

Credentials and paths are parameterized via environment variables:
  GH_TOKEN     (required) GitHub token with `repo` scope
  MIRROR_BASE  destination directory for the mirrors (default: ~/git-mirrors)
  GH_API       API base URL (default: https://api.github.com)
"""
import json, subprocess, os, urllib.request

TOKEN = os.environ["GH_TOKEN"]
BASE = os.environ.get("MIRROR_BASE", os.path.expanduser("~/git-mirrors"))
API = os.environ.get("GH_API", "https://api.github.com")
PER_PAGE = 100

os.makedirs(BASE, exist_ok=True)
os.chdir(BASE)

repos = []
page = 1
while True:
    req = urllib.request.Request(
        f"{API}/user/repos?per_page={PER_PAGE}&page={page}",
        headers={"Authorization": "token " + TOKEN, "User-Agent": "mirror-sync"},
    )
    batch = json.loads(urllib.request.urlopen(req).read())
    if not batch:
        break
    repos.extend(batch)
    if len(batch) < PER_PAGE:
        break
    page += 1

print(f"Total: {len(repos)} repos")

ok = fail = 0
for r in repos:
    name = r["name"]
    dest = name + ".git"
    url = f"https://github.com/{r['full_name']}.git"
    if os.path.exists(dest):
        print(f"EXISTS {name}")
        continue
    proc = subprocess.run(
        ["git", "clone", "--mirror", url, dest],
        capture_output=True, text=True, env=os.environ,
    )
    if proc.returncode == 0:
        print(f"OK    {name} ({r.get('visibility','?')})")
        ok += 1
    else:
        print(f"FAIL  {name}: {proc.stderr.strip()[-120:]}")
        fail += 1

print(f"--- cloned: {ok}, failed: {fail}")
