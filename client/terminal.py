"""Defines a Terminal class to assist with terminal interaction."""

from enum import Enum
from typing import Callable

from shared.config import MAX_LINE_LENGTH


class TerminalColor(Enum):
    """ANSI color codes."""
    Black = "\033[30m"
    Red = "\033[31m"
    Green = "\033[32m"
    Yellow = "\033[33m"
    Blue = "\033[34m"
    Purple = "\033[35m"
    Cyan = "\033[36m"
    White = "\033[37m"
    Reset = "\033[0m"


class Terminal:
    """Helpful interface for interaction with the terminal."""

    def __init__(
            self,
            interrupt_handler: Callable[[], None],
            max_line_len: int = MAX_LINE_LENGTH
    ) -> None:
        """Initialize an interface for the terminal."""
        self._interrupt_handler = interrupt_handler
        self._max_line_len = max_line_len

    def print_inline(self, msg: str, color: TerminalColor = None) -> None:
        """Print a message without a terminating newline."""
        # Apply color
        if color:
            msg = self.wrap_color(msg, color)

        # Split message between lines if too long
        msg = self._split_msg(msg)

        # Print the message without a newline at the end
        print(msg, end="")

    def print_line(self, msg: str, color: TerminalColor = None) -> None:
        """Print a message with a terminating newline."""
        self.print_inline(msg, color)
        print()

    def replace_current_line(
            self, msg: str, color: TerminalColor = None
    ) -> None:
        """Print over the current line, replacing it.

        Does not print a terminating newline."""
        self.clear_line()
        self.print_inline(msg, color)

    def replace_previous_line(
            self, msg: str, color: TerminalColor = None
    ) -> None:
        """Print over the previous line, replacing it.

        Does not print a terminating newline."""
        self.cursor_up()
        self.replace_current_line(msg, color)

    def wait_for_enter(self, prompt: str = "") -> None:
        """Wait for the user to press enter."""
        try:
            input(prompt)
        except KeyboardInterrupt:
            self._interrupt_handler()

        return

    def wait_for_input(self, prompt: str = "") -> str:
        """Wait for and return input."""
        try:
            return input(prompt)
        except KeyboardInterrupt:
            self._interrupt_handler()

        return ""

    def wrap_color(self, msg: str, color: TerminalColor) -> str:
        """Wrap a string in ANSI color codes."""
        return f"{color.value}{msg}{TerminalColor.Reset.value}"

    def clear_line(self) -> None:
        """Clear the current line."""
        print(f"\r{' '*self._max_line_len}\r", end="")

    def clear_previous_line(self) -> None:
        """Clear the previous line."""
        print(f"\033[A\r{' ' * self._max_line_len}\r", end="")

    def cursor_up(self) -> None:
        """Move the cursor up one line."""
        print('\033[A', end="")

    def carriage_return(self) -> None:
        """Return the cursor to the start of the current line."""
        print('\r', end="")

    def _split_msg(self, msg: str) -> str:
        """Split a message into multiple lines based on the max line length."""
        # If it's short enough to fit on one line
        if len(msg) <= self._max_line_len:
            return msg

        # If there are multiple lines in the message, handle each separately
        if "\n" in msg:
            lines = msg.split('\n')
            parts = []
            for line in lines:
                split_line = self._split_msg(line)
                parts.append(split_line)
            return "\n".join(parts)

        # Split the message into multiple lines
        lines = []
        while len(msg) > self._max_line_len:
            split_line = msg[:self._max_line_len + 1]
            msg = msg[self._max_line_len + 1:]
            lines.append(split_line)
        lines.append(msg)

        # Return the new split msg
        return "\n".join(lines)
