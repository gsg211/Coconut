# SocketManager (UDP packet transmission abstraction)

## Overview
The `SocketManager` class is a thread-safe, non-blocking network interface wrapper designed to handle UDP communication. It employs the **Reactor Pattern** using Python's `selectors` module to efficiently manage Input/Output operations without blocking the main application execution.

## Architecture

The manager runs a dedicated background thread (the **Worker/Reactor**) that monitors file descriptors for events. It communicates with the main application thread via thread-safe queues.

### Key Components

1.  **Non-Blocking UDP Socket:**
    *   The underlying socket is set to `setblocking(False)`.
    *   It binds to a local address/port and sends to a specific peer address/port.

2.  **I/O Selector (`selectors.DefaultSelector`):**
    *   Monitors the socket for `EVENT_READ` (incoming data) and `EVENT_WRITE` (readiness to send data).
    *   Monitors a "Self-Pipe" for internal signaling.

3.  **Thread-Safe Queues:**
    *   **`send_queue`**: The application pushes data here. The Worker pulls from here to send over the network.
    *   **`receive_queue`**: The Worker pushes received network data here. The application pulls from here to process packets.

4.  **The Self-Pipe (`os.pipe`):**
    *   Used to wake up the `select()` call in the Worker thread immediately when the main thread adds data to the send queue or signals a stop. This ensures data is sent as soon as possible without waiting for a read-timeout.

## Data Flow

### 1. Sending Data
1.  **Application** calls `q_snd_put(data)`.
2.  Data is added to the `send_queue`.
3.  A byte is written to the **pipe** (`__pipe_fd_wr`).
4.  The **Worker Thread**, currently blocked on `selector.select()`, wakes up because the pipe (`__pipe_fd_rd`) became readable.
5.  The Worker detects the queue is not empty and modifies the socket registration to listen for `EVENT_WRITE`.
6.  When the socket is ready, the Worker pulls data from the queue and calls `sendto`.

### 2. Receiving Data
1.  The **Worker Thread**'s selector detects `EVENT_READ` on the UDP socket.
2.  The Worker calls `recvfrom` to get the raw bytes.
3.  The data is pushed into `__receive_queue`.
4.  **Application** calls `q_rcv_get()` (non-blocking) to retrieve the data.
