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
