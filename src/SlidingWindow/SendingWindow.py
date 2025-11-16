import time
from operator import truediv

import protocol.SocketManager as sm
from itertools import islice
import UDP_packet as udp
import defines as d
import random

"""
DEFAULT_PORT_A => SENDER
DEFAULT_PORT_B => RECEIVER
"""
class SendingWindow:
    def __init__(self,
                 window_size=2,  #TODO: modify placeholder value
                 packet_data_size=5,  #TODO: modify placeholder value
                 sender_address = d.LOCAL_HOST_ADDR,
                 sender_port = d.DEFAULT_PORT_A,
                 destination_address = d.LOCAL_HOST_ADDR,
                 destination_port = d.DEFAULT_PORT_B,
                 time_out_interval = 0.1,  #TODO: modify placeholder value
                 packet_loss_chance=0.0):

        self.__window_size=window_size
        self.__packet_data_size=packet_data_size # the max size of a packet
        self.__manager=sm.SocketManager(sender_address, sender_port, "sender")
        self.__manager.set_peer_data(destination_address, destination_port)
        self.__time_out_interval=time_out_interval
        self.__packet_loss_chance=packet_loss_chance
        self.window= [None] * window_size
        self.packet_list : list[udp.UDP_Packet]=list()

    #splits the input string into multiple strings of a max length (__packet_data_size)
    def split_input(self,data:str) -> list[str]:
        it = iter(data)
        string_list = [''.join(islice(it, self.__packet_data_size)) \
               for _ in range((len(data) + self.__packet_data_size - 1) // self.__packet_data_size)]
        return string_list

    #converts the string into a list of packets
    def convert_data_to_packets(self, data:str):
        string_list=self.split_input(data)
        sequence_counter=1
        for string in string_list:
            packet_to_send=udp.UDP_Packet(d.Operation_Header.H_DATA,sequence_counter,string)
            packet_to_send.print_payload_decoded()
            self.packet_list.append(packet_to_send)
            sequence_counter+=1

    #decided if packet gets lost (used to simulate real packet  loss)
    def will_lose(self) -> bool:
        return random.random() < self.__packet_loss_chance

    def send_H_DONE(self,sequence_number):
        nak_packet = udp.UDP_Packet(d.Flow_Header.H_NAK, sequence_number, '')
        self.__manager.q_snd_put(nak_packet.get_full_message())

    #sends the data using the sliding window protocol
    def send(self, data: str):

        self.convert_data_to_packets(data)
        self.__manager.start()
        window: list[udp.UDP_Packet] =list()
        current_window_position=0
        while current_window_position + self.__window_size <= len(self.packet_list):

            for position in range(current_window_position,current_window_position + self.__window_size):
                packet_to_send=self.packet_list[position]
                window.append(packet_to_send)
                self.__manager.q_snd_put(packet_to_send.get_full_message())

            while window: #wait for ACKS
                print(window)
                packet = self.__manager.q_rcv_get()
                if packet is None:
                    time.sleep(0.01)
                    continue

                raw_packet, (addr, port) = packet
                pkt = udp.UDP_Packet.__new__(udp.UDP_Packet)
                pkt.init_from_full_message(bytearray(raw_packet))
                pkt.print_everything_decoded()

                if pkt.get_custom_header() == d.Flow_Header.H_NAK:
                    seq=pkt.get_seq_nr()
                    for packet in window:
                        if packet.get_seq_nr() == seq:
                            self.__manager.q_snd_put(packet.get_full_message())
                elif pkt.get_custom_header() == d.Flow_Header.H_ACK:
                    seq = pkt.get_seq_nr()
                    for packet in window:
                        if packet.get_seq_nr() == seq:
                            window.remove(packet)

            current_window_position+=self.__window_size

        self.send_H_DONE(len(self.packet_list)+1)




if __name__=="__main__":
    sender=SendingWindow()

    sender.send("hello I am a very big string that needs splitting")

    print(sender.packet_list)
    # for packet in sender.packet_list:
    #     print(packet.print_everything())
    #     print()


