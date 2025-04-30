"""Define ChatTerminal, a textual interface for a ChatClient.

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

from client.chat_client import ChatClient
from client.terminal import Terminal, TerminalColor


class ChatTerminal:
    """UI for the chatroom."""

    def __init__(self):
        """Initialize the ChatTerminal."""
        # Interface for interacting with the terminal
        self.terminal = Terminal(self.exit)

        # Ask the user for their username
        username = self._ask_username()

        # Initialize chat client and listen for messages
        self.client = ChatClient(username)
        self.client.on_receive_message(self._receive_message)

        # Python doesn't support complex terminal manipulation on
        # Windows (at least not easily). Therefore, when the user is writing a
        # message, received messages must wait in a message queue before
        # they're displayed to the user.
        self.msg_queue = []

        # Keeps track of when input is active so messages can be queued
        self._should_queue_messages = False

    def start(self) -> None:
        """Start the chat terminal."""
        # Connect to the chatroom
        self.client.start()

        # Display an intro for the user
        self._intro()

        # Repeatedly waits for user to send msg until they exit
        self._send_msg_forever()

    def exit(self) -> None:
        """Exit the chat room."""
        self.client.exit()
        exit_msg = self._format_exit_message(self.client.username)
        self.terminal.clear_line()
        self.terminal.print_line(exit_msg)
        exit()

    def _intro(self) -> None:
        """Print the intro text."""
        self.terminal.print_line(
            "You have entered the chatroom!\n"
            "Press enter at any time to begin inputting a message.\n"
            "Preface a message with @example to send a private message to the"
            " user with the username 'example'.\n"
            "Private messages to you are indicated with the separator '->' and"
            " the color purple.\n"
            "Send !exit to leave the chatroom.\n"
        )

    def _send_msg_forever(self) -> None:
        """Send messages from the user to the server forever."""
        sending = True
        while sending:
            # Wait till the user presses enter
            self.terminal.wait_for_enter()
            self.terminal.clear_previous_line()

            # Prompt for message
            msg = self._prompt_for_msg()

            # Print messages in queue
            self._print_msg_queue()

            # Parse message
            sending = self._parse_user_msg(msg)

    def _prompt_for_msg(self) -> str:
        """Gets a message from the user."""
        self._enable_message_queue()
        msg = self.terminal.wait_for_input("> ")
        self._disable_message_queue()

        # Clear the user's message to make room
        self.terminal.clear_previous_line()
        return msg

    def _print_msg_queue(self) -> None:
        """Print the message queue"""
        # self.terminal.clear_line()

        # Print the queued messages
        for msg in self.msg_queue:
            self.terminal.print_line(msg)

        # Clear the queued messages
        self.msg_queue.clear()

    def _parse_user_msg(self, msg: str) -> bool:
        """Parse user msg, handle it, and return whether to continue sending.

        If the message is invalid, display an error message.
        """
        msg = msg.strip()

        # Print error msg if input msg is empty or whitespace
        if not msg:
            self._print_error("ERROR: You must specify a message to send.")
            return True

        # Exit the chatroom
        if msg == "!exit":
            self.exit()
            return False

        # Validate & parse private message
        if msg[0] == "@":
            self._parse_user_private_msg(msg)
            return True

        # Broadcast message
        # Needs no further parsing or validation
        self.client.send_broadcast(msg)
        return True

    def _parse_user_private_msg(self, msg: str) -> None:
        """Parse user private message and handle it.

        If the message is invalid, display error message."""
        # No recipient or message is specified
        if len(msg) == 1:
            self._print_error("ERROR: You must specify a message to send.")
            return

        # Get the end of the username of the recipient
        try:
            recipient_end_index = msg.index(' ')
        # No message to send
        except ValueError:
            self._print_error(
                "ERROR: You must specify the message to send to the"
                " recipient. This means '@recipient' must be followed by"
                " the message you wish to send to the user. For example,"
                " '@Alice this is a private message to Alice'."
            )
            return

        # Get the username of the recipient
        recipient = msg[1:recipient_end_index]

        # No recipient is specified
        if not recipient:
            self._print_error(
                "ERROR: You must specify the recipient in a private"
                " message. This means @ must be followed by the name of"
                " the user you wish to message. For example, '@Alice this"
                " is a private message to Alice'."
            )
            return

        # Remove the username from the message to send
        send_msg = msg[recipient_end_index + 1:]

        self.client.send_private(send_msg, recipient)
        private_msg = self._format_private_message(send_msg, recipient)
        self.terminal.clear_line()
        self.terminal.print_line(private_msg)

    def _receive_message(self, raw_response: str) -> None:
        """Print or queue a received message."""
        msg = self._parse_received_message(raw_response)

        # Queue message if enabled
        if self._should_queue_messages:
            self.msg_queue.append(msg)
        # Print message
        else:
            self.terminal.print_line(msg)

    def _parse_received_message(self, raw_response: str) -> str:
        """Parse and format a message for display."""
        response = json.loads(raw_response)
        sender = response["sender"]

        match response["type"].upper():
            case "START":
                return self._format_start_message(sender)
            case "EXIT":
                return self._format_exit_message(sender)
            case "BROADCAST":
                msg = response["message"]
                return self._format_broadcast_message(sender, msg)
            case "PRIVATE":
                msg = response["message"]
                return self._format_private_message(sender, msg)

    def _format_start_message(self, sender: str) -> str:
        """Format a start message."""
        return self.terminal.wrap_color(
            f"{sender} joined the chat.", TerminalColor.Yellow
        )

    def _format_exit_message(self, sender: str) -> str:
        """Format an exit message."""
        return self.terminal.wrap_color(
            f"{sender} left the chat.", TerminalColor.Yellow
        )

    def _format_broadcast_message(self, sender: str, msg: str) -> str:
        """Format a broadcast message."""
        return f"{sender} >> {msg}"

    def _format_private_message(self, sender: str, msg: str) -> str:
        """Format a private message."""
        return self.terminal.wrap_color(
            f"{sender} -> {msg}", TerminalColor.Purple
        )

    def _ask_username(self) -> str:
        """Asks for a username from the user and returns it."""
        username = ""
        valid_username = False
        while not valid_username:
            valid_username = True

            # Get username
            username = self.terminal.wait_for_input(
                "Please enter a username: "
            )

            # Empty username
            if not username:
                self.terminal.print_line("You must enter a username!\n")
                valid_username = False
            # Username not alphanumeric
            elif not username.isalnum():
                self.terminal.print_line("Username must be alphanumeric!\n")
                valid_username = False

        self.terminal.print_line("")
        return username

    def _enable_message_queue(self) -> None:
        """Enable message queuing."""
        self._should_queue_messages = True

    def _disable_message_queue(self) -> None:
        """Disable message queuing."""
        self._should_queue_messages = False

    def _print_error(self, msg: str) -> None:
        """Print message in a red color."""
        self.terminal.print_line(msg, TerminalColor.Red)
