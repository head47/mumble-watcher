import json
import logging
import signal
import time
from typing import no_type_check

import Ice
import nio
from tenacity import retry, wait_fixed

import MumbleServer
from callbacks import MetaCallback, ServerCallback
from common import CONFIG_FILE
from message_sender import MessageSender

logging.basicConfig(level=logging.INFO, style="{", format="[{asctime}] {levelname} {message}")

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


@no_type_check
@retry(wait=wait_fixed(3))
def get_ice_meta(proxy: Ice.ObjectPrx) -> MumbleServer.MetaPrx:
    return MumbleServer.MetaPrx.checkedCast(proxy)


async def main():
    signal.signal(signal.SIGTERM, stop_gracefully)
    with open(CONFIG_FILE) as f:
        cfg = json.load(f)
    matrix_client = get_matrix_client(cfg["matrix"])

    with Ice.initialize() as communicator:
        ctx = {"secret": cfg["mumble"]["ice_secret"]}
        proxy = communicator.stringToProxy(f"Meta:{cfg['mumble']['ice_endpoint']}").ice_context(ctx)
        meta = get_ice_meta(proxy)
        server = meta.getAllServers()[0].ice_context(ctx)
        adapter = communicator.createObjectAdapterWithEndpoints("Callback.Client", cfg["mumble"]["callback_endpoint"])
        adapter.activate()

        room_id = cfg["matrix"]["room_id"]
        sender = MessageSender(matrix_client, room_id)

        server_callback = ServerCallback(server, sender)
        server_callback_prx = MumbleServer.ServerCallbackPrx.checkedCast(adapter.addWithUUID(server_callback))
        users = server.getUsers()
        for _, u in users.items():
            server_callback.session_channel_map[u.session] = u.channel
        server.addCallback(server_callback_prx)

        meta_callback = MumbleServer.MetaCallbackPrx.checkedCast(
            adapter.addWithUUID(MetaCallback(ctx, adapter, server, sender))
        )
        meta.addCallback(meta_callback)

        logging.info("Listening for events")

        while True:
            if stopping:
                await matrix_client.close()
                raise SystemExit
            else:
                time.sleep(3)
                await sender.check_for_messages()
