# cloudflare/

## update_ddns.ps1

A PowerShell script that keeps a Cloudflare DNS **A record** in sync with the machine's current public IP address. Useful for home servers or any host with a dynamic public IP (DDNS — Dynamic DNS).

### How it works

1. Fetches the current public IP from [ipify.org](https://api.ipify.org/).
2. Queries the Cloudflare API for an existing `A` record matching the configured hostname.
3. **If the record exists** — updates it with the current IP (`PUT`).
4. **If the record does not exist** — creates it (`POST`).
5. Prints a timestamped log line to stdout indicating whether the record was updated or created.

### Requirements

- Windows PowerShell 5.1+ or PowerShell 7+
- A [Cloudflare](https://cloudflare.com) account with:
  - An API token that has **Zone / DNS / Edit** permissions for the target zone
  - The Zone ID of the domain you want to update

### Configuration

Edit the top of the script and replace the placeholder values:

```powershell
$token  = "toke.with.update.zone.access.cloudflare"  # Cloudflare API token
$zoneId = "your.zone.id.cloudflare"                  # Zone ID (found in the Cloudflare dashboard)
$record = "yoursurdomain.domain.tld"                  # Full DNS record name, e.g. home.example.com
```

### Usage

Run the script manually:

```powershell
.\cloudflare\update_ddns.ps1
```

Or schedule it with **Task Scheduler** to run at a regular interval (e.g., every 5 minutes) to keep the record continuously updated.

### Example output

```
02/18/2026 23:55:00 - DNS updated: home.example.com -> 203.0.113.42
```

## football_time.bat

A batch script that automatically checks whether your website is still reachable **through Cloudflare** — the typical "football time" problem where, during major football match days, an ISP blocks or cuts the connections to Cloudflare's edge IPs, so the site appears down even though the origin server is perfectly fine.

It disambiguates the two failure modes by making **two requests per domain**:

1. **PUBLIC** — a normal request that goes through Cloudflare. If the ISP is blocking Cloudflare for football, this one fails / times out.
2. **ORIGIN** — a request forced with `--resolve` straight to the real server IP, bypassing Cloudflare. If this responds, the site **is** alive and the problem is only the ISP's Cloudflare block.

It also detects whether you are behind Cloudflare by inspecting the `Server:` header and the presence of `CF-RAY`, and prints a clear **VERDICT** (ALIVE / origin not responding) per domain.

### Usage

```bat
football_time.bat DOMAIN [ORIGIN_IP] [PATTERN]
football_time.bat list.txt
```

- `DOMAIN` — e.g. `tabandblank.com`
- `ORIGIN_IP` — optional, defaults to the `SOURCE` variable at the top of the script (your VPS IP, to bypass Cloudflare).
- `PATTERN` — optional, greps the origin HTML for matching lines (e.g. `googletagmanager`).
- `list.txt` — batch mode, one `DOMAIN [ORIGIN_IP] [PATTERN]` per line.

### Example output

```
 example.com
=======================================================================
  Public DNS.......: 172.66.147.243, 104.20.23.154
  ORIGIN   1.1.1.1 (bypassing Cloudflare with --resolve):
       HTTP 403   ip 1.1.1.1   0.075148s
         Server: cloudflare
         => you go through Cloudflare
  PUBLIC (via normal DNS / Cloudflare):
       HTTP 200   ip 172.66.147.243   0.086374s
  VERDICT: ALIVE - the origin server responds OK.
```
