import protocol.SocketManager as SM
import defines as d
import time 
if __name__ == "__main__":
    clB = SM.SocketManager(d.LOCAL_HOST_ADDR,d.DEFAULT_PORT_B,'B')
    clB.set_peer_data(d.LOCAL_HOST_ADDR,d.DEFAULT_PORT_A)
    clB.start()
    
    clB.q_snd_put("hello, A".encode())
    print("sent from clB")
    time.sleep(5)
    for i in range(0,5):
        data = clB.q_rcv_get()
        print(data)
    
    clB.signal_stop()
            