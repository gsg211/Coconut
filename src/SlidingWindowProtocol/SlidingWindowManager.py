
import defines as d
from src.SlidingWindowProtocol.SendingWindow import SendingWindow
from src.SlidingWindowProtocol.ReceivingWindow import ReceivingWindow


class SlidingWindowManager:
    def __init__(self,
                 window_size=2,
                 packet_data_size=5,
                 sender_address=d.LOCAL_HOST_ADDR,
                 sender_port=d.DEFAULT_PORT_A,
                 destination_address=d.LOCAL_HOST_ADDR,
                 destination_port=d.DEFAULT_PORT_B,
                 time_out_interval=0.1,
                 packet_loss_chance=0.0):

        self._sw = SendingWindow(
            window_size=window_size,
            packet_data_size=packet_data_size,
            sender_address=sender_address,
            sender_port=sender_port,
            destination_address=destination_address,
            destination_port=destination_port,
            time_out_interval=time_out_interval,
            packet_loss_chance=packet_loss_chance
        )

        self._rw = ReceivingWindow(
            window_size=window_size,
            packet_data_size=packet_data_size,
            sender_address=sender_address,
            sender_port=sender_port,
            destination_address=destination_address,
            destination_port=destination_port,
            time_out_interval=time_out_interval,
            packet_loss_chance=packet_loss_chance
        )

    def listen(self):
        self._rw.listen()

    def receive_window(self) -> str:
        data = self._rw.get_data()
        return data if data else ""

    def send_window(self, data: str) -> None:
        self._sw.send(data)

