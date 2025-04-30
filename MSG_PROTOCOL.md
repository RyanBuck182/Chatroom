# Message Protocol

The client and server exchange messages using a custom protocol. This file provides documentation of this protocol.

## Requirements

Messages must be sent as JSON over TCP. They should be encoded with UTF-8 and prefixed with the message length as a 4 byte unsigned big-endian integer. 

## Message Types

Each message type requires different fields. At the least, they all require `type` and `sender`.

### START

A start message is sent to the server when a client connects to the server. The server will forward this message to all connected clients.

**Required Fields**
  - `type`
    - a string indicating the type of message that's being sent
  - `sender`
    - the username of the message sender

**Example**

```json
{
  "type": "START",
  "sender": "username"
}
```

### EXIT

An exit message is sent to the server when a client disconnects from the server. The server will forward this message to all connected clients.

**Required Fields**
  - `type`
    - a string indicating the type of message that's being sent
  - `sender`
    - the username of the message sender

**Example**

```json
{
  "type": "EXIT",
  "sender": "username"
}
```

### BROADCAST

A broadcast message is sent to the server when a client wants to send a message to all other clients. The server will forward this message to all connected clients.

**Required Fields**
  - `type`
    - a string indicating the type of message that's being sent
  - `sender`
    - the username of the message sender
  - `message`
    - the message the client is sending

**Example**

```json
{
  "type": "BROADCAST",
  "sender": "username",
  "message": "This is my message.\n1 2 3 4 5."
}
```

### PRIVATE

A private message is sent to the server when a client wants to send a message to one specific client. The server will forward this message to the specified client.

**Required Fields**
  - `type`
    - a string indicating the type of message that's being sent
  - `sender`
    - the username of the message sender
  - `recipient`
    - the username of the message recipient
  - `message`
    - the message the client is sending

**Example**

```json
{
  "type": "PRIVATE",
  "sender": "username1",
  "recipient": "username2",
  "message": "This is my message.\n1 2 3 4 5."
}
```
