# http_server_python

This project is a TEN extension that implements a simple HTTP server, enabling interaction with the running TEN graph from external systems.

## Features

- **Command Execution**: Seamlessly pass any `cmd` to the running TEN graph and receive the results.
- **Asynchronous Handling**: Utilizes `asyncio` and `aiohttp` for efficient, non-blocking request processing.
- **Configurable Server**: Easily configure the server's listening address and port through the TEN environment.


## API

### Property

Refer to api definition in [manifest.json](manifest.json) and default values in [property.json](property.json).

| Property |	Type |	Description |
| - | - | - |
| `listen_addr`| `string`| address to listen on |
| `listen_port` | `int32` | port to listen on|	

## HTTP API

### POST `/cmd/{cmd_name}`

- **Description**: Sends a command with the specified name on the TEN graph.    
- **Request Body**: JSON object containing the command properties.    
- **Response**: JSON object with the command execution result.    

#### Example Request

```bash
curl -X POST http://127.0.0.1:8888/cmd/example_cmd_name \
-H "Content-Type: application/json" \
-d '{
    "num_property1": 1,
    "str_property2": "Hello"
}'
```

## Development

### Standalone testing

<!-- how to do unit test for the extension -->

```bash
task install
task test
```

