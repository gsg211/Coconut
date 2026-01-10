# Sliding Window Protocol (Selective Repeat with NAK)

## Overview
Here is presented the data transfer protocol over UDP used. **Sliding Window** mechanism with **Selective Repeat** and **Negative Acknowledgements (NAK)**. It is designed to handle packet loss, packet corruption (via checksums), and out-of-order delivery.

## Key Features
1.  **Selective Repeat:** Only missing packets are retransmitted, rather than the entire window.
2.  **NAK (Negative Acknowledgement):** The receiver explicitly requests retransmission of missing packets immediately upon detecting a gap in the sequence, reducing wait times compared to timeouts alone.
3.  **Simulated Packet Loss:** Both sender and receiver can simulate network instability.
4.  **Checksum Verification:** Packets with corrupted data are detected and dropped.

## Packet Types used
[PACKET_TYPES](../UDP_PACKET/UDP_PACKET.md)

## Detailed Protocol Flow

### 1. Sender Logic (`SendingWindow`)
The sender maintains a **window** of size N (configured via window_size).

**Variables:**
*   `Base`: The sequence number of the oldest unacknowledged packet.
*   `NextSeqNum`: The sequence number of the next packet to be sent.

**The Loop:**
1.  **Sending Phase:**
    *   If `NextSeqNum < Base + WindowSize`, the sender transmits the packet at `NextSeqNum` and starts a timer for it.
    *   It checks `will_lose()` to simulate random packet loss during transmission.
2.  **Listening Phase (ACK/NAK):**
    *   **Receive ACK:** Marks packet as acknowledged. If the packet sequence number == base, the window slides forward (`Base` increments) until it hits an unacknowledged packet.
    *   **Receive NAK:** Immediately retransmits packet (Fast Retransmit) and resets its timer.
3.  **Timeout Phase:**
    *   The sender iterates through the current window. If any unacknowledged packet has exceeded the `time_out_interval`, it is retransmitted.
4.  **Termination:**
    *   Once all data packets are ACKed, the sender transmits `H_DONE` to signal completion.

### 2. Receiver Logic (`ReceivingWindow`)
The receiver maintains an `expected_number` (initially 1) and a `buffer` for out-of-order packets.

**The Loop:**
1.  **Receive Packet:**
    *   Calculates checksum. If invalid, the packet is dropped silently.
2.  **Check Sequence Number:**
    *   **Case A: In-Order SeqNr == Expected:**
        1.  Append data to the list.
        2.  Send `ACK`.
        3.  Increment `Expected`.
        4.  **Clear Buffer:** Check if `Expected` is already in the `buffer`. If yes, process it, ACK it, and increment `Expected` again. Repeat until a gap is found.
    *   **Case B: Out-of-Order / Gap Detected:**
        1.  Store packet in the `buffer`.
        2.  **Send `NAK`:** This tells the sender, "I received a future packet, but I am still waiting for packet Expected. Please resend it now."
    *   **Case C: Duplicate/Old:**
        1.  Send `ACK` again (to ensure the sender knows it was received, in case the previous ACK was lost).
3.  **Termination:**
    *   If `H_DONE` is received, the receiver notes the final sequence number.
    *   The loop exits only when `Expected` passes the final sequence number (ensuring all buffered packets are processed).

## Configuration

You can adjust the behavior of the protocol:

*   **`window_size`**: How many packets can be "in flight" at once.
*   **`packet_data_size`**: Max characters per UDP packet.
*   **`time_out_interval`**: How long the sender waits before retransmitting un-ACKed packets.
*   **`packet_loss_chance`**: Float (0.0 to 1.0) representing the probability of dropping a packet to simulate bad network conditions.
