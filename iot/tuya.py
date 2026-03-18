import tinytuya
import sys

# Tuya credentials
API_KEY    = "your_api_key"
API_SECRET = "your_api_secret"
REGION     = "eu"  # Central Europe

# Device map: name -> (device_id, switch_code)
DEVICES = {
    "lamp":     ("device_one_id", "switch_1"),
    "strip1":   ("device_two_id", "switch_1"),
    "strip2":   ("device_two_id", "switch_2"),
    "strip3":   ("device_two_id", "switch_3"),
    "stripusb": ("device_two_id", "switch_usb1"),
}

def connect(device_id):
    return tinytuya.Cloud(
        apiRegion=REGION,
        apiKey=API_KEY,
        apiSecret=API_SECRET,
        apiDeviceID=device_id
    )

def status(name):
    device_id, switch = DEVICES[name]
    c = connect(device_id)
    result = c.getstatus(device_id)
    for dp in result.get("result", []):
        if dp.get("code") == switch:
            on = dp["value"]
            print(f"{name}: {'ON' if on else 'OFF'}")
            return on
    print(f"Could not get status for {name}.")
    return None

def send(name, value: bool):
    device_id, switch = DEVICES[name]
    c = connect(device_id)
    resp = c.cloudrequest(
        f"v1.0/devices/{device_id}/commands",
        action="POST",
        post={"commands": [{"code": switch, "value": value}]}
    )
    if resp.get("success"):
        print(f"{name}: {'ON' if value else 'OFF'}")
    else:
        print(f"Error on {name}: {resp}")

def toggle(name):
    current = status(name)
    if current is True:
        send(name, False)
    elif current is False:
        send(name, True)

def all_status():
    for name in DEVICES:
        status(name)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tuya_enchufe.py <device> <action>")
        print("Devices: lamp, strip1, strip2, strip3, stripusb, all")
        print("Actions: on, off, status, toggle")
        sys.exit(1)

    name = sys.argv[1].lower()

    if name == "all" and (len(sys.argv) < 3 or sys.argv[2].lower() == "status"):
        all_status()
        sys.exit(0)

    if name not in DEVICES:
        print(f"Unknown device: {name}")
        print(f"Options: {', '.join(DEVICES.keys())}, all")
        sys.exit(1)

    if len(sys.argv) < 3:
        status(name)
        sys.exit(0)

    cmd = sys.argv[2].lower()
    if cmd == "on":
        send(name, True)
    elif cmd == "off":
        send(name, False)
    elif cmd == "status":
        status(name)
    elif cmd == "toggle":
        toggle(name)
    else:
        print(f"Unknown action: {cmd}")
        print("Options: on / off / status / toggle")
