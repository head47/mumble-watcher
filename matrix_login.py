#!/usr/bin/env python3

import asyncio
import getpass
import json
import os

from nio import AsyncClient, LoginResponse

from common import CONFIG_FILE


async def main() -> None:
    try:
        with open(CONFIG_FILE) as f:
            cfg = json.load(f)
        if "matrix" in cfg:
            print(f"Creds already configured in {CONFIG_FILE}")
            raise SystemExit
        cfg["matrix"] = {}
    except (FileNotFoundError, json.JSONDecodeError):
        open(CONFIG_FILE, "w").close()
        os.chmod(CONFIG_FILE, 0o600)
        cfg = {"matrix": {}}

    homeserver = input("Homeserver: ")
    user_id = input("User ID: ")
    device_name = input("Device name: ")
    room_id = input("Room ID: ")
    password = getpass.getpass()

    client = AsyncClient(homeserver, user_id)
    resp = await client.login(password, device_name=device_name)
    await client.close()

    if isinstance(resp, LoginResponse):
        cfg["matrix"]["homeserver"] = homeserver
        cfg["matrix"]["user_id"] = resp.user_id
        cfg["matrix"]["device_id"] = resp.device_id
        cfg["matrix"]["access_token"] = resp.access_token
        cfg["matrix"]["room_id"] = room_id

        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f)
        print(f"Logged in as {resp.user_id}. Credentials saved to {CONFIG_FILE}")
    else:
        raise Exception(f"Failed to log in: {resp}")


if __name__ == "__main__":
    asyncio.run(main())
