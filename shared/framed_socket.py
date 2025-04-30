"""Defines FramedSocket, a length prefixed TCP socket."""

import socket
from typing import Callable, NoReturn

from shared.config import FRAME_BYTES, ENCODING


class FramedSocket:
    """A length prefixed TCP socket."""

    class EndOfMessageError(EOFError):
        """Indicates the message ended before it was expected."""
        pass

    def __init__(
            self,
            sock: socket.socket = None,
            frame_bytes: int = FRAME_BYTES,
            encoding: str = ENCODING
    ) -> None:
        """Initialize the FramedSocket."""
        self._sock = sock or socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._frame_bytes = frame_bytes
        self._encoding = encoding

    def receive_msg_forever(self, handler: Callable[[str], bool]) -> None:
        """Receive messages forever, passing them to a handler.

        The handler takes the msg as input and returns False to stop receiving
        and True otherwise.
        """
        receiving = True
        while receiving:
            try:
                # Receive message
                msg = self.recv_msg()
            # Close socket while receiving
            except OSError:
                break

            receiving = handler(msg)

    def recv_msg(self) -> str:
        """Receive an entire framed message."""
        # Get the expected length of the message
        msg_len = int.from_bytes(
            self._sock.recv(self._frame_bytes),
            byteorder="big")

        # Receive until the expected length is reached
        full_msg = b""
        while len(full_msg) < msg_len:
            recv_msg = self._sock.recv(msg_len - len(full_msg))
            if not recv_msg:
                raise self.EndOfMessageError(
                    f"Expected {msg_len} bytes but only received"
                    f" {len(full_msg)} before the socket closed"
                )
            full_msg += recv_msg

        # Decode and return the message
        return full_msg.decode("utf-8")

    def send_msg(self, msg: str):
        """Frame and send a message."""
        # Encode the message
        encoded_msg = msg.encode(self._encoding)

        # Frame the message
        msg_len = len(encoded_msg).to_bytes(4, byteorder="big")
        framed_msg = msg_len + encoded_msg

        # Send the message
        self._sock.sendall(framed_msg)

    def connect(self, addr: tuple[str, int]) -> None:
        self._sock.connect(addr)

    def close(self) -> None:
        """Close the socket."""
        # Necessary to close the socket while it's blocked and accepting
        try:
            self._sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

        self._sock.close()
