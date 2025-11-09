from enum import IntEnum


PAYLOAD_SZ             = int(512)
HEADER_SZ              = int(1)
SEQ_NR_SZ              = int(4)
DATA_LEN_SZ            = int(2)
APP_CHECKSUM_SZ        = int(2)
MAX_DATA_SZ            = PAYLOAD_SZ - HEADER_SZ - SEQ_NR_SZ - DATA_LEN_SZ - APP_CHECKSUM_SZ 

class InvalidDataSzException(Exception):
    def __init__(self, field:str):
        super().__init__ ('Invalid size of data given to: {}'.format(field.upper()))


class Flow_Header(IntEnum):
    H_DONE             = 0b0000_0001
    H_CANCEL           = 0b0000_0010
    H_SYN              = 0b0000_0011
    H_SYN_CHANGECONFIG = 0b0000_0100
    H_ACK              = 0b0000_0101
    H_NAK              = 0b0000_0110
    H_VALID            = 0b0000_0111
    H_OP_FAILED        = 0b0000_1000
    H_OP_SUCCESS       = 0b0000_1001
    H_CONFIG           = 0b0000_1010
    H_FIN              = 0b0000_1011
    
    @property
    def as_bytes(self) -> bytes:
        return self.to_bytes(HEADER_SZ,'big')

class Operation_Header(IntEnum):
    H_OP_ACCESS        = 0b0001_0000 
    H_OP_CREATE        = 0b0010_0000
    H_OP_DELETE        = 0b0011_0000
    H_OP_DOWNLOAD      = 0b0100_0000
    H_OP_UPLOAD        = 0b0101_0000
    H_OP_MOVE          = 0b0110_0000
    
    @property
    def as_bytes(self) -> bytes:
        return self.to_bytes(HEADER_SZ,'big')
    

    
    