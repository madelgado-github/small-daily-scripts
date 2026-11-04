# small-daily-scripts

A collection of utility scripts for day-to-day system automation tasks.

---

## Folders

### [`cloudflare/`](cloudflare/README.md)

PowerShell script that keeps a Cloudflare DNS A record in sync with the machine's current public IP (DDNS).

### [`gemma/`](gemma/README.md)

Local AI chat setup using Gemma 3 models via Ollama, containerized with Docker and accessed through a Python CLI client.

### [`git-mirror/`](git-mirror/README.md)

Mirror all repos of a GitHub account as bare `*.git` repos on a local server and keep them updated (sanitized version of the pi3 mirror setup).

### [`iot/`](iot/README.md)

Python scripts to control Tuya smart plugs from the terminal and expose them as MCP tools for AI assistants.

### [`midi/`](midi/)

Python scripts that generate 8-bit style two-track MIDI files (melody + bass/arpeggio) using `mido`.

### [`short_url_mcp/`](short_url_mcp/README.md)

Setup guide for the two agent channels of **surl** (`https://surl.ap4a.com`): the remote MCP endpoint (`POST /mcp`) for Claude Desktop/Code, opencode and other clients, and the in-browser WebMCP widget; plus a dependency-free Python script (`surl_mcp.py`) to shorten URLs and fetch QR codes directly from a script.

---

miguel_AT_onlywebs.com / surtursoftware
