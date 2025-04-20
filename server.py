"""A server for a chatroom."""

import socket
import threading
from typing import Callable

from config import HOST, SEND_PORT, RECV_PORT


class ChatServer:
    """A multithreaded server to send and receive chatroom messages."""

    def __init__(self):
        # Socket to send messages
        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.send_sock.bind((HOST, SEND_PORT))
        self.send_sock.listen()

        # Socket to receive messages
        self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recv_sock.bind((HOST, RECV_PORT))
        self.recv_sock.listen()

        send_thread = threading.Thread(target=self.receive_connections,
                                       args=(self.send_sock,
                                             self.send_handler))
        recv_thread = threading.Thread(target=self.receive_connections,
                                       args=(self.recv_sock,
                                             self.receive_handler))

        send_thread.start()
        recv_thread.start()


    def receive_connections(
            self, sock: socket.socket, handler: Callable[[socket.socket], None]
    ) -> None:
        while True:
            conn, _ = self.recv_sock.accept()
            handler(conn)
            conn.close()

    def receive_handler(self, conn: socket.socket) -> None:
        print("connection accepted")

    def send_handler(self, conn: socket.socket) -> None:
        print("connection accepted")


def main():
    serv = ChatServer()


if __name__ == "__main__":
    main()
