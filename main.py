import yaml
import os
from matrix_client.client import MatrixClient
from matrix_client.errors import MatrixRequestError
import config

CONFIG_PATH = "../config/config.yml"

def get_token():
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    matrix_conf = config.get("matrix", {})
    homeserver = matrix_conf.get("homeserver")
    username = matrix_conf.get("username")
    password = matrix_conf.get("password")
    device_id = matrix_conf.get("device_id")

    if not all([homeserver, username, password]):
        print("Missing configuration values.")
        return

    client = MatrixClient(homeserver)
    try:
        token = client.login(username, password)
        return token, homeserver
    except MatrixRequestError as e:
        print(f"Login failed: {e}")
        return None


if (config.create_config()==1):
    exit(0)
token, homeserver = get_token()
client = MatrixClient(homeserver, token)

# List all devices for the account
devices_response = client.api._send(
    method="GET",
    path="/devices"
)

devices = devices_response.get("devices", [])

if not devices:
    exit(1)

# Filter out devices with missing or None last_seen_ts
active_devices = [d for d in devices if d.get("last_seen_ts") is not None]

if not active_devices:
    # If none have timestamps, fallback to first device (should be the new one just created)
    device_id = devices[0]["device_id"]
else:
    # Pick device with latest timestamp
    device_id = max(active_devices, key=lambda d: d["last_seen_ts"])["device_id"]


new_name = "Multi Chat Desktop (PyQt6)"
client.api._send(
    method="PUT",
    path=f"/devices/{device_id}",
    content={"display_name": new_name}
)

print(f"Paste token={token} and device_id={device_id} !")
