### Description 

This project implements the Sliding Window Protocol with selective repeat on negative acknowledgements over UDP, which uses a "window" to manage packet flow. This mechanism allows multiple packets to be in transit simultaneously while waiting for them to be acknowledged, then the window "slides" to the last packet that has not received an acknowledgement. Selective Repeat  only retransmits the packets that have received a NAK (negative acknowledgement) which means that they were lost.


### Client General Flow

![RC_P_CLIENT_FLOW](images/diagrams_flow_config/RCP_CL_flow.drawio.svg)

The client behavior is based on the state machine presented in the diagram.

#### IDLE
Waiting for user input. From the application the user can set up configuration settings:

- window size
- packet data size
- timeout duration
- timeout threshold
- client name (the id is tied to the name)
  
#### Configuration Process
This state is explained in greater detail in the Client Side Session Startup section.
If the configuration is successful, the client waits for further input from the user.

#### Waiting Input
The user can select an operation from the application.

The operation request is sent to the server in a sequence of packets marked with the corresponding H_OP_ header. After the operation sequence is sent, a packet with the H_DONE header is also sent, to signal the server it can start processing the request.

#### Receiving Response

The response can either be VALID or INVALID.
- VALID: the request was correctly processed, now the client can start receiving the response packets.
- INVALID: the request failed. An error message is displayed and the client can attempt again.
  
#### Response Processing

After receiving all the response data, the client processes the response. If the received data is not valid, then an error message is displayed.


<br>
<br>

### Server General Flow

![RC_P_SERVER_FLOW](images/diagrams_flow_config/RCP_SV_flow.drawio.svg)

The server behavior is based on the state machine presented in the diagram.

#### IDLE
The server is listening for new connections. When a "Config request received" event occurs, it moves to handle the session setup.

#### Configuration Process
This state is explained in greater detail in the Server Side Session Setup section. If the configuration is successful ("Config done"), the server is ready to handle client requests. If it fails, the session is aborted and the server returns to `IDLE`.

#### Waiting for operation
The server has an established connection and waits for the client to send a request. When the "first packet of operation" is received, it begins receiving the full request.

#### Receiving Operation
The server receives all packets that make up the client's operation request. When the final `H_DONE` packet is received, it signals that the full request is ready for processing.

#### Processing request
The server executes the operation requested by the client. Once processing is done, it determines if the request was successful.

#### Sending Response
The outcome of the processing determines the response.
- VALID -  If processing was successful, the server sends the response data, followed by a final `H_DONE` packet. It then returns to the `Waiting for operation` state.
- INVALID - If processing failed, the server sends an `H_INVALID` packet. It then returns to the `Waiting for operation` state to await a new command.

<br>
<br>

### Client-side Session Setup

![RC_P_CLIENT_CONFIG](images/diagrams_flow_config/RCP_CL_Config.drawio.svg)

#### There are four main stages

- Initialization
- Server Response
- Configuration Exchange (optional)
- Finalization
  
#### Initialization
The client starts in the `IDLE` state. The connection initialization is started from the application.<br>

The initialization is started by either a regular request, or a request marked as "change config". This is done through the use of the `H_SYN_CHANGE_CONFIG` header.<br>

#### Server Response
Now the client waits for an amount of time for a response from the server. There are multiple possibilities: 

- Nothing is received - after a while, the client re-sends the request.
- `SYN/ACK` is received - this means that the server acknowledges the client, because it has found a valid configuration. In exchange, the server sends a `SYN`chronize request containing its `SEQ`uence number.

#### Configuration Exchange
- `NAK` is received - the server either has no valid config for the requesting client ID, or the received initial request was marked "CHANGE_CONFIG". The client now has to send config information to the server. 

#### Finalization
The client sends a final `ACK`nowledgement to the server, saying the connection should be established.

From the client perspective, if the connection is established, but a server `SYN` is received again, it means that the final `ACK` was lost, and is sent again.

<br>
<br>

### Server-side Session Setup

![RC_P_SERVER_CONFIG](images/diagrams_flow_config/RCP_SV_Config.drawio.svg)

This process is designed to handle two types of clients

