"""A server for a chatroom.

Author: Ryan Buck
Class: CSI-275-02
Assignment: Final Project

Certification of Authenticity:
I certify that this is entirely my own work, except where I have given
fully-documented references to the work of others. I understand the definition
and consequences of plagiarism and acknowledge that the assessor of this
assignment may, for the purpose of assessing this assignment:
- Reproduce this assignment and provide a copy to another member of academic
- staff; and/or Communicate a copy of this assignment to a plagiarism checking
- service (which may then retain a copy of this assignment on its database for
- the purpose of future plagiarism checking)
"""
import json

from config import HOST, WRITE_PORT, READ_PORT
from shared.framed_server_socket import FramedServerSocket
from shared.framed_socket import FramedSocket


class ChatServer:
    """Chatroom server."""

    def __init__(self) -> None:
        """Initialize the chat server."""
        # Sends messages to the connected clients
        self.write_sock = FramedServerSocket((HOST, WRITE_PORT))

        # Reads messages from the connected clients
        self.read_sock = FramedServerSocket((HOST, READ_PORT))

        # Stores users and their connection sockets
        self.users: dict[str, FramedSocket] = dict()

    def start(self) -> None:
        """Start the chat server."""
        print("Press CTRL+C at any time to close the server.")

        # Receive connections forever, storing them to send messages to later
        self.write_sock.start_server(conn_handler=self._handle_write_conn)

        # Receive connections forever, reading messages from them
        self.read_sock.start_server(conn_handler=self._handle_read_conn)

        # Wait until a keyboard interrupt then close
        try:
            while True:
                input()
        except KeyboardInterrupt:
            print("Server closing...")
            self.write_sock.close_server()
            self.read_sock.close_server()

    def _handle_write_conn(self, conn: FramedSocket) -> None:
        """Handle a connection from a client's receiving socket."""
        msg = conn.recv_msg()
        msg_dict = json.loads(msg)
        username = msg_dict["sender"]

        # Add to dict of connected users
        self._add_user(username, conn)

        print(f"Connection to {username} opened")

    def _handle_read_conn(self, conn: FramedSocket) -> None:
        """Handle a connection from a client's sending socket."""
        # Receive messages from the client until they disconnect
        conn.receive_msg_forever(self._handle_read_msg)
        conn.close()

    def _handle_read_msg(self, msg: str) -> bool:
        """Handle a message sent from a client."""
        msg_dict = json.loads(msg)
        msg_type = msg_dict["type"]
        username = msg_dict["sender"]

        match msg_type.upper():
            case "EXIT":
                self._remove_user(username)
                self._forward_all(msg)
                print(f"Connection from {username} closed")

                # Stop reading messages
                return False
            case "BROADCAST":
                self._forward_all(msg)
                print(f"Broadcast message from {username}")
            case "PRIVATE":
                recipient = msg_dict["recipient"]
                self._forward_one(msg, recipient)
                print(f"Private message from {username} to {recipient}")

        # Continue reading messages so long as the server isn't closed
        return not self.read_sock.is_closed()

    def _forward_all(self, msg: str) -> None:
        """Forward a message to all clients."""
        for conn in self.users.values():
            conn.send_msg(msg)

    def _forward_one(self, msg: str, recipient: str) -> None:
        """Forward a message to one client."""
        try:
            conn = self.users[recipient]
        except KeyError:
            return
        conn.send_msg(msg)

    def _add_user(self, username: str, conn: FramedSocket) -> None:
        """Add a user."""
        self.users[username] = conn

    def _remove_user(self, username: str) -> None:
        """Remove a user."""
        self.users[username].close()
        self.users.pop(username)
