# iot/

Scripts to control Tuya smart plugs and power strips from the terminal, and to expose them as MCP tools for AI assistants.

---

## tuya.py

A command-line script to control Tuya smart plugs directly from the terminal.

### How it works

1. Connects to the Tuya Cloud API using the configured credentials.
2. Resolves the target device and switch code from the local device map.
3. Executes the requested action (on, off, toggle, or status) via the Tuya REST API.
4. Prints the result to stdout.

### Requirements

- Python 3.10+
- [`tinytuya`](https://github.com/jasonacox/tinytuya) (`pip install tinytuya`)
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
    "lamp":   ("device_one_id", "switch_1"),
    "strip1": ("device_two_id", "switch_1"),
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
python iot/tuya.py lamp on        # Turn on the lamp
python iot/tuya.py strip1 off     # Turn off strip1
python iot/tuya.py lamp toggle    # Toggle the lamp
python iot/tuya.py strip2 status  # Get status of strip2
python iot/tuya.py all            # Get status of all devices
```

---

## tuya_mcp.py

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
