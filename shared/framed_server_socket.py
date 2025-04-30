"""Defines FramedServerSocket to receive connections from FramedSockets."""

import socket
import threading
from typing import Callable, NoReturn

from framed_socket import FramedSocket


class FramedServerSocket:
    """A multi-threaded TCP server utilizing framed sockets."""

    def __init__(
            self, addr: tuple[str, int], sock: socket.socket = None
    ) -> None:
        """Initialize the FramedServerSocket."""
        self._sock = sock or socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._addr = addr

        # Bind the socket to the specified address
        self._sock.bind(self._addr)

    def start_server(
            self, connection_handler: Callable[[FramedSocket], None]
    ) -> None:
        """Start receiving connections, passing them to a handler."""
        recv_thread = threading.Thread(
            target=self._receive_conn_forever, args=(connection_handler,)
        )
        recv_thread.start()

    def _receive_conn_forever(
            self, handler: Callable[[FramedSocket], None]
    ) -> NoReturn:
        """Receive connections and pass them to a handler."""
        self._sock.listen()
        while True:
            # Receive connection
            conn, addr = self._sock.accept()

            # Wrap connection socket with FramedSocket
            framed_conn = FramedSocket(addr, sock=conn)

            # Start thread to handle the connection
            conn_thread = threading.Thread(
                target=handler, args=(framed_conn,), daemon=True
            )
            conn_thread.start()
