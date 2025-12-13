from SlidingWindowProtocol import DataTransferManager as df
from defines import *

if __name__ == "__main__":

    dm = df.DataTransferManager(
        root_dir="ClientStorage",
        window_size=2,
        packet_data_size=5,
        sender_address=LOCAL_HOST_ADDR,
        sender_port=DEFAULT_PORT_A,
        destination_port=DEFAULT_PORT_B
    )

    dm.send_window("NewFile.txt")
    dm.send_window(dm.getStorageManager().read("misc"))