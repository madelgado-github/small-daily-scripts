import os
import tinytuya
from mcp.server.fastmcp import FastMCP

# Tuya credentials
API_KEY    = os.environ.get("TUYA_API_KEY",    "your_api_key")
API_SECRET = os.environ.get("TUYA_API_SECRET", "your_api_secret")
REGION     = os.environ.get("TUYA_REGION",     "eu")

# Device map: name -> (device_id, switch_code)
DEVICES = {
    "lamp":     ("device_one_id", "switch_1"),
    "strip1":   ("device_two_id", "switch_1"),
    "strip2":   ("device_two_id", "switch_2"),
    "strip3":   ("device_two_id", "switch_3"),
    "stripusb": ("device_two_id", "switch_usb1"),
}

mcp = FastMCP("Tuya Smart Plugs")


def _connect(device_id: str) -> tinytuya.Cloud:
    return tinytuya.Cloud(
        apiRegion=REGION,
        apiKey=API_KEY,
        apiSecret=API_SECRET,
        apiDeviceID=device_id,
    )


def _get_status(name: str) -> bool | None:
    device_id, switch = DEVICES[name]
    c = _connect(device_id)
    result = c.getstatus(device_id)
    for dp in result.get("result", []):
        if dp.get("code") == switch:
            return dp["value"]
    return None


def _send(name: str, value: bool) -> str:
    device_id, switch = DEVICES[name]
    c = _connect(device_id)
    resp = c.cloudrequest(
        f"v1.0/devices/{device_id}/commands",
        action="POST",
        post={"commands": [{"code": switch, "value": value}]},
    )
    if resp.get("success"):
        return f"{name}: {'ON' if value else 'OFF'}"
    return f"Error on {name}: {resp}"


@mcp.tool()
def turn_on(device: str) -> str:
    """Turn on a smart plug.

    Args:
        device: Device name. Options: lamp, strip1, strip2, strip3, stripusb
    """
    if device not in DEVICES:
        return f"Unknown device: '{device}'. Options: {', '.join(DEVICES)}"
    return _send(device, True)


@mcp.tool()
def turn_off(device: str) -> str:
    """Turn off a smart plug.

    Args:
        device: Device name. Options: lamp, strip1, strip2, strip3, stripusb
    """
    if device not in DEVICES:
        return f"Unknown device: '{device}'. Options: {', '.join(DEVICES)}"
    return _send(device, False)


@mcp.tool()
def toggle(device: str) -> str:
    """Toggle a smart plug (turns it off if on, and on if off).

    Args:
        device: Device name. Options: lamp, strip1, strip2, strip3, stripusb
    """
    if device not in DEVICES:
        return f"Unknown device: '{device}'. Options: {', '.join(DEVICES)}"
    current = _get_status(device)
    if current is None:
        return f"Could not get status for {device}."
    return _send(device, not current)


@mcp.tool()
def status(device: str) -> str:
    """Get the current state (on/off) of a smart plug.

    Args:
        device: Device name. Options: lamp, strip1, strip2, strip3, stripusb
    """
    if device not in DEVICES:
        return f"Unknown device: '{device}'. Options: {', '.join(DEVICES)}"
    value = _get_status(device)
    if value is None:
        return f"Could not get status for {device}."
    return f"{device}: {'ON' if value else 'OFF'}"


@mcp.tool()
def all_status() -> str:
    """Get the current state of all smart plugs."""
    lines = []
    for name in DEVICES:
        value = _get_status(name)
        if value is None:
            lines.append(f"{name}: ERROR")
        else:
            lines.append(f"{name}: {'ON' if value else 'OFF'}")
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
