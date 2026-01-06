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
                 socket_manager,
                 window_size=2,  #TODO: modify placeholder value
                 packet_data_size=5,  #TODO: modify placeholder value
                 sender_address = d.LOCAL_HOST_ADDR_A,
                 sender_port = d.DEFAULT_PORT_A,
                 destination_address = d.LOCAL_HOST_ADDR_B,
                 destination_port = d.DEFAULT_PORT_B,
                 time_out_interval = 0.1,  #TODO: modify placeholder value
                 packet_loss_chance=0.0,
                 ):

        self.__window_size = window_size
        self.__packet_data_size = packet_data_size  # the max size of a packet
        self.__manager = socket_manager


        # self.__manager = sm.SocketManager(destination_address, destination_port, "receiver")
        # self.__manager.set_peer_data(sender_address, sender_port)

        self.__time_out_interval = time_out_interval
        self.__packet_loss_chance = packet_loss_chance
        self.packet_list: list[udp.UDP_Packet] = list()
        self.done_transmission=False


    def __send_ACK(self, sequence_number):
        ack_packet=udp.UDP_Packet(d.Flow_Header.H_ACK,sequence_number,'')
        self.__manager.q_snd_put(ack_packet.get_full_message())

    def __send_NAK(self, sequence_number):
        nak_packet = udp.UDP_Packet(d.Flow_Header.H_NAK, sequence_number, '')
        self.__manager.q_snd_put(nak_packet.get_full_message())

    # decided if packet gets lost (used to simulate real packet  loss)
    def __will_lose(self) -> bool:
        return random.random() < self.__packet_loss_chance

    def start(self):
        self.__manager.start()

    def listen(self):
        if not self.__manager.is_started:
            self.__manager.start()

        buffer: dict[int, udp.UDP_Packet] = {}
        expected_number = 1
        self.done_transmission = False
        self.packet_list.clear()

        final_sequence_number = -1

        while True:
            expected_packet = self.__manager.q_rcv_get()

            if expected_packet is None:
                if final_sequence_number != -1 and expected_number > final_sequence_number:
                    break
                time.sleep(0.001)
                continue

            raw_packet, (addr, port) = expected_packet
            pkt = udp.UDP_Packet.__new__(udp.UDP_Packet)
            pkt.init_from_full_message(bytearray(raw_packet))
            seq = pkt.get_seq_nr()

            if pkt.get_custom_header() == d.Flow_Header.H_DONE:
                final_sequence_number = seq
                self.done_transmission = True

            if seq == expected_number:
                self.packet_list.append(pkt)
                self.__send_ACK(seq)
                expected_number += 1

                # Pull from buffer
                while expected_number in buffer:
                    buf_pkt = buffer.pop(expected_number)
                    self.packet_list.append(buf_pkt)
                    self.__send_ACK(expected_number)
                    expected_number += 1
            elif seq > expected_number:
                if seq not in buffer:
                    buffer[seq] = pkt
                self.__send_NAK(expected_number)
            else:
                self.__send_ACK(seq)

            if final_sequence_number != -1 and expected_number > final_sequence_number:
                break

    def get_custom_headers(self) -> list[int]:
        lst = []
        if self.done_transmission:
            for packet in self.packet_list:
                lst.append(packet.get_custom_header())

        return lst

    def get_data(self) -> str | None:
        if self.done_transmission:
            data = ''.join(packet.get_payload() for packet in self.packet_list
                           if packet.get_custom_header() == d.Operation_Header.H_DATA)
            return data
        return None



if __name__ == "__main__":
    sender = ReceivingWindow()
    sender.listen()
    # print(sender.get_data())