- Registered clients - they are correctly identified by the server using the corresponding client ID, and the connection request is not marked as "CHANGE_CONFIG"
- Unregistered clients - the server requests a client profile configuration

#### There are four main stages
- Listening
- Validation
- Configuration handling
- Final handshake
  
#### Listening
The server passively waits on a port for a connection request.

#### Client validation
After receiving a connection request, the server enters the SYN_RECEIVED state. Now it checks whether the request is marked as `CHANGE_CONFIG` or not.

#### Configuration Handling
- `CHANGE_CONFIG` - the server will send a NAK to the client, this meaning that it has requested a configuration.
- normal request - the server will check if it has a valid config for the corresponding client id. If yes, then an `ACK` is sent, together with the `SYN` request on its `SEQ` nr. If not, then a `NAK`is sent, requesting the config.
  
#### Final Handshake
If the final client-side `ACK` is received, then the connection is established. If not, then the server `SYN` is sent a few more times (max_retransmits times).


<br>
<br>

### Active Closer Process

![RC_P_PASSIVE_CLOSER](images/diagrams_flow_config/RCP_ACTIVE_CLOSER.drawio.svg)

The closing process is bi-directional. This means either the client or the server can initialize it.

The shut-down process is initialized by sending a `FIN` packet.

#### FIN_WAIT1
After sending the `FIN` packet, the sender waits for a response from the other party.

#### FIN_WAIT2
The active closer has received an `ACK` for the shutdown request.

Now the active closer has to wait for the other party to send its own `FIN` request. If there is no FIN received, then the connection is shut down by force.

After the `FIN` is received, the active closer sends a `FINAL_ACK` to acknowledge it.

#### TIME_WAIT
After sending the `FINAL_ACK`, the sender enters the `TIME_WAIT` state. Here it waits for a period of time, to ensure correct shutdown. The `TIME_WAIT` timer trigger duration is calculated from:
- 2*`MSL`
- MSL = Maximum Segment Lifetime (default = 30sec)

If while in this state another `FIN` packet is received, then another `FINAL_ACK` will be sent and the `TIME_WAIT` timer will be reset.

#### CLOSED
After the `TIME_WAIT` timer elapses, the active closer enters the final, CLOSED state.



<br>
<br>

### Passive Closer Process

![RC_P_PASSIVE_CLOSER](images/diagrams_flow_config/RCP_PASSIVE_CLOSER.drawio.svg)

The process begins when a FIN packet is received from the active closer, signaling a request to shut down.

#### Sending FIN_ACK
The passive closer's first action is to send an acknowledgement for the closing request.

#### CLOSE_WAIT

The passive closer waits here, in order to wait for all the running processes to be peacefully shut down. 

#### FIN

Once the application is shut down, the passive closer sends it's own `FIN` package.

#### LAST_ACK

After sending the `FIN`, the passive closer enters the `LAST_ACK` state. Here it waits to receive the final ACK from the closer.

- If `LAST_ACK` is received - handshake complete
- If timeout occurs - resends `FIN`
- If max number of retransmits is exceeded - force close\
  
<br>
<br>
<br>
<br>

## Proprietary UDP based packets

![RC_P_UDP_STRUCTURE](images/UDP/RCP_UDP_FORMAT.drawio.svg)


#### UDP Protocol fields
The fields marked as UDP protocol are based on the protocol defined in `RFC-768: User Datagram Protocol` https://www.ietf.org/rfc/rfc768.txt

#### Custom fields
These fields take up space from the payload portion of the classic UDP datagram.
All packets used in this project will have all the custom fields defined in the same positions.

#### Custom Header
1 byte - enough to store 255 numbered headers

Implemented custom headers together with their associated numbers:


**Flow headers**

| HEADER NAME        | VALUE | VALUE IN BINARY |
| ------------------ | ----- | --------------- |
| H_DONE             | 1     | 0b0000_0001     |
| H_CANCEL           | 2     | 0b0000_0010     |
| H_SYN              | 3     | 0b0000_0011     |
| H_SYN_CHANGECONFIG | 4     | 0b0000_0100     |
| H_ACK              | 5     | 0b0000_0101     |
| H_NAK              | 6     | 0b0000_0110     |
| H_VALID            | 7     | 0b0000_0111     |
| H_OP_FAILED        | 8     | 0b0000_1000     |
| H_OP_SUCCESS       | 9     | 0b0000_1001     |
| H_CONFIG           | 10    | 0b0000_1010     |
| H_FIN              | 11    | 0b0000_1011     |


