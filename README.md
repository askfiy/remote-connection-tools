# README

## status code

Request status code:

| code | desc                                                      |
| ---- | --------------------------------------------------------- |
| 100  | Management request to join the link                       |
| 200  | Client request to join link                               |
| 300  | The management side requests to view all clients          |
| 400  | The management side requests to link the client           |
| 500  | The management side tries to send a message to the client |
| 600  | The client tried to send a message to the management      |

Response status code:

The response status codes are all obtained with the request status code +1 or +2.

For example, 101 means success and 102 means failure.

special:
501 indicates that the command was forwarded successfully.
502 means command forwarding failed.
The same is true for the 600 series.

### Package list

Client:

{
    "client ip:port": {
        "conn": conn link object
    },
...
}

Management side:

{
    "Management ip:port": {
        "conn": the management side conn link object
        "client": client conn link object or None
    }
}

The management side sends a message:

{
    "code": 500,
    "data": {
        "manage": "Management ip:port",
        "command": "shll command",
    },
    "error": string
}

Client sends message:

{
    "code": 600,
    "data": {
        "manage": "Management ip:port",
        "result": None or string
    },
    "error": string
}

The management side requests to link the client:

{
    "code": 400,
    "data": {
        "client": "client ip:port",
    },
    "error": "",
}
