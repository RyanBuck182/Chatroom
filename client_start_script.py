"""Start a chat client."""

from client.chat_terminal import ChatTerminal


def main():
    """Start a chat client."""
    terminal = ChatTerminal()
    terminal.start()


if __name__ == "__main__":
    main()
