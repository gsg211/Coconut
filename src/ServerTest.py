from SlidingWindowProtocol import DataTransferManager as df
from defines import *
import time

from server.Server import Server

if __name__ == "__main__":

    # dm = df.DataTransferManager(
    #     root_dir="ServerStorage",
    #     window_size=2,
    #     packet_data_size=5,
    #     sender_address=LOCAL_HOST_ADDR,
    #     sender_port=DEFAULT_PORT_A,
    #     destination_port=DEFAULT_PORT_B
    # )
    #
    # print("Server: Listening...")
    # dm.listen()
    # name = dm.get_data()
    # time.sleep(1)
    # dm.listen()
    # dm.getStorageManager().write(name,dm.get_data())
    config = {}

    config["root_dir"] = SERVER_ROOT_PATH

    config["window_size"] = 2
    config["packet_data_size"] = 5

    config["sender_address"] = LOCAL_HOST_ADDR_A  # here the client - B is the sender and the server - A is the destination
    config["sender_port"] = DEFAULT_PORT_A

    config["destination_address"] = LOCAL_HOST_ADDR_B
    config["destination_port"] = DEFAULT_PORT_B

    config["time_out_interval"] = 0.2
    config["packet_loss_chance"] = 0

    server_instance = Server(config)

    server_instance.startOp_listen()
