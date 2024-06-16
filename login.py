#!/usr/bin/env python3

import asyncio
import getpass
import json
import os

from common import CREDS_FILE, DEVICE_NAME, HOMESERVER, USER_ID
from nio import AsyncClient, LoginResponse


async def main() -> None:
    if os.path.exists(CREDS_FILE):
        print(f"Creds already configured in {CREDS_FILE}")
        raise SystemExit

    client = AsyncClient(HOMESERVER, USER_ID)
    password = getpass.getpass()
    resp = await client.login(password, device_name=DEVICE_NAME)
    await client.close()
    if isinstance(resp, LoginResponse):
        open(CREDS_FILE, "w").close()
        os.chmod(CREDS_FILE, 0o600)
        with open(CREDS_FILE, "w") as f:
            json.dump(
                {
                    "homeserver": HOMESERVER,
                    "user_id": resp.user_id,
                    "device_id": resp.device_id,
                    "access_token": resp.access_token,
                },
                f,
            )
        print(f"Logged in as {resp.user_id}. Credentials saved to {CREDS_FILE}")
    else:
        raise Exception(f"Failed to log in: {resp}")


if __name__ == "__main__":
    asyncio.run(main())
