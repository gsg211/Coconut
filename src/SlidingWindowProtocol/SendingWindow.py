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
                 socket_manager,
                 window_size=2,  #TODO: modify placeholder value
                 packet_data_size=5,  #TODO: modify placeholder value
                 time_out_interval = 0.1,  #TODO: modify placeholder value
                 packet_loss_chance=0.0):

        self.__window_size=window_size
        self.__packet_data_size=packet_data_size # the max size of a packet
        self.__manager = socket_manager




        self.__time_out_interval=time_out_interval
        self.__packet_loss_chance=packet_loss_chance
        self.window= [None] * window_size
        self.packet_list : list[udp.UDP_Packet]=list()

    #splits the input string into multiple strings of a max length (__packet_data_size)
    def __split_input(self,data:str) -> list[str]:
        it = iter(data)
        string_list = [''.join(islice(it, self.__packet_data_size)) \
               for _ in range((len(data) + self.__packet_data_size - 1) // self.__packet_data_size)]
        return string_list

    #converts the string into a list of packets
    def convert_data_to_packets(self, data:str):
        string_list=self.__split_input(data)
        sequence_counter=len(self.packet_list) + 1
        self.packet_list.clear()
        for string in string_list:
            packet_to_send=udp.UDP_Packet(d.Operation_Header.H_DATA,sequence_counter,string)
            self.packet_list.append(packet_to_send)
            sequence_counter+=1

    #decided if packet gets lost (used to simulate real packet  loss)
    def __will_lose(self) -> bool:
        return random.random() < self.__packet_loss_chance

    def __send_H_DONE(self,sequence_number):
        done_packet = udp.UDP_Packet(d.Flow_Header.H_DONE, sequence_number, '')
        self.__manager.q_snd_put(done_packet.get_full_message())

    def prepare_operation_header(self,custom_header:int):
        sequence_counter = len(self.packet_list) + 1
        packet_to_send = udp.UDP_Packet(custom_header,sequence_counter,"")
        self.packet_list.append(packet_to_send)

    def clear_packet_list(self):
        self.packet_list = []


    def start(self):
       self.__manager.start()

    #sends the data using the sliding window protocol
    def send(self):
        if not self.__manager.is_started:
            self.__manager.start()

        total_packets = len(self.packet_list)
        done_seq_num = total_packets + 1

        base = 1
        next_seq_num = 1

        acked_packets = [False] * (done_seq_num + 1)
        last_sent_time = {}  # seq_num -> timestamp

        print(f"Sender: Starting transmission of {total_packets} packets (Done Seq: {done_seq_num})")

        while not acked_packets[done_seq_num]:

            # 1. SEND PHASE (Fill the window)
            while next_seq_num <= total_packets and (next_seq_num - base) < self.__window_size:
                packet = self.packet_list[next_seq_num - 1]
                if not self.__will_lose():
                    self.__manager.q_snd_put(packet.get_full_message())

                last_sent_time[next_seq_num] = time.time()
                next_seq_num += 1
                time.sleep(0.0001)

            if next_seq_num > total_packets and not acked_packets[done_seq_num]:
                if done_seq_num not in last_sent_time or \
                        (time.time() - last_sent_time[done_seq_num] > self.__time_out_interval):
                    self.__send_H_DONE(done_seq_num)
                    last_sent_time[done_seq_num] = time.time()

            for _ in range(self.__window_size):
                received = self.__manager.q_rcv_get()
                if not received:
                    break

                raw_pkt, _ = received
                pkt = udp.UDP_Packet.__new__(udp.UDP_Packet)
                pkt.init_from_full_message(bytearray(raw_pkt))

                seq = pkt.get_seq_nr()
                header = pkt.get_custom_header()

                if header == d.Flow_Header.H_ACK:
                    if 1 <= seq <= done_seq_num:
                        acked_packets[seq] = True
                        while base <= total_packets and acked_packets[base]:
                            base += 1
                            if base - 1 in last_sent_time:
                                del last_sent_time[base - 1]

                elif header == d.Flow_Header.H_NAK:
                    if base <= seq <= total_packets:
                        re_pkt = self.packet_list[seq - 1]
                        self.__manager.q_snd_put(re_pkt.get_full_message())
                        last_sent_time[seq] = time.time()

            now = time.time()
            for s in range(base, next_seq_num):
                if not acked_packets[s]:
                    if s in last_sent_time and (now - last_sent_time[s]) > self.__time_out_interval:
                        if not self.__will_lose():
                            self.__manager.q_snd_put(self.packet_list[s - 1].get_full_message())
                        last_sent_time[s] = now

            time.sleep(0.001)

