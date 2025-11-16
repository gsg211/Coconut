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
        self.window = [None] * window_size
        self.packet_list: list[udp.UDP_Packet] = list()

