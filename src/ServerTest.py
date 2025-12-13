from SlidingWindowProtocol import DataTransferManager as df
from defines import *
import time
if __name__ == "__main__":

    dm = df.DataTransferManager(
        root_dir="ServerStorage",
        window_size=2,
        packet_data_size=5,
        sender_address=LOCAL_HOST_ADDR,
        sender_port=DEFAULT_PORT_A,
        destination_port=DEFAULT_PORT_B
    )

    print("Server: Listening...")
    dm.listen()
    name = dm.get_data()
    time.sleep(1)
    dm.getStorageManager().write(name,dm.get_data())
