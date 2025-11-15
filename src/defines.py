import os
from enum import IntEnum

HEADER_POS             = slice(0,1) # slice is end exclusive, so it's really 0-0
SEQ_NR_POS             = slice(1,5) # 1-4
DATA_LEN_POS           = slice(5,7) # 5-6
CHECKSUM_POS           = slice(7,9) # 7-8
PAYLOAD_POS            = slice(9,512) # 9-511

WINDOW_SIZE            = int(3)


class InvalidDataSzException(Exception):
    def __init__(self, field:str):
        super().__init__('Invalid size of data given to: {}'.format(field.upper()))
        

class SocketNotOpenException(Exception):
    def __init__(self, sck:str):
        super.__init__('The socket {} is not properly configured',format(sck))

class UDP_Size(IntEnum):
    PAYLOAD_SZ         = 512
    HEADER_SZ          = 1
    SEQ_NR_SZ          = 4
    DATA_LEN_SZ        = 2
    APP_CHECKSUM_SZ    = 2
    CHECKSUM_CHUNK_SZ  = 2
    MAX_DATA_SZ        = PAYLOAD_SZ - HEADER_SZ - SEQ_NR_SZ - DATA_LEN_SZ - APP_CHECKSUM_SZ

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
        return self.to_bytes(UDP_Size.HEADER_SZ,'big')

class Operation_Header(IntEnum):
    H_OP_ACCESS        = 0b0001_0000 
    H_OP_CREATE        = 0b0010_0000
    H_OP_DELETE        = 0b0011_0000
    H_OP_DOWNLOAD      = 0b0100_0000
    H_OP_UPLOAD        = 0b0101_0000
    H_OP_MOVE          = 0b0110_0000
    H_DATA             = 0b0111_0000
    @property
    def as_bytes(self) -> bytes:
        return self.to_bytes(UDP_Size.HEADER_SZ,'big')
    
    

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) #/src
ROOT_DIR = os.path.dirname(BASE_DIR)                  # /

CLIENT_LOG_PATH     = os.path.join(ROOT_DIR, "src", "client", "config.txt")
SERVER_LOG_PATH = os.path.join(ROOT_DIR, "src", "server", "saved_configs")
UTILS_LOG_PATH         = os.path.join(ROOT_DIR, "logs", "utils_log.log")

class Config_Line(IntEnum):
    ID_LINE           = 0
    WINDOW_LINE       = 1
    
    
LOCAL_HOST_ADDR       = '127.0.0.1'
DEFAULT_PORT_A        = int(8080)
DEFAULT_PORT_B        = int(18080)
MAX_CONNECTIONS       = int(1)

NAME_UNDEFINED        = "UNDEFINED" 
    
    