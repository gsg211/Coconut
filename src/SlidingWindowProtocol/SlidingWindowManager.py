
import defines as d
from src.SlidingWindowProtocol.SendingWindow import SendingWindow
from src.SlidingWindowProtocol.ReceivingWindow import ReceivingWindow
import protocol.SocketManager as sm


class SlidingWindowManager:
    def __init__(self,
                 window_size=2,
                 packet_data_size=5,
                 sender_address=d.LOCAL_HOST_ADDR_A,
                 sender_port=d.DEFAULT_PORT_A,
                 destination_address=d.LOCAL_HOST_ADDR_B,
                 destination_port=d.DEFAULT_PORT_B,
                 time_out_interval=0.1,
                 packet_loss_chance=0.0):

        self.socket_manager = sm.SocketManager(sender_address, sender_port, "def_name")
        self.socket_manager.set_peer_data(destination_address, destination_port)

        self._sw = SendingWindow(
            socket_manager=self.socket_manager,
            window_size=window_size,
            packet_data_size=packet_data_size,
            time_out_interval=time_out_interval,
            packet_loss_chance=packet_loss_chance
        )

        self._rw = ReceivingWindow(
            socket_manager=self.socket_manager,
            window_size=window_size,
            packet_data_size=packet_data_size,
            time_out_interval=time_out_interval,
            packet_loss_chance=packet_loss_chance
        )

    def prepare_data_packets(self, data: str) -> None:
        self._sw.convert_data_to_packets(data)

    def prepare_operation_packet(self, custom_header: int) -> None:
        self._sw.prepare_operation_header(custom_header)

    def clear_sending_packet_list(self):
        self._sw.clear_packet_list()


    def listen(self):
        self._rw.listen()

    def receive_window(self) -> str:
        data = self._rw.get_data()
        return data if data else ""

    def get_custom_headers(self) ->list[int]:
        return self._rw.get_custom_headers()

    def send_window(self) -> None:
        self._sw.send()

    def stop(self):
        self.socket_manager.signal_stop()

