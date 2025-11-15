import protocol.SocketManager as sm
import defines as d
import time
if __name__ == "__main__":
    clB = sm.SocketManager(d.LOCAL_HOST_ADDR, d.DEFAULT_PORT_A, 'A')
    clB.set_peer_data(d.LOCAL_HOST_ADDR, d.DEFAULT_PORT_B)
    clB.start()

    while True:
        packet = clB.q_rcv_get()
        if packet is not None:
            payload, (addr, port) = packet
            print(f"Received from {addr}:{port} -> {payload.decode()}")
        time.sleep(0.01)

