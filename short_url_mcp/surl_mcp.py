#!/usr/bin/env python3
"""MCP client for surl (https://surl.ap4a.com/mcp) with no external dependencies.

The endpoint is stateless JSON-RPC 2.0 over HTTP, so no MCP library is
needed: the stdlib urllib is enough.

CLI usage:
    python surl_mcp.py shorten <url> [name]
    python surl_mcp.py qr <short_url_or_hash> [--save file.png] [--name label]
    python surl_mcp.py tools

Module usage:
    from surl_mcp import SurlMCP
    s = SurlMCP()
    r = s.shorten("https://example.com", name="demo")
    print(r["short_url"])

Authentication: SURL_MCP_TOKEN environment variable or token= parameter.
"""

import base64
import json
import os
import sys
import urllib.error
import urllib.request

ENDPOINT = os.environ.get("SURL_MCP_URL", "https://surl.ap4a.com/mcp")
# Cloudflare (in front of surl.ap4a.com) blocks clients with a Python
# User-Agent signature; curl's UA passes. Override with SURL_MCP_UA.
USER_AGENT = os.environ.get("SURL_MCP_UA", "curl/8.0.1")
PROTOCOL_VERSION = "2025-03-26"
CLIENT_INFO = {"name": "surl_mcp.py", "version": "1.0"}


class SurlError(RuntimeError):
    pass


class SurlMCP:
    def __init__(self, endpoint: str = ENDPOINT, token: str | None = None,
                 timeout: float = 30.0, user_agent: str = USER_AGENT):
        self.endpoint = endpoint
        self.token = token or os.environ.get("SURL_MCP_TOKEN") or None
        self.timeout = timeout
        self.user_agent = user_agent
        self._id = 0

    def _rpc(self, method: str, params: dict) -> dict:
        self._id += 1
        payload = {"jsonrpc": "2.0", "id": self._id, "method": method, "params": params}
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": self.user_agent,
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        req = urllib.request.Request(
            self.endpoint, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")
            if e.code == 401:
                raise SurlError("401 unauthorized: the endpoint requires MCP_TOKEN. "
                                "Set SURL_MCP_TOKEN or pass token=...") from e
            raise SurlError(f"HTTP {e.code}: {detail or e.reason}") from e
        except urllib.error.URLError as e:
            raise SurlError(f"Network error: {e.reason}") from e

        # Direct JSON response (the server is stateless); SSE tolerated just in case.
        if body.lstrip().startswith("event:") or "\ndata: " in body:
            for line in body.splitlines():
                if line.startswith("data: "):
                    body = line[6:]
                    break
        msg = json.loads(body)
        if "error" in msg:
            err = msg["error"]
            raise SurlError(f"JSON-RPC {err.get('code')}: {err.get('message')}")
        return msg["result"]

    def _call_tool(self, name: str, arguments: dict):
        result = self._rpc("tools/call", {"name": name, "arguments": arguments})
        if result.get("isError"):
            texts = [c.get("text", "") for c in result.get("content", []) if c.get("type") == "text"]
            raise SurlError("; ".join(texts) or f"tool {name} failed")
        return result

    @staticmethod
    def _structured(result: dict) -> dict:
        if "structuredContent" in result:
            return result["structuredContent"]
        for c in result.get("content", []):
            if c.get("type") == "text":
                return json.loads(c["text"])
        raise SurlError("response with no usable content")

    def initialize(self) -> dict:
        return self._rpc("initialize", {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": CLIENT_INFO,
        })

    def list_tools(self) -> list[dict]:
        return self._rpc("tools/list", {}).get("tools", [])

    def shorten(self, url: str, name: str | None = None) -> dict:
        """Create (or reuse) the short link. Returns short_url, qr_url, created."""
        args = {"url": url}
        if name:
            args["name"] = name
        return self._structured(self._call_tool("shorten_url", args))

    def get_qr(self, short_url: str, name: str | None = None,
               include_image: bool = False) -> dict:
        """Short-link info; with include_image adds an image_png key (bytes)."""
        args = {"short_url": short_url}
        if name:
            args["name"] = name
        if include_image:
            args["include_image"] = True
        result = self._call_tool("get_qr", args)
        info = self._structured(result)
        if include_image:
            for c in result.get("content", []):
                if c.get("type") == "image":
                    info["image_png"] = base64.b64decode(c["data"])
                    info.setdefault("image_mime", c.get("mimeType"))
                    break
        return info


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd = argv[1]
    s = SurlMCP()
    try:
        if cmd == "tools":
            for t in s.list_tools():
                print(f"- {t['name']}: {t.get('description', '').splitlines()[0]}")
            return 0
        if cmd == "shorten":
            if len(argv) < 3:
                print("missing URL", file=sys.stderr)
                return 2
            name = argv[3] if len(argv) > 3 else None
            r = s.shorten(argv[2], name=name)
            print(f"short_url: {r['short_url']}")
            print(f"qr_url:    {r['qr_url']}")
            print(f"created:   {r['created']}")
            return 0
        if cmd == "qr":
            if len(argv) < 3:
                print("missing short link or hash", file=sys.stderr)
                return 2
            save = name = None
            rest = argv[3:]
            i = 0
            while i < len(rest):
                if rest[i] == "--save" and i + 1 < len(rest):
                    save = rest[i + 1]
                    i += 2
                elif rest[i] == "--name" and i + 1 < len(rest):
                    name = rest[i + 1]
                    i += 2
                else:
                    i += 1
            r = s.get_qr(argv[2], name=name, include_image=bool(save))
            print(f"short_url: {r['short_url']}")
            print(f"dest_host: {r.get('dest_host')}")
            print(f"visits:    {r.get('visits')}")
            print(f"qr_url:    {r.get('qr_url')}")
            if save:
                with open(save, "wb") as f:
                    f.write(r["image_png"])
                print(f"saved:     {save} ({len(r['image_png'])} bytes)")
            return 0
        print(f"unknown command: {cmd}", file=sys.stderr)
        return 2
    except SurlError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
