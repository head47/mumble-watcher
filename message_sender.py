import logging
import threading

import nio


class MessageSender:
    "Message sender that accepts messages from other threads"
    matrix_client: nio.AsyncClient
    room_id: str
    messages: list[tuple[str, str]]
    message_lock: threading.Lock

    def __init__(self, matrix_client, room_id):
        self.matrix_client = matrix_client
        self.room_id = room_id
        self.messages = []
        self.messages_lock = threading.Lock()

    def send_message(self, message, html_message):
        with self.messages_lock:
            self.messages.append((message, html_message))
            logging.info(f"Added '{message}' to queue")

    async def check_for_messages(self):
        with self.messages_lock:
            for message, html_message in self.messages:
                await self._send_message(message, html_message)
            self.messages = []

    async def _send_message(self, message, html_message):
        await self.matrix_client.room_send(
            room_id=self.room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "format": "org.matrix.custom.html",
                "formatted_body": html_message,
                "body": message,
            },
        )
        logging.info(f"Sent '{message}'")
