# surl — agent channels (remote MCP and WebMCP)

**surl** (URL shortener with QR, `https://surl.ap4a.com`) exposes its tools to
agents through **two paths**:

- **Remote MCP** — `POST /mcp`, outside the browser: any desktop/CLI MCP
  client (Claude, opencode, Cursor) or script. Configured below.
- **WebMCP** — the blue `wmcp` widget on the landing page: the same tools
  inside an open tab, for browser-integrated agents. Explained in
  [WebMCP channel](#webmcp-channel-in-the-browser).
- Plus a **Python script** (`surl_mcp.py`) that talks to the remote endpoint
  with no external libraries.

The remote endpoint is **stateless JSON-RPC 2.0 over Streamable HTTP**: one
request = one JSON response, no `Mcp-Session-Id`, no SSE. It travels over the
landing page's own 443, so no port has to be opened.

Exposed tools:

| tool | parameters | returns |
|---|---|---|
| `shorten_url` | `url` (required), `name` (optional, QR footer label) | `{ short_url, qr_url, created }` — idempotent |
| `get_qr` | `short_url` (required, short URL or 8-char hash), `name?`, `include_image?` | `{ short_url, dest_host, visits, qr_url, image_mime }` (+ base64 image block) |

> Note: `shorten_url` **probes the destination** before creating the link; if
> it doesn't exist (DNS failure, connection refused, 404/410) the call fails
> and nothing is created.

## Authentication

By default the endpoint runs **without a token** (public, protected only by
per-IP rate-limit, blacklist and Safe Browsing). If the server is configured
with `MCP_TOKEN`, add the header:

```
Authorization: Bearer <token>
```

In the snippets below, wherever `--header` is indicated.

## WebMCP channel (in the browser)

Besides the remote MCP, the landing page `https://surl.ap4a.com` exposes the
**same two tools** via **WebMCP**: the blue `wmcp` widget (the
[webmcp.dev](https://webmcp.dev) library, vendored in `web/mcp.js`) registers
`shorten_url` and `get_qr` on the tab itself, and a browser-integrated agent
calls them as regular tools.

Differences from the remote channel (`POST /mcp`):

| | WebMCP (browser) | Remote MCP (`/mcp`) |
|---|---|---|
| Where the server lives | in the open tab | on the VPS, reachable from any client |
| Captcha (Turnstile) | **required** — the human solves it on the page | omitted (rate-limit + blacklist + Safe Browsing) |
| Requires | a browser with the surl tab open | network only |
| Typical use | an agent already inside the browser | Claude/opencode desktop or CLI script |

Usage from a desktop MCP agent (opencode, Claude) with the webmcp.dev
**relay**, which bridges agent ⇄ tab:

1. Start the relay daemon **before** the agent's MCP client
   (otherwise the client retries forever with `token=undefined`):
   `npx @jason.today/webmcp@latest --mcp` — listens on `localhost:4797`.
2. Open `https://surl.ap4a.com` and activate the blue `wmcp` widget.
3. In the agent, call the `webmcp_get-token` tool → it returns a single-use
   token; paste it into the page's widget to pair tab ⇄ relay.
4. The tools show up in the agent prefixed by the tab name
   (`surl_get_qr`, `surl_shorten_url`, like any MCP tool) and are used the
   same as in the remote channel.

Channel gotchas (verified in production 2026-11-01):

- The **pairing token is consumed on disconnect**: regenerate it with
  `webmcp_get-token` and paste it again.
- The page's Turnstile token **gets exhausted after each creation**: on
  `CAPTCHA verification failed`, ask the human to re-check the box and retry
  (one at a time, with a few seconds of margin).
- The `qr_url` returned by the browser version may come **relative** (the tab
  already has page context); the remote channel always returns absolute URLs.

> To automate without a browser (scripts, terminal agents, servers), use the
> remote channel or `surl_mcp.py` — WebMCP only adds the human-solved captcha,
> which buys nothing extra here: the remote endpoint is already protected by
> rate-limit, blacklist and Safe Browsing.

## Claude Desktop

Edit `claude_desktop_config.json`
(Windows: `%APPDATA%\Claude\` · macOS: `~/Library/Application Support/Claude/`):

```json
{
  "mcpServers": {
    "surl": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://surl.ap4a.com/mcp"]
    }
  }
}
```

With token:

```json
{
  "mcpServers": {
    "surl": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://surl.ap4a.com/mcp",
               "--header", "Authorization: Bearer <TOKEN>"]
    }
  }
}
```

Restart Claude Desktop. `mcp-remote` bridges stdio ⇄ HTTP; requires Node.js.

## Claude Code (CLI)

```bash
claude mcp add surl -- npx -y mcp-remote https://surl.ap4a.com/mcp
```

With token (headers go through `--header`):

```bash
claude mcp add surl --header "Authorization: Bearer <TOKEN>" -- npx -y mcp-remote https://surl.ap4a.com/mcp
```

Verify: `claude mcp list` → `surl: ✓ connected`.
To make it available in every project: `claude mcp add surl --scope user ...`

## opencode

In `opencode.json` (project root) or `~/.config/opencode/opencode.json`:

Option A — direct remote server (opencode speaks Streamable HTTP without a bridge):

```json
{
  "mcp": {
    "surl": {
      "type": "remote",
      "url": "https://surl.ap4a.com/mcp",
      "enabled": true
    }
  }
}
```

With token:

```json
{
  "mcp": {
    "surl": {
      "type": "remote",
      "url": "https://surl.ap4a.com/mcp",
      "enabled": true,
      "headers": { "Authorization": "Bearer <TOKEN>" }
    }
  }
}
```

Option B — stdio bridge (works exactly like Claude):

```json
{
  "mcp": {
    "surl": {
      "type": "local",
      "command": ["npx", "-y", "mcp-remote", "https://surl.ap4a.com/mcp"],
      "enabled": true
    }
  }
}
```

## Cursor, Windsurf and similar

Almost every desktop client accepts the `npx mcp-remote` pattern.
In Cursor: **Settings → MCP Tools → Add**, or `~/.cursor/mcp.json` with the
same `mcpServers` structure as Claude Desktop.

## Any other MCP client

If it supports MCP over HTTP directly, the endpoint is simply
`POST https://surl.ap4a.com/mcp` with `Content-Type: application/json` and
`Accept: application/json, text/event-stream`. Test with `curl`:

```bash
curl -s -X POST https://surl.ap4a.com/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

It should answer with the two tools (`shorten_url`, `get_qr`).

## Example prompts (opencode / Claude Code)

Once the server is configured (see the opencode / Claude Code sections
above), the agent calls the tools automatically — you just ask in natural
language. Same prompts work in both.

**Shorten a link**

> shorten https://tabandblank.com/blog/baraja-espanola/ with surl

> acorta esta URL con surl y ponle de pie del QR "blog baraja":
> https://tabandblank.com/blog/baraja-espanola/

Expected: the agent calls `shorten_url` and answers with the short link and
the QR PNG URL.

**Get the QR of an existing link**

> give me the QR URL for https://surl.ap4a.com/g64NmKIF

> get the QR for hash g64NmKIF and save the PNG to qr.png
(the agent calls `get_qr` with `include_image` and writes the file)

**Check whether a link is still alive (and its traffic)**

> is https://surl.ap4a.com/AbC12345 still around? how many visits?
(`get_qr` checks the DB — if the 30-day GC deleted it, the tool says so)

**Batch work**

> shorten every external link in blog/posts/recorrido-del-caballo.md with
> surl and rewrite the markdown with the short URLs

> take this list of URLs from links.txt, shorten them all and give me a
> two-column table url / short_url

(The agent loops `shorten_url` per URL; keep it to a few per minute — the
endpoint has per-IP rate limits.)

**Decide between the two channels**

> the surl tab is open in my browser and webmcp is paired: shorten
> https://example.com using the browser tools

(Uses the `surl_shorten_url` WebMCP tool instead of the remote one — the
human solves the Turnstile captcha on the page.)

## Python script (no dependencies)

[`surl_mcp.py`](surl_mcp.py) speaks JSON-RPC against the endpoint using only
the standard library (`urllib`).

> **Cloudflare gotcha**: `surl.ap4a.com` sits behind Cloudflare, which blocks
> clients with a Python User-Agent signature (error 1010 / HTTP 403). The
> script sends `User-Agent: curl/8.0.1` by default, which passes; override it
> with the `SURL_MCP_UA` environment variable. If you write your own client,
> send a UA that doesn't look like Python.

Usage:

```bash
python surl_mcp.py shorten https://example.com/a-long-url
python surl_mcp.py shorten https://example.com "My label"
python surl_mcp.py qr AbC12345                  # short-link info
python surl_mcp.py qr AbC12345 --save qr.png    # save the QR PNG
python surl_mcp.py tools                        # list available tools
```

With token (or `SURL_MCP_TOKEN` environment variable):

```bash
set SURL_MCP_TOKEN=<TOKEN>        # Windows
export SURL_MCP_TOKEN=<TOKEN>     # Linux/macOS
python surl_mcp.py shorten https://example.com
```

It can also be imported as a module:

```python
from surl_mcp import SurlMCP
s = SurlMCP()                       # or SurlMCP(token="...")
r = s.shorten("https://example.com", name="demo")
print(r["short_url"], r["qr_url"])
qr = s.get_qr(r["short_url"], include_image=True)   # qr["image_png"] = bytes
```
