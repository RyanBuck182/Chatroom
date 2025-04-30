"""Configuration options for the chatroom.

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
# Address/ports
HOST = "localhost"
READ_PORT = 15001
WRITE_PORT = 15002

# Sockets, data framing
FRAME_BYTES = 4
ENCODING = 'UTF-8'

# Terminal
MAX_LINE_LENGTH = 99
