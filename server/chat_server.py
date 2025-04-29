import json

from shared.config import HOST, WRITE_PORT, READ_PORT
from shared.framed_server_socket import FramedServerSocket
from shared.framed_socket import FramedSocket


class ChatServer:

    def __init__(self):
        # Sends messages to the connected clients
        self.write_sock = FramedServerSocket((HOST, WRITE_PORT))

        # Reads messages from the connected clients
        self.read_sock = FramedServerSocket((HOST, READ_PORT))

        # Stores users and their connection sockets
        self.users: dict[str, FramedSocket] = dict()

    def start(self):
        # Receive connections forever, storing them to send messages to later
        self.write_sock.start_server(
            connection_handler=self._handle_write_conn
        )

        # Receive connections forever, reading messages from them
        self.read_sock.start_server(
            connection_handler=self._handle_read_conn
        )

    def _handle_write_conn(self, conn: FramedSocket):
        """Handle a connection from a client's receiving socket."""
        msg = conn.recv_msg()
        msg_dict = json.loads(msg)
        username = msg_dict["sender"]

        self._add_user(username, conn)

    def _handle_read_conn(self, conn: FramedSocket):
        """Handle a connection from a client's sending socket."""
        # Receive messages from the client until they disconnect.
        conn.receive_msg_forever(self._handle_read_msg)

    def _handle_read_msg(self, msg: str):
        """Handle a message sent from a client."""
        msg_dict = json.loads(msg)

        match msg_dict["type"].upper():
            case "EXIT":
                self._remove_user(msg_dict["sender"])
                self._forward_all(msg)
            case "BROADCAST":
                self._forward_all(msg)
            case "PRIVATE":
                self._forward_one(msg, msg_dict["recipient"])

    def _forward_all(self, msg: str):
        for conn in self.users.values():
            conn.send_msg(msg)

    def _forward_one(self, msg: str, recipient: str):
        conn = self.users[recipient]
        conn.send_msg(msg)

    def _add_user(self, username: str, conn: FramedSocket):
        self.users[username] = conn

    def _remove_user(self, username: str):
        self.users.pop(username)
