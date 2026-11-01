# git-mirror/

Mirror every repo of a GitHub account onto a local server (e.g. a Raspberry
Pi on the LAN) as bare `*.git` repos, kept up to date periodically. This is
the sanitized version (no accounts, tokens or internal paths) of the mirror
system running on the pi3.

---

## clone_mirrors.py

Discovers all repos accessible to a GitHub token and clones the ones not yet
present as bare mirrors (`git clone --mirror`).

### Requirements

- Python 3.8+ (stdlib only)
- `git` on the PATH
- A GitHub token with `repo` scope (needed to see private repos too)

### Configuration

Everything is passed through environment variables — no credentials in the
script:

```bash
export GH_TOKEN="ghp_xxx..."           # required: account token
export MIRROR_BASE="$HOME/git-mirrors" # optional: where mirrors live
export GH_API="https://api.github.com" # optional: API base (GitHub Enterprise)
```

### Usage

```bash
python3 clone_mirrors.py
```

Iterates the repos with pagination (100 per page) and prints `OK`, `EXISTS`
or `FAIL` for each one, plus a final summary. It is idempotent: it only
clones what is missing; use `update-mirrors.sh` to refresh existing mirrors.

---

## update-mirrors.sh

Maintenance loop: runs `git fetch --prune` over every bare `*.git` repo in
the directory where the script sits, logging results to `update.log` next
to the script.

### Usage

```bash
./update-mirrors.sh       # per-repo detailed log
./update-mirrors.sh -q    # summary only (ideal for cron)
./update-mirrors.sh -r    # force refetch of references (--force)
```

Exit code is the number of failed repos (0 = all OK).

### Fetch authentication

Mirrors cloned over HTTPS remember the `https://github.com/...` URL. The
original system used `credential.helper store` (a plaintext token in
`~/.git-credentials`). To avoid leaving secrets on disk:

1. **SSH clones** (recommended): set a global URL rewrite for the user
   running the scripts:
   ```bash
   git config --global url."git@github.com:".insteadOf "https://github.com/"
   ```
   and register the server's public key as a read deploy key on the repos.
2. **In-memory helper** with `cache`:
   ```bash
   git config --global credential.helper 'cache --timeout=3600'
   ```

### Scheduling (cron)

```cron
# example: every 6 hours, quiet
0 */6 * * * /path/to/mirror/dir/update-mirrors.sh -q >/dev/null 2>&1
```

`clone_mirrors.py` only needs to run occasionally (it just adds new repos);
the periodic work is done by the update script.

---

## Serving the mirrors on the LAN

A bare repo can still be used as a remote from anywhere:

```bash
# over SSH, no daemon needed:
git clone user@server:/path/to/mirror/dir/repo.git

# or expose the directory with git-daemon (port 9418):
git daemon --base-path=/path/to/mirror/dir --export-all
git clone git://server/repo.git
```

## Security notes

- The token should only live in the process environment (`GH_TOKEN`) or an
  SSH agent; never committed nor written into scripts.
- `update.log` may contain full URLs of private repos; treat the log as
  internal information and do not publish it.
- This folder does not list the real names of the mirrored repos.
