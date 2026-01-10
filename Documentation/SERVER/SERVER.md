# Remote File System Server

It operates on an infinite loop, listening for incoming requests from the Client, executing file system operations, and returning status updates or data.

## High-Level Architecture

The Server is designed as a passive, state-machine-based system:

1.  **Network Listener (`Server` Main Loop)**:
    *   The entry point `startOp_listen` continuously monitors the network port using the `DataTransferManager`.
    *   It inspects incoming packet headers to determine which operation to execute.

2.  **Operation Handlers (`endOp_` methods)**:
    *   Each operation (for example `endOp_download_file`, `endOp_create_file`) is encapsulated in its own method.
    *   These handlers constitute the logic: they wait for specific arguments (like filenames), interact with the disk, and formulate the response.

3.  **Storage & Protocol Layer**:
    *   **StorageManager**: Abstracts the physical file system (writing files, traversing trees, deleting).
    *   **DataTransferManager**: Handles the reliability of the connection, ensuring packets sent by the client are reassembled correctly before the Server logic sees them.


### Supported Operations
[SUPPORTED_OPERATIONS](../OPERATIONS/OPERATIONS.md)

## Server Flow

1.  **Idle State**: The server runs an infinite `while True` loop in `startOp_listen`, blocking until a valid packet arrives.
2.  **Header Detection**: Upon receiving a packet, it reads the **Operation Header** (e.g., `H_OP_ACCESS`, `H_OP_UPLOAD`).
3.  **Dispatch**: The server breaks out of the listening loop and calls the specific handler method associated with that header.
4.  **Payload Reception (Synchronous)**:
    *   Inside the handler, if the operation requires arguments (e.g., a file path for deletion), the server calls `listen()` again to wait specifically for those data packets.
5.  **Execution**: The server performs the requested action on the local file system.
6.  **Response**:
    *   The server prepares a response packet containing `H_OP_SUCCESS` or `H_OP_FAILED`.
    *   If data was requested (e.g., file download), the data is packetized and queued before the success header.
7.  **Reset**: The handler finishes, and the server returns to the **Idle State** to await the next command.
