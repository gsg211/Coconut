import protocol.SocketManager as sm
import defines as d
import time
import UDP_packet as udp
if __name__ == "__main__":
    clB = sm.SocketManager(d.LOCAL_HOST_ADDR, d.DEFAULT_PORT_B, 'A')
    clB.set_peer_data(d.LOCAL_HOST_ADDR, d.DEFAULT_PORT_A)
    clB.start()

    while True:
        packet = clB.q_rcv_get()

        if packet is not None:
            raw_packet, (addr, port) = packet
            pkt = udp.UDP_Packet.__new__(udp.UDP_Packet)
            pkt.init_from_full_message(bytearray(raw_packet))
            pkt.print_everything_decoded()
        time.sleep(0.01)

