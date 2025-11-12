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

### POST `/cmd`

- **Description**: Sends a command to the TEN graph.
- **Request Body**: JSON object with the following structure:
  - `name` (required): The name of the command to execute
  - `payload` (optional): JSON object containing the command properties
- **Response**: JSON object with the command execution result.
- **Status Codes**:
  - `200`: Command executed successfully
  - `400`: Bad request (invalid JSON or missing `name` field)
  - `502`: Command execution failed
  - `504`: Command execution timeout (5 second timeout)

#### Example Request

```bash
curl -X POST http://127.0.0.1:8888/cmd \
-H "Content-Type: application/json" \
-d '{
    "name": "example_cmd_name",
    "payload": {
        "num_property1": 1,
        "str_property2": "Hello"
    }
}'
```

### POST `/data`

- **Description**: Sends data to the TEN graph (fire-and-forget, no response expected).
- **Request Body**: JSON object with the following structure:
  - `name` (required): The name of the data to send
  - `payload` (optional): JSON object containing the data properties
- **Response**: Empty response with status code.
- **Status Codes**:
  - `200`: Data sent successfully
  - `400`: Bad request (invalid JSON or missing `name` field)

#### Example Request

```bash
curl -X POST http://127.0.0.1:8888/data \
-H "Content-Type: application/json" \
-d '{
    "name": "example_data_name",
    "payload": {
        "num_property1": 1,
        "str_property2": "Hello"
    }
}'
```

## Development

### Standalone testing

<!-- how to do unit test for the extension -->

```bash
task install
task test
```

