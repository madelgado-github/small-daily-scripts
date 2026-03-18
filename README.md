# daily-scripts

A collection of utility scripts for day-to-day system automation tasks.

---

## cloudflare/update_ddns.ps1

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
---

## iot/tuya.py

A command-line script to control Tuya smart plugs and power strips directly from the terminal.

### How it works

1. Connects to the Tuya Cloud API using the configured credentials.
2. Resolves the target device and switch code from the local device map.
3. Executes the requested action (on, off, toggle, or status) via the Tuya REST API.
4. Prints the result to stdout.

### Requirements

- Python 3.10+
- [`tinytuya`](https://github.com/jasonacox/tinytuya) library (`pip install tinytuya`)
- A [Tuya developer account](https://iot.tuya.com) with an active project and API credentials

### Configuration

Edit the constants at the top of the script:

```python
API_KEY    = "your_api_key"
API_SECRET = "your_api_secret"
REGION     = "eu"  # eu, us, in, cn
```

And update `DEVICES` with your own device IDs and switch codes:

```python
DEVICES = {
    "lamp":     ("device_one_id", "switch_1"),
    "strip1":   ("device_two_id", "switch_1"),
    ...
}
```

### Usage

```
python iot/tuya.py <device> <action>
```

| Argument | Options |
|----------|---------|
| `device` | `lamp`, `strip1`, `strip2`, `strip3`, `stripusb`, `all` |
| `action` | `on`, `off`, `status`, `toggle` |

```bash
python iot/tuya.py lamp on          # Turn on the lamp
python iot/tuya.py strip1 off       # Turn off strip1
python iot/tuya.py lamp toggle      # Toggle the lamp
python iot/tuya.py strip2 status    # Get status of strip2
python iot/tuya.py all              # Get status of all devices
```

---

## iot/tuya_mcp.py

An [MCP](https://modelcontextprotocol.io) server that exposes Tuya smart plug control as tools, allowing AI assistants (e.g. Claude) to turn devices on/off or query their state.

### How it works

Wraps the same Tuya Cloud API calls as `tuya.py` and exposes them as MCP tools via `FastMCP`:

| Tool | Description |
|------|-------------|
| `turn_on(device)` | Turns on the specified device |
| `turn_off(device)` | Turns off the specified device |
| `toggle(device)` | Toggles the specified device |
| `status(device)` | Returns current state (ON/OFF) |
| `all_status()` | Returns state of all devices |

### Requirements

- Python 3.10+
- [`tinytuya`](https://github.com/jasonacox/tinytuya) (`pip install tinytuya`)
- [`mcp`](https://github.com/modelcontextprotocol/python-sdk) (`pip install mcp`)

### Configuration

Credentials are read from environment variables (falling back to hardcoded placeholders):

```bash
export TUYA_API_KEY="your_api_key"
export TUYA_API_SECRET="your_api_secret"
export TUYA_REGION="eu"
```

Update the `DEVICES` map in the script with your own device IDs, same as `tuya.py`.

### Usage

Run the MCP server:

```bash
python iot/tuya_mcp.py
```

To register it in Claude Desktop, add it to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "tuya": {
      "command": "python",
      "args": ["C:/path/to/iot/tuya_mcp.py"],
      "env": {
        "TUYA_API_KEY": "your_api_key",
        "TUYA_API_SECRET": "your_api_secret",
        "TUYA_REGION": "eu"
      }
    }
  }
}
```

---

miguel_AT_onlywebs.com /surtursoftware