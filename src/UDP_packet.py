import defines as d

class UDP_Packet():
    __custom_header:bytes
    __seq_nr:bytes
    __data_len:bytes
    __app_checksum:bytes = b'\x00\x00'
    __payload:bytes
    __full_message:bytearray = bytearray(d.PAYLOAD_SZ)
    
    def __init__(self,header:int, seq_nr:int, payload:str):    
        
        header_bytes = header.to_bytes(d.HEADER_SZ,'big')
        if len(header_bytes) != d.HEADER_SZ:
            raise d.InvalidDataSzException('CUSTOM_HEADER')
        self.__custom_header = header_bytes
        
        
        seq_nr_bytes = seq_nr.to_bytes(d.SEQ_NR_SZ,'big')
        if len(seq_nr_bytes) != d.SEQ_NR_SZ:
            raise d.InvalidDataSzException('SEQ_NR')
        self.__seq_nr = seq_nr_bytes
        
        
        payload_bytes = bytes(payload,'utf-8')
        payload_len_tmp = len(payload_bytes)
        
        if payload_len_tmp > d.MAX_DATA_SZ:
            raise d.InvalidDataSzException('ACTUAL_PAYLOAD')
        
        self.__data_len = payload_len_tmp.to_bytes(d.DATA_LEN_SZ,'big')
        
        if payload_len_tmp < d.MAX_DATA_SZ:
            dif = d.MAX_DATA_SZ - payload_len_tmp
            self.__payload = bytes(bytearray(payload_bytes) + bytearray(dif))
        else:
            self.__payload = payload_bytes
        
        self.__app_checksum = bytes(d.APP_CHECKSUM_SZ)
        
        self.__full_message = self.__custom_header + self.__seq_nr + self.__data_len + self.__app_checksum + self.__payload
      

          
    def get_msg_as_bytes(self) ->bytes:
        return bytes(self.__full_message)
      
      
    
    def print_header(self):
        print(self.__custom_header)
    def print_seq_nr(self):
        print(self.__seq_nr)
    def print_data_len(self):
        print(self.__data_len)
    def print_app_checksum(self):
        print(self.__app_checksum)
    def print_payload(self):
        print(self.__payload)
    def print_full(self):
        print(self.__full_message)
        
    def print_everything(self):
        self.print_header()
        self.print_seq_nr()
        self.print_data_len()
        self.print_app_checksum()
        self.print_payload()
        print()
        self.print_full()
        
        
        
        