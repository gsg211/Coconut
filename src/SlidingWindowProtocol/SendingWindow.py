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
                 sender_address = d.LOCAL_HOST_ADDR_A,
                 sender_port = d.DEFAULT_PORT_A,
                 destination_address = d.LOCAL_HOST_ADDR_B,
                 destination_port = d.DEFAULT_PORT_B,
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
        sequence_counter=1
        self.packet_list.clear()
        for string in string_list:
            packet_to_send=udp.UDP_Packet(d.Operation_Header.H_DATA,sequence_counter,string)
            packet_to_send.print_payload_decoded()
            self.packet_list.append(packet_to_send)
            sequence_counter+=1

    #decided if packet gets lost (used to simulate real packet  loss)
    def __will_lose(self) -> bool:
        return random.random() < self.__packet_loss_chance

    def __send_H_DONE(self,sequence_number):
        done_packet = udp.UDP_Packet(d.Flow_Header.H_DONE, sequence_number, '')
        self.__manager.q_snd_put(done_packet.get_full_message())

    def prepare_operation_header(self,header_type:d.Operation_Header):
        sequence_counter = 1
        packet_to_send = udp.UDP_Packet(header_type,sequence_counter,"")
        self.packet_list.append(packet_to_send)

    def start(self):
       self.__manager.start()

    #sends the data using the sliding window protocol
    def send(self):
        if not self.__manager.is_started:
            self.__manager.start()

        base = 1
        next_seq_num = 1
        last_seen_time = {}
        acked_packets = [False] * (len(self.packet_list) + 1)

        total_packets = len(self.packet_list)
        done_sending_data = False
        done_transmission_ack = False

        while not (done_sending_data and done_transmission_ack and base > total_packets):

            while next_seq_num <= total_packets and (next_seq_num - base) < self.__window_size:
                packet_to_send = self.packet_list[next_seq_num - 1]
                if not self.__will_lose():
                    self.__manager.q_snd_put(packet_to_send.get_full_message())
                    print(f"Sender: Sent packet {packet_to_send.get_seq_nr()}")
                else:
                    print(f"Sender: Simulating loss of packet {packet_to_send.get_seq_nr()}")
                last_seen_time[next_seq_num] = time.time()
                next_seq_num += 1


            if next_seq_num > total_packets and not done_sending_data:
                self.__send_H_DONE(total_packets + 1)
                last_seen_time[total_packets + 1] = time.time()
                print(f"Sender: Sent H_DONE with sequence number {total_packets + 1}")
                done_sending_data = True


            current_time = time.time()
            received_packet = self.__manager.q_rcv_get()

            if received_packet:
                raw_packet, (addr, port) = received_packet
                pkt = udp.UDP_Packet.__new__(udp.UDP_Packet)
                pkt.init_from_full_message(bytearray(raw_packet))
                pkt.print_everything_decoded()
                seq = pkt.get_seq_nr()

                if pkt.get_custom_header() == d.Flow_Header.H_ACK:
                    print(f"Sender: Received ACK for {seq}")
                    if seq == total_packets + 1:
                        done_transmission_ack = True
                        print("Sender: Received ACK for H_DONE. Transmission complete.")
                    elif base <= seq <= total_packets:
                        acked_packets[seq] = True
                        while base <= total_packets and acked_packets[base]:
                            print(f"Sender: Advanced base to {base + 1}")
                            base += 1
                elif pkt.get_custom_header() == d.Flow_Header.H_NAK:
                    print(f"Sender: Received NAK for {seq}. Retransmitting packet {seq}.")
                    if base <= seq <= total_packets:
                        packet_to_retransmit = self.packet_list[seq - 1]
                        self.__manager.q_snd_put(packet_to_retransmit.get_full_message())
                        last_seen_time[seq] = time.time()
            else:

                for seq_num in range(base, next_seq_num):
                    if not acked_packets[seq_num] and (current_time - last_seen_time.get(seq_num, 0)) > self.__time_out_interval:
                        print(f"Sender: Timeout for packet {seq_num}. Retransmitting.")
                        packet_to_retransmit = self.packet_list[seq_num - 1]
                        self.__manager.q_snd_put(packet_to_retransmit.get_full_message())
                        last_seen_time[seq_num] = time.time()

                if done_sending_data and not done_transmission_ack and (current_time - last_seen_time.get(total_packets + 1, 0)) > self.__time_out_interval:
                    self.__send_H_DONE(total_packets + 1)
                    last_seen_time[total_packets + 1] = time.time()
                    print(f"Sender: Timeout for H_DONE. Retransmitting H_DONE with sequence number {total_packets + 1}.")

            time.sleep(0.01)


        print("Sender: All packets sent and acknowledged.")





if __name__=="__main__":
    sender=SendingWindow()

    sender.send("hello I am a very big string that needs splitting")

    print(sender.packet_list)
    # for packet in sender.packet_list:
    #     print(packet.print_everything())
    #     print()


