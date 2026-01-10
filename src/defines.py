import os
from enum import IntEnum

HEADER_POS             = slice(0,1) # slice is end exclusive, so it's really 0-0
SEQ_NR_POS             = slice(1,4) # 1-3
DATA_LEN_POS           = slice(4,6) # 4-5
CHECKSUM_POS           = slice(6,8) # 6-7
PAYLOAD_POS            = slice(8,512) # 8-511

class InvalidDataSzException(Exception):
    def __init__(self, field:str):
        super().__init__('Invalid size of data given to: {}'.format(field.upper()))
        

class SocketNotOpenException(Exception):
    def __init__(self, sck:str):
        super.__init__('The socket {} is not properly configured',format(sck))

class UDP_Size(IntEnum):
    PAYLOAD_SZ         = 512
    HEADER_SZ          = 1
    SEQ_NR_SZ          = 3
    DATA_LEN_SZ        = 2
    APP_CHECKSUM_SZ    = 2
    CHECKSUM_CHUNK_SZ  = 2
    MAX_DATA_SZ        = PAYLOAD_SZ - HEADER_SZ - SEQ_NR_SZ - DATA_LEN_SZ - APP_CHECKSUM_SZ

class Flow_Header(IntEnum):
    H_DONE             = 0x01
    H_CANCEL           = 0x02
    H_SYN              = 0x03
    H_SYN_CHANGECONFIG = 0x04
    H_ACK              = 0x05
    H_NAK              = 0x06
    H_VALID            = 0x07
    H_OP_FAILED        = 0x08
    H_OP_SUCCESS       = 0x09
    H_CONFIG           = 0x0a
    H_FIN              = 0x0b
    
    @property
    def as_bytes(self) -> bytes:
        return self.to_bytes(UDP_Size.HEADER_SZ,'big')

class Operation_Header(IntEnum):
    H_OP_ACCESS        = 0x10
    H_OP_CREATE        = 0x20
    H_OP_DELETE        = 0x30
    H_OP_DOWNLOAD      = 0x40
    H_OP_UPLOAD        = 0x50
    H_OP_MOVE          = 0x60
    H_DATA             = 0x70
    H_OP_CONFIG        = 0x80
    @property
    def as_bytes(self) -> bytes:
        return self.to_bytes(UDP_Size.HEADER_SZ,'big')
    
    

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) #/src
ROOT_DIR = os.path.dirname(BASE_DIR)                  # /


CLIENT_ROOT_PATH = os.path.join(ROOT_DIR, "ClientStorage")
SERVER_ROOT_PATH = os.path.join(ROOT_DIR, "ServerStorage")
class Config_Line(IntEnum):
    ID_LINE           = 0
    WINDOW_LINE       = 1
    
    
LOCAL_HOST_ADDR_A       = '127.0.0.1'
LOCAL_HOST_ADDR_B       = '127.0.0.2'
DEFAULT_PORT_A        = int(8080)
DEFAULT_PORT_B        = int(18080)
MAX_CONNECTIONS       = int(1)

NAME_UNDEFINED        = "UNDEFINED" 
    
    