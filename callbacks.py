import Ice

import MumbleServer
from message_sender import MessageSender


class ServerCallback(MumbleServer.ServerCallback):
    ctx: dict
    server: MumbleServer.ServerPrx
    sender: MessageSender
    session_channel_map: dict[int, int]

    def __init__(self, ctx, server, sender):
        self.ctx = ctx
        self.server = server
        self.sender = sender
        self.session_channel_map = {}

    def userConnected(self, user, current=None):
        channel = self.server.getChannelState(user.channel)
        self.session_channel_map[user.session] = user.channel

        message = f"{user.name} присоединились к 🔈{channel.name}"
        formatted_message = f"<b>{user.name}</b> присоединились к 🔈{channel.name}"
        self.sender.send_message(message, formatted_message)

    def userDisconnected(self, user, current=None):
        channel = self.server.getChannelState(user.channel)
        del self.session_channel_map[user.session]

        message = f"{user.name} отключились от 🔈{channel.name}"
        formatted_message = f"<b>{user.name}</b> отключились от 🔈{channel.name}"
        self.sender.send_message(message, formatted_message)

    def userStateChanged(self, user, current=None):
        if user.channel != self.session_channel_map[user.session]:
            try:
                old_channel = self.server.getChannelState(self.session_channel_map[user.session])
            except MumbleServer.InvalidChannelException:
                old_channel_name = "<несуществующего канала>"
            else:
                old_channel_name = old_channel.name
            channel = self.server.getChannelState(user.channel)
            self.session_channel_map[user.session] = user.channel

            message = f"{user.name} перешли из 🔈{old_channel_name} в 🔈{channel.name}"
            formatted_message = f"<b>{user.name}</b> перешли из 🔈{old_channel_name} в 🔈{channel.name}"
            self.sender.send_message(message, formatted_message)

    def userTextMessage(self, user, message, current=None): ...

    def channelCreated(self, channel, current=None): ...

    def channelRemoved(self, channel, current=None): ...

    def channelStateChanged(self, channel, current=None): ...


class MetaCallback(MumbleServer.MetaCallback):
    ctx: dict
    adapter: Ice.ObjectAdapterI
    server: MumbleServer.ServerPrx
    sender: MessageSender

    def __init__(self, ctx, adapter, server, sender):
        self.ctx = ctx
        self.adapter = adapter
        self.server = server
        self.sender = sender

    def started(self, server, current=None):
        self.server = server.ice_context(self.ctx)
        server_callback = ServerCallback(self.ctx, self.server, self.sender)
        server_callback_prx = MumbleServer.ServerCallbackPrx.checkedCast(self.adapter.addWithUUID(server_callback))
        users = server.getUsers()
        for _, u in users.items():
            server_callback.session_channel_map[u.session] = u.channel
        server.addCallback(server_callback_prx)

    def stopped(self, server, current=None): ...
