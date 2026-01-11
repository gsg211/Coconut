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

        self.window_manager = window_manager.SlidingWindowManager(
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
        self.window_manager.listen()

    def get_data(self) -> str:
        return self.window_manager.receive_window()

    def get_custom_headers(self) -> list[int]:
        return self.window_manager.get_custom_headers()

    def prepare_data_packets(self,data:str)->None:
        self.window_manager.prepare_data_packets(data)

    def prepare_operation_packet(self,custom_header:int)->None:
        self.window_manager.prepare_operation_packet(custom_header)

    def send_prepared_packets(self) -> None:
        self.window_manager.send_window()

    def clear_sending_packet_list(self):
        self.window_manager.clear_sending_packet_list()


    def clear_receiving_queue(self):
        self.window_manager.socket_manager.flush_receive_queue()

    def stop(self):
        self.window_manager.stop()
