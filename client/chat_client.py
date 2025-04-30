"""A client for a chatroom."""

import json
import threading
from typing import Callable

from shared.config import HOST, WRITE_PORT, READ_PORT
from shared.framed_socket import FramedSocket


class ChatClient:
    """A multithreaded client to send and receive chatroom messages."""

    class ManualMessageSendError(Exception):
        """Message that should only be sent by the class was sent manually."""
        pass

    def __init__(self, username: str) -> None:
        """Initialize the chat client."""
        self.username = username

        # Sends messages to the server
        self._send_sock = FramedSocket()

        # Connect the send sock to the server
        # READ_PORT because we send to where the server receives
        self._send_sock.connect((HOST, READ_PORT))

        # Receives messages from the server
        self._recv_sock = FramedSocket()

        # Connect the recv sock to the server
        # WRITE_PORT because we recv from where the server sends
        self._recv_sock.connect((HOST, WRITE_PORT))

        # Callbacks for when a message is received
        self._recv_msg_listeners = []

    def start(self) -> None:
        """Join the chatroom."""
        # Send start to the chat server
        self._send_start()

        # Start receiving messages from the server
        threading.Thread(
            target=self._recv_sock.receive_msg_forever,
            args=(self._receive_msg,),
            daemon=True
        )

    def exit(self):
        """Handle exiting the chatroom."""
        # Send exit to the server
        self._send_exit()

        # Close sockets
        self._send_sock.close()
        self._recv_sock.close()

    def on_receive_message(self, listener: Callable[[str], None]) -> None:
        """Add a listener for receiving messages."""
        self._recv_msg_listeners.append(listener)

    def send_from_dict(self, msg_dict: dict) -> None:
        """Send a message from dictionary data."""
        msg_type = msg_dict["type"]

        match msg_type.upper():
            case "BROADCAST":
                msg = msg_dict["message"]
                self.send_broadcast(msg)
            case "PRIVATE":
                msg = msg_dict["message"]
                recipient = msg_dict["recipient"]
                self.send_private(msg, recipient)
            case "START" | "EXIT":
                raise self.ManualMessageSendError(
                    "Start and exit should be called through their respective"
                    " functions, the message should not be sent manually from"
                    " outside the class."
                )

    def send_broadcast(self, msg: str) -> None:
        """Send a broadcast message to all recipients."""
        self._send_msg(
            self._send_sock,
            msg_type="BROADCAST",
            sender=self.username,
            message=msg,
        )

    def send_private(self, msg: str, recipient: str) -> None:
        """Send a private message to one recipient."""
        self._send_msg(
            self._send_sock,
            msg_type="PRIVATE",
            sender=self.username,
            recipient=recipient,
            message=msg,
        )

    def _receive_msg(self, msg: str) -> None:
        """Call receive message listeners when receiving a message."""
        for callback in self._recv_msg_listeners:
            callback(msg)

    def _send_start(self) -> None:
        """Send a start message to the server."""
        self._send_msg(
            self._recv_sock,
            msg_type="START",
            sender=self.username,
        )

    def _send_exit(self) -> None:
        """Send an exit message to the server."""
        self._send_msg(
            self._send_sock,
            msg_type="EXIT",
            sender=self.username,
        )

    def _send_msg(
            self,
            sock: FramedSocket,
            msg_type: str,
            sender: str,
            recipient: str = None,
            message: str = None
    ) -> None:
        """Send a chat message to the server."""
        # Initialize message dict
        msg_dict = {
            "type": msg_type,
            "sender": sender
        }

        # Add optional recipient field
        if recipient:
            msg_dict["recipient"] = recipient

        # Add optional message field
        if message:
            msg_dict["message"] = message

        # Convert to json and send
        sock.send_msg(json.dumps(msg_dict))
