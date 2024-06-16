#!/usr/bin/env python3

import asyncio
import json
import logging
import signal

import aiofiles
import discord
import nio

from common import CREDS_FILE, ROOM_ID

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


class DiscordClient(discord.Client):
    matrix_client: nio.AsyncClient

    async def on_voice_state_update(
        self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState
    ):
        if before.channel is None:
            if after.channel is None:
                return
            else:
                formatted_message = (
                    f"[{member.guild.name}] <b>{member.display_name}</b> присоединились к 🔈{after.channel.name}"
                )
                message = f"[{member.guild.name}] {member.display_name} присоединились к 🔈{after.channel.name}"
        else:
            if after.channel is None:
                formatted_message = (
                    f"[{member.guild.name}] <b>{member.display_name}</b> покинули 🔈{before.channel.name}"
                )
                message = f"[{member.guild.name}] {member.display_name} покинули 🔈{before.channel.name}"
            else:
                formatted_message = f"<b>{member.display_name}</b> перешли из {member.guild.name}:🔈{before.channel.name} в {member.guild.name}:🔈{after.channel.name}"
                message = f"{member.display_name} перешли из {member.guild.name}:🔈{before.channel.name} в {member.guild.name}:🔈{after.channel.name}"
        await self.matrix_client.room_send(
            room_id=ROOM_ID,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "format": "org.matrix.custom.html",
                "formatted_body": formatted_message,
                "body": message,
            },
        )


async def main():
    signal.signal(signal.SIGTERM, stop_gracefully)
    async with aiofiles.open(CREDS_FILE) as f:
        contents = await f.read()
    creds = json.loads(contents)
    matrix_client = get_matrix_client(creds)

    intents = discord.Intents.default()
    intents.voice_states = True
    discord_client = DiscordClient(intents=intents)
    discord_client.matrix_client = matrix_client
    async with asyncio.TaskGroup() as tg:
        task = tg.create_task(discord_client.start(creds["discord_token"]))
        while True:
            if stopping:
                await matrix_client.close()
                raise SystemExit
            else:
                await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(main())
