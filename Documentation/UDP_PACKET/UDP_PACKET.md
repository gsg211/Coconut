## Proprietary UDP based packets

![RC_P_UDP_STRUCTURE](./RCP_UDP_FORMAT.drawio.svg)


#### UDP Protocol fields
The fields marked as UDP protocol are based on the protocol defined in `RFC-768: User Datagram Protocol` https://www.ietf.org/rfc/rfc768.txt

#### Custom fields
These fields take up space from the payload portion of the classic UDP datagram.
All packets used in this project will have all the custom fields defined in the same positions.

#### Custom Header
1 byte - enough to store 255 numbered headers

Implemented custom headers together with their associated numbers:


**Flow headers**

| HEADER NAME        | VALUE | VALUE IN HEX    |
| ------------------ | ----- | --------------- |
| H_DONE             | 1     |      0x01       |
| H_CANCEL           | 2     |      0x02       |
| H_SYN              | 3     |      0x03       |
| H_SYN_CHANGECONFIG | 4     |      0x04       |
| H_ACK              | 5     |      0x05       |
| H_NAK              | 6     |      0x06       |
| H_VALID            | 7     |      0x07       |
| H_OP_FAILED        | 8     |      0x08       |
| H_OP_SUCCESS       | 9     |      0x09       |
| H_CONFIG           | 10    |      0x0a       |
| H_FIN              | 11    |      0x0b       |


**Operation Headers**

| HEADER NAME   | VALUE | VALUE IN HEX    |
| ------------- | ----- | --------------- |
| H_OP_ACCESS   | 16    | 0x10            |
| H_OP_CREATE   | 32    | 0x20            |
| H_OP_DELETE   | 48    | 0x30            |
| H_OP_DOWNLOAD | 64    | 0x40            |
| H_OP_UPLOAD   | 80    | 0x50            |
| H_OP_MOVE     | 96    | 0x60            |
| H_DATA        | 112   | 0x70            |
| H_OP_CONFIG   | 128   | 0x80            |


#### Sequence Number
3 bytes - enough to store numbers in [0,2^(3*8)-1]

- Packets are tagged with their corresponding sequence number

#### Data Length

2 bytes - enough to store numbers in [0,2^16-1]

The standard maximum packet data size used in this project will be 512bytes.

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
  - If the result is 16'h00, then the data is correct

<br>
<br>
<br>