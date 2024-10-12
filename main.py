#!/usr/bin/env python3

import asyncio
import json
import logging
import signal
import time

import Ice
import nio

import MumbleServer
from callbacks import MetaCallback, ServerCallback
from common import CONFIG_FILE
from message_sender import MessageSender

logging.basicConfig(level=logging.INFO)

stopping = False


def stop_gracefully(signum, frame):
    global stopping
    stopping = True


def get_matrix_client(creds: dict[str, str]) -> nio.AsyncClient:
    client = nio.AsyncClient(creds["homeserver"])
    client.access_token = creds["access_token"]
    client.user_id = creds["user_id"]
    client.device_id = creds["device_id"]
    return client


async def main():
    signal.signal(signal.SIGTERM, stop_gracefully)
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    matrix_client = get_matrix_client(config["matrix"])

    with Ice.initialize() as communicator:
        ctx = {"secret": config["mumble"]["ice_secret"]}
        proxy = communicator.stringToProxy("Meta:tcp -h 127.0.0.1 -p 6502").ice_context(ctx)
        meta = MumbleServer.MetaPrx.checkedCast(proxy)
        server = meta.getAllServers()[0].ice_context(ctx)
        adapter = communicator.createObjectAdapterWithEndpoints("Callback.Client", "tcp -h 127.0.0.1")
        adapter.activate()

        room_id = config["matrix"]["room_id"]
        sender = MessageSender(matrix_client, room_id)

        server_callback = ServerCallback(ctx, server, sender)
        server_callback_prx = MumbleServer.ServerCallbackPrx.checkedCast(adapter.addWithUUID(server_callback))
        users = server.getUsers()
        for _, u in users.items():
            server_callback.session_channel_map[u.session] = u.channel
        server.addCallback(server_callback_prx)

        meta_callback = MumbleServer.MetaCallbackPrx.checkedCast(
            adapter.addWithUUID(MetaCallback(ctx, adapter, server, sender))
        )
        meta.addCallback(meta_callback)

        while True:
            if stopping:
                matrix_client.close()
                raise SystemExit
            else:
                time.sleep(3)
                await sender.check_for_messages()


if __name__ == "__main__":
    asyncio.run(main())
