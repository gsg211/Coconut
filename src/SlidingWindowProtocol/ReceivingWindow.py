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
        buffer: dict[int, udp.UDP_Packet] = {}
        expected_number=1
        h_done_received_and_acked = False


        while not h_done_received_and_acked:
            expected_packet = self.__manager.q_rcv_get()
            if expected_packet is None:
                if self.done_transmission:
                    time.sleep(self.__time_out_interval * 2)
                    h_done_received_and_acked = True
                time.sleep(0.01)
                continue

            raw_packet, (addr, port) = expected_packet
            pkt = udp.UDP_Packet.__new__(udp.UDP_Packet)
            pkt.init_from_full_message(bytearray(raw_packet))
            pkt.print_everything_decoded()

            sequence_number = pkt.get_seq_nr()

            if sequence_number == expected_number:
                self.packet_list.append(pkt)
                self.send_ACK(sequence_number)
                print(f"Receiver: Received expected packet {sequence_number}. Sending ACK {sequence_number}.")
                expected_number+=1

                while expected_number in buffer:
                    buffered_pkt = buffer.pop(expected_number)
                    self.packet_list.append(buffered_pkt)
                    self.send_ACK(expected_number)
                    print(f"Receiver: Processed buffered packet {expected_number}. Sending ACK {expected_number}.")
                    expected_number += 1

            elif sequence_number > expected_number:
                if sequence_number not in buffer:
                    buffer[sequence_number]=pkt
                    print(f"Receiver: Received out-of-order packet {sequence_number}. Buffering.")
                for missing_number in range(expected_number,sequence_number):
                    if missing_number not in buffer:
                        self.send_NAK(missing_number)
                        print(f"Receiver: Sending NAK for missing packet {missing_number}.")
            else:
                self.send_ACK(sequence_number)
                print(f"Receiver: Received duplicate packet {sequence_number}. Re-sending ACK {sequence_number}.")

            if self.packet_list and self.packet_list[-1].get_custom_header()==d.Flow_Header.H_DONE:
                self.done_transmission=True
                print(f"Receiver: H_DONE packet {sequence_number} received and added to list. Preparing to terminate.")



        self.__manager.signal_stop()
        print("Receiver: Transmission complete and manager signaled to stop.")
        return

    def get_data(self) -> str | None:
        if self.done_transmission:
            self.__manager.signal_stop()
            return ''.join(packet.get_payload() for packet in self.packet_list)
        return None



if __name__ == "__main__":
    sender = ReceivingWindow()
    sender.listen()
    print(sender.get_data())
