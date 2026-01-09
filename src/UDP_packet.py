import defines as d
class UDP_Packet():

    def __init__(self,header:int, seq_nr:int, payload:str):    
        
        header_bytes = header.to_bytes(d.UDP_Size.HEADER_SZ,'big')
        if len(header_bytes) != d.UDP_Size.HEADER_SZ:
            raise d.InvalidDataSzException('CUSTOM_HEADER')
        self.__custom_header = header_bytes
        
        
        seq_nr_bytes = seq_nr.to_bytes(d.UDP_Size.SEQ_NR_SZ,'big')
        if len(seq_nr_bytes) != d.UDP_Size.SEQ_NR_SZ:
            raise d.InvalidDataSzException('SEQ_NR')
        self.__seq_nr = seq_nr_bytes
        
        payload_bytes = bytes(payload,'utf-8')
        payload_len_tmp = len(payload_bytes)
        
        if payload_len_tmp > d.UDP_Size.MAX_DATA_SZ:        
            raise d.InvalidDataSzException('ACTUAL_PAYLOAD')
        
        self.__data_len = payload_len_tmp.to_bytes(d.UDP_Size.DATA_LEN_SZ,'big')
        
        if payload_len_tmp < d.UDP_Size.MAX_DATA_SZ:
            dif = d.UDP_Size.MAX_DATA_SZ - payload_len_tmp
            self.__payload = bytes(bytearray(payload_bytes) + bytearray(dif))
        else:
            self.__payload = payload_bytes

        self.__full_message = bytearray(d.UDP_Size.PAYLOAD_SZ)
        self.__app_checksum                 = bytes(d.UDP_Size.APP_CHECKSUM_SZ)
        self.__full_message[d.HEADER_POS]   = self.__custom_header
        self.__full_message[d.SEQ_NR_POS]   = self.__seq_nr
        self.__full_message[d.DATA_LEN_POS] = self.__data_len
        self.__full_message[d.CHECKSUM_POS] = self.__app_checksum
        self.__full_message[d.PAYLOAD_POS]  = self.__payload

        checksum                            = self.calculate_checksum()
        self.__app_checksum                 = checksum
        self.__full_message[d.CHECKSUM_POS] = self.__app_checksum



    def init_from_full_message(self, full_message:bytearray):
        if len(full_message) != d.UDP_Size.PAYLOAD_SZ:
            raise d.InvalidDataSzException('FULL MESSAGE ON INIT')
        self.__full_message  = full_message
        self.__custom_header = self.__full_message[d.HEADER_POS]   
        self.__seq_nr        = self.__full_message[d.SEQ_NR_POS]   
        self.__data_len      = self.__full_message[d.DATA_LEN_POS] 
        self.__app_checksum  = self.__full_message[d.CHECKSUM_POS] 
        self.__payload       = self.__full_message[d.PAYLOAD_POS]  
        
    def get_custom_header(self)->int:
        return int.from_bytes(self.__custom_header,'big')
    def get_seq_nr(self)->int:
        return int.from_bytes(self.__seq_nr,'big')
    def get_data_len(self)->int:
        return int.from_bytes(self.__data_len,'big')
    def get_checksum(self)->int:
        return int.from_bytes(self.__app_checksum,'big')
    def get_payload(self)->str:
        data_len = self.get_data_len()
        return self.__payload[0:data_len].decode()
    def get_full_message(self):
        return self.__full_message
    
        
    def get_msg_as_bytes(self) ->bytes:
        return bytes(self.__full_message)

    def calculate_checksum(self) -> bytes:
        total = int(0)
        for i in range(0,d.UDP_Size.PAYLOAD_SZ,d.UDP_Size.CHECKSUM_CHUNK_SZ):
            current_chunk = self.__full_message[i:i+d.UDP_Size.CHECKSUM_CHUNK_SZ]
            total += int.from_bytes(current_chunk,'big')
            wraparound_bit = total >> 16 # (2 byte checksum)
            total = (total & 0xFFFF) + wraparound_bit
        total = ~total # c1
        total = total & 0xFFFF # lower 16 bits, removes extra 1 bits from C1
        return total.to_bytes(d.UDP_Size.CHECKSUM_CHUNK_SZ,'big')
      

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

    def print_header_decoded(self):
        print(self.get_custom_header())

    def print_seq_nr_decoded(self):
        print(self.get_seq_nr())

    def print_data_len_decoded(self):
        print(self.get_data_len())

    def print_app_checksum_decoded(self):
        print(self.get_checksum())

    def print_payload_decoded(self):
        print(self.get_payload())

    def print_everything_decoded(self):
        self.print_header_decoded()
        self.print_seq_nr_decoded()
        self.print_data_len_decoded()
        self.print_app_checksum_decoded()
        self.print_payload_decoded()
