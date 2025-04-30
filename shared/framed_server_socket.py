"""Defines FramedServerSocket to receive connections from FramedSockets.

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
import socket
import threading
from typing import Callable

from shared.framed_socket import FramedSocket


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

        # Track client connections
        self._connections = set()

        # Indicates that the server is closing
        self._closed = False

    def start_server(
            self, conn_handler: Callable[[FramedSocket], None]
    ) -> None:
        """Start receiving connections, passing them to a handler."""
        recv_thread = threading.Thread(
            target=self._receive_conn_forever, args=(conn_handler,)
        )
        recv_thread.start()

    def close_server(self) -> None:
        """Close the server."""
        self._closed = True

        # Necessary to close a socket while it's blocked
        try:
            self._sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

        self._sock.close()

        # Close all connected sockets
        for conn in list(self._connections):
            conn.close()

    def is_closed(self) -> bool:
        """Check if the server is closed."""
        return self._closed

    def _receive_conn_forever(
            self, handler: Callable[[FramedSocket], None]
    ) -> None:
        """Receive connections and pass them to a handler."""
        self._sock.listen()
        while not self._closed:
            # Receive connection
            try:
                conn, addr = self._sock.accept()
            # Socket closed while accepting
            except OSError:
                break

            # Wrap connection socket with FramedSocket
            framed_conn = FramedSocket(conn)

            # Start thread to handle the connection
            conn_thread = threading.Thread(
                target=self._handle_connection, args=(handler, framed_conn,)
            )
            conn_thread.start()

    def _handle_connection(
            self, handler: Callable[[FramedSocket], None], conn: FramedSocket
    ) -> None:
        """Handle a server connection."""
        # Track the connection
        self._connections.add(conn)

        # Automatically untrack the connection when it closes
        original_close = conn.close
        def close_and_untrack():
            self._connections.discard(conn)
            original_close()
        conn.close = close_and_untrack

        # Handle the connection
        handler(conn)