**Operation Headers**

| HEADER NAME   | VALUE | VALUE IN BINARY |
| ------------- | ----- | --------------- |
| H_OP_ACCESS   | 16    | 0b0001_0000     |
| H_OP_CREATE   | 32    | 0b0010_0000     |
| H_OP_DELETE   | 48    | 0b0011_0000     |
| H_OP_DOWNLOAD | 64    | 0b0100_0000     |
| H_OP_UPLOAD   | 80    | 0b0101_0000     |
| H_OP_MOVE     | 96    | 0b0110_0000     |


#### Sequence Number
4 bytes - enough to store numbers in [0,2^32-1]

- Server/Client personal sequence numbers are generated randomly in the range [0,2^16-1]
- Each packet sent has it's own sequence number
  - When initializing a Session, the client will send it's own SEQnr in the SYN packet.
  - The server acknowledges it, sending back an ACK packet with `SEQnr = ( Received SEQ from client + 1 )`
  - The server also sends a SYN packet with the server sequence number
  - The client responds to this with an acknowledgement containing `SEQnr = ( Received SEQ from server + 1 )`

#### Data Length

2 bytes - enough to store numbers in [0,2^16-1]

The standard maximum packet data size used in this project will be 512bytes, but this setting can be altered by the client, in the configuration application.

It tells the application exactly how many bytes of data to use. The UDP header Data Length field shows the entire datagram length size, which is not useful for knowing how much data is really transfered.

#### Application Checksum

The UDP protocol checksum may be disabled or only cover transport-level errors. Thus an application-level checksum is needed to check packet integrity.

**Used Checksum method: Integer Additive 16bit**

- **Sender**
    - Data is split into 16bit words
    - The words are summed together
    - One's complement is applied to the sum
    - This value is sent as the checksum
- **Receiver**
  - Data is split into 16 bit words
  - The words are summed together with the checksum
  - If the result is 16'hFF, then the data is correct

<br>
<br>
<br>

#### Simulated Packet Loss

In order to simulate real world UDP packet loss caused by environmental causes, the client can opt in to set up a `Packet Loss Probability`.

If the setting is enabled in the application, then the client can select a probability in the range [0-100]% for the packages to be lost.

For example, if the selected probability is `n%`, then the number `n/100` will be saved in the client's configuration. This `n%` chance of losing a packet is split between the client and the server.

- When the client sends a packet, it has a `(n/2)%` chance to mark the packet as sent, but not really transmit it.
- When the server receives a packet, it has a `(n/2)%` chance to ignore it, sending a `NAK` instead of an `ACK`

#### Operations Dataflow


![Access_Dataflow](/images/diagrams_flow_data/RCP_access.jpeg)

This operation is for viewing the contents of a directory in a tree-like format.

The client sends the filepath of the folder it wants to access. 

The server generates the tree and sends it to the client.

![Access_Dataflow](/images/diagrams_flow_data/RCP_create_delete.jpeg)

This operation is for creating or deleting a file on the server.

The client sends the filepath of the file including the name. 
The server does the corresponding operation and signals to the client of its 
success.


![Access_Dataflow](/images/diagrams_flow_data/RCP_Move.jpeg)

This operation is similar to the mv command.

The client will send two filepaths separated by a H_DONE packet

The server does the corresponding operation and signals to the client of its success.

![Access_Dataflow](/images/diagrams_flow_data/RCP_Download.jpeg)

The client sends the filepath of the file it wants to download.

The server sends the contents of the file ended by a H_DONE packet. 

![Access_Dataflow](/images/diagrams_flow_data/RCP_Upload.jpeg)

The client sends the filepath of the file it wants to upload.

The server creates the new file and informs the client.

The client starts sending the contents of the file.

The server informs the client that the operations was a success .
