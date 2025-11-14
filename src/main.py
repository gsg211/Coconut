import UDP_packet as udpp
import defines as d
import utils.myTimer as t
import utils.ConfigData as c
from queue import Queue

import debugging.logs as logs

import protocol.SocketManager as SM



if __name__ == '__main__':
    seq_nr = 2
    msg = bytes("hello",'utf-8')
    try:
        my_packet = udpp.UDP_Packet(d.Flow_Header.H_SYN,seq_nr,'Hello')
    except d.InvalidDataSzException as e:
        print(e)
        
    bts = my_packet.get_msg_as_bytes()
    
    try:
        my_packet.init_from_full_message(bts)
    except d.InvalidDataSzException as e:
        print(e)
        
    checksum = my_packet.calculate_checksum()
    print(checksum[0])    
    print(checksum[1])
    print()
    
    print(my_packet.get_payload())
    
    print()
    # my_timer = t.myTimer(0.5,3)
    # my_timer.run()
    # t.time.sleep(5)
    # print(my_timer.try_consume_notification()[0])
    # my_timer.notify_stop()
    
    # try:
    #     my_data = c.ConfigData(True)
    #     my_data.save_current_config()
    #     print(my_data.find_client(1))
    # except Exception as e:
    #     print(str(e))
    # my_data.print_data()
    
    
    clA = SM.SocketManager(d.LOCAL_HOST_ADDR,d.DEFAULT_PORT_A,'A')
    clA.set_peer_data(d.LOCAL_HOST_ADDR,d.DEFAULT_PORT_B)
    clA.start()
    clA.q_snd_put("hello1, B".encode())
    clA.q_snd_put("hello2, B".encode())
    clA.q_snd_put("hello3, B".encode())
    clA.q_snd_put("hello4, B".encode())
    clA.q_snd_put("hello5, B".encode())
    
    print("sent from clA")
    clA.signal_stop()
    
    


  
        