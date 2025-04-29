"""Defines a Terminal class to assist with terminal interaction."""

from enum import Enum
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

    def __init__(self, max_line_len: int = MAX_LINE_LENGTH) -> None:
        """Initialize an interface for the terminal."""
        self._max_line_len = max_line_len

    def print_inlines(self, msg: str, color: TerminalColor = None) -> None:
        """Print a message without a terminating newline."""
        # Apply color
        if color:
            msg = self.wrap_color(msg, color)

        # Split message between lines if too long
        msg = self._split_msg(msg)

        # Print the message without a newline at the end
        print(msg, end="")

    def print_lines(self, msg: str, color: TerminalColor = None) -> None:
        """Print a message with a terminating newline."""
        self.print_inlines(msg, color)
        print()

    def replace_current_line(
            self, msg: str, color: TerminalColor = None
    ) -> None:
        """Print over the current line, replacing it.

        Does not print a terminating newline."""
        self.clear_line()
        self.print_inlines(msg, color)

    def replace_previous_line(
            self, msg: str, color: TerminalColor = None
    ) -> None:
        """Print over the previous line, replacing it.

        Does not print a terminating newline."""
        self.cursor_up()
        self.replace_current_line(msg, color)

    def wait_for_enter(self, prompt: str = "") -> None:
        """Wait for the user to press enter."""
        input(prompt)
        return

    def wait_for_input(self, prompt: str = "") -> str:
        """Wait for and return input."""
        return input(prompt)

    def wrap_color(self, msg: str, color: TerminalColor) -> str:
        """Wrap a string in ANSI color codes."""
        return f"{color}{msg}{TerminalColor.Reset}"

    def clear_line(self) -> None:
        """Clear the current line."""
        print(f"\r{' '*self._max_line_len}\r", end="")

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

        # Split the message into multiple lines
        lines = []
        while len(msg) > self._max_line_len:
            line = msg[:self._max_line_len+1]
            msg = msg[self._max_line_len+1:]
            lines.append(line)

        # Return the msg split into different lines
        return "\n".join(lines)
