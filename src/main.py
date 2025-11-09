import UDP_packet as udpp
import defines as d

if __name__ == '__main__':
    seq_nr = 2
    msg = bytes("hello",'utf-8')
    my_packet = udpp.UDP_Packet(d.Flow_Header.H_SYN,3,'Hello')
    bts = my_packet.get_msg_as_bytes()
    