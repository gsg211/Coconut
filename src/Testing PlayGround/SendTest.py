import protocol.SocketManager as sm
import defines as d
import time
if __name__ == "__main__":
    clB = sm.SocketManager(d.LOCAL_HOST_ADDR, d.DEFAULT_PORT_B, 'B')
    clB.set_peer_data(d.LOCAL_HOST_ADDR, d.DEFAULT_PORT_A)
    clB.start()
    while True:
        clB.q_snd_put("hello, A".encode())
        time.sleep(1)
