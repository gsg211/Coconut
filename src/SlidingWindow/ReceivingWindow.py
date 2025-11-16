from token import NUMBER
import random
import time

import protocol.SocketManager as sm
from itertools import islice
import UDP_packet as udp
import defines as d


"""
DEFAULT_PORT_A => SENDER
DEFAULT_PORT_B => RECEIVER
"""
class ReceivingWindow:
    def __init__(self,
                 window_size=2,  #TODO: modify placeholder value
                 packet_data_size=5,  #TODO: modify placeholder value
                 sender_address = d.LOCAL_HOST_ADDR,
                 sender_port = d.DEFAULT_PORT_A,
                 destination_address = d.LOCAL_HOST_ADDR,
                 destination_port = d.DEFAULT_PORT_B,
                 time_out_interval = 0.1,  #TODO: modify placeholder value
                 packet_loss_chance=0.0):

        self.__window_size = window_size
        self.__packet_data_size = packet_data_size  # the max size of a packet
        self.__manager = sm.SocketManager(destination_address, destination_port, "receiver")
        self.__manager.set_peer_data(sender_address, sender_port)
        self.__time_out_interval = time_out_interval
        self.__packet_loss_chance = packet_loss_chance
        self.packet_list: list[udp.UDP_Packet] = list()
        self.done_transmission=False

    def send_ACK(self, sequence_number):
        ack_packet=udp.UDP_Packet(d.Flow_Header.H_ACK,sequence_number,'')
        self.__manager.q_snd_put(ack_packet.get_full_message())

    def send_NAK(self, sequence_number):
        nak_packet = udp.UDP_Packet(d.Flow_Header.H_NAK, sequence_number, '')
        self.__manager.q_snd_put(nak_packet.get_full_message())

    # decided if packet gets lost (used to simulate real packet  loss)
    def will_lose(self) -> bool:
        return random.random() < self.__packet_loss_chance

    def listen(self):
        self.__manager.start()
        window: list[udp.UDP_Packet]
        buffer: dict[int, udp.UDP_Packet] = {}
        expected_number=1
        total_number_of_packets=-1
        while True:
            expected_packet = self.__manager.q_rcv_get()
            if expected_packet is None:
                time.sleep(0.01)
                continue

            raw_packet, (addr, port) = expected_packet
            pkt = udp.UDP_Packet.__new__(udp.UDP_Packet)
            pkt.init_from_full_message(bytearray(raw_packet))
            pkt.print_everything_decoded()

            if pkt.get_custom_header() == d.Flow_Header.H_DONE:
                total_number_of_packets=pkt.get_seq_nr()
                continue

            sequence_number = pkt.get_seq_nr()
            if sequence_number == expected_number:
                self.packet_list.append(pkt)
                self.send_ACK(sequence_number)
                expected_number+=1

                while expected_number in buffer:
                    expected_packet = buffer[expected_number]
                    self.packet_list.append(expected_packet)
                    buffer.pop(expected_number)
                    expected_number += 1

            elif sequence_number > expected_number:
                buffer[sequence_number]=pkt
                for missing_number in range(expected_number,sequence_number):
                    self.send_NAK(missing_number)

            else:
                pass

            if len(self.packet_list) == total_number_of_packets - 1 :
                self.done_transmission=True
                return

    def get_data(self) -> str | None:
        if self.done_transmission:
            return ''.join(packet.get_payload() for packet in self.packet_list)
        return None



if __name__ == "__main__":
    sender = ReceivingWindow()
    sender.listen()
    while True:
        string=sender.get_data()
        if string is not None:
            print(string)
            break

