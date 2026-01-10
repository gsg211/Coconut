### Description 

This project implements the Sliding Window Protocol with selective repeat on negative acknowledgements over UDP, which uses a "window" to manage packet flow. This mechanism allows multiple packets to be in transit simultaneously while waiting for them to be acknowledged, then the window "slides" to the last packet that has not received an acknowledgement. Selective Repeat only retransmits the packets that have received a NAK (negative acknowledgement) which means that they were lost.


### Client General Flow

[CLIENT_FLOW](./Documentation/CLIENT/CLIENT.md)
<br>
<br>

### Server General Flow

[SERVER_FLOW](./Documentation/SERVER/SERVER.md)
<br>
<br>

#### Simulated Packet Loss

In order to simulate real world UDP packet loss caused by environmental causes, the client can opt in to set up a `Packet Loss Probability`.

If the setting is enabled in the application, then the client can select a probability in the range [0-100]% for the packages to be lost.

For example, if the selected probability is `0.5` in the client configuration, then the number `0.5` will be saved in the client's configuration.

- When the client sends a packet, it has a `50%` chance to mark the packet as sent, but not really transmit it.
- When the server receives a packet, it has a `50%` chance to ignore it, sending a `NAK` instead of an `ACK`

#### Operations Flow

[OPERATIONS](./Documentation/OPERATIONS/OPERATIONS.md)