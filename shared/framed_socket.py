"""Defines FramedSocket, a length prefixed TCP socket."""

import socket
from typing import Callable, NoReturn

from config import FRAME_BYTES, ENCODING


class FramedSocket:
    """A length prefixed TCP socket."""

    class EndOfMessageError(EOFError):
        """Indicates the message ended before it was expected."""
        pass

    def __init__(
            self,
            addr: tuple[str, int],
            sock: socket.socket = None,
            frame_bytes: int = FRAME_BYTES,
            encoding: str = ENCODING
    ) -> None:
        """Initialize the FramedSocket."""
        self._addr = addr
        self._sock = sock or socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._frame_bytes = frame_bytes
        self._encoding = encoding

        # Connect to the specified address
        self._sock.connect(self._addr)

    def receive_msg_forever(self, handler: Callable[[str], None]) -> NoReturn:
        """Receive messages forever, passing them to a handler."""
        while True:
            msg = self.recv_msg()
            handler(msg)

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

    def close(self) -> None:
        """Close the socket."""
        self._sock.close()
