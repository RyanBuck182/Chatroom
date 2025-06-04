"""Start a chat server."""

from server.chat_server import ChatServer


def main():
    """Start a chat server."""
    server = ChatServer()
    server.start()


if __name__ == "__main__":
    main()
