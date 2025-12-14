import UDP_packet as udp
import defines as d
from src.SlidingWindowProtocol import StorageManager as storage_manager
from src.SlidingWindowProtocol import SlidingWindowManager as window_manager


class DataTransferManager:
    def __init__(self,
                 root_dir: str = "storage",

                 window_size=2,
                 packet_data_size=5,

                 sender_address=d.LOCAL_HOST_ADDR_A,
                 sender_port=d.DEFAULT_PORT_A,

                 destination_address=d.LOCAL_HOST_ADDR_B,
                 destination_port=d.DEFAULT_PORT_B,

                 time_out_interval=0.1,
                 packet_loss_chance=0.0
                 ):
        self._storage_manager = storage_manager.StorageManager(root_dir)

        self._window_manager = window_manager.SlidingWindowManager(
            window_size=window_size,
            packet_data_size=packet_data_size,
            sender_address=sender_address,
            sender_port=sender_port,
            destination_address=destination_address,
            destination_port=destination_port,
            time_out_interval=time_out_interval,
            packet_loss_chance=packet_loss_chance
        )

    def getStorageManager(self) -> storage_manager.StorageManager:
        return self._storage_manager

    def listen(self):
        self._window_manager.listen()

    def get_data(self) -> str:
        return self._window_manager.receive_window()

    def get_custom_headers(self) -> list[int]:
        return self._window_manager.get_custom_headers()




    def prepare_data_packets(self,data:str)->None:
        self._window_manager.prepare_data_packets(data)

    def prepare_operation_packet(self,op_header:d.Operation_Header)->None:
        self._window_manager.prepare_operation_packet(op_header)

    def send_prepared_packets(self) -> None:
        self._window_manager.send_window()



    def send_special_packet(self, header_type):
        packet = udp.UDP_Packet(header_type, 0, "")
        self._window_manager._sw._SendingWindow__manager.q_snd_put(packet.get_full_message())