from SlidingWindowProtocol import DataTransferManager as df
from defines import *
from client.Client import Client

if __name__ == "__main__":

    # dm = df.DataTransferManager(
    #     root_dir="ClientStorage",
    #     window_size=2,
    #     packet_data_size=5,
    #     sender_address=LOCAL_HOST_ADDR,
    #     sender_port=DEFAULT_PORT_A,
    #     destination_port=DEFAULT_PORT_B
    # )
    #
    # dm.send_window("NewFile.txt")
    # dm.send_window(dm.getStorageManager().read("misc"))

    config = {}

    config["root_dir"] = CLIENT_ROOT_PATH

    config["window_size"] = 2
    config["packet_data_size"] = 5

    config["sender_address"] = LOCAL_HOST_ADDR_B # here the client - A is the sender and the server - B is the destination
    config["sender_port"] = DEFAULT_PORT_B

    config["destination_address"] = LOCAL_HOST_ADDR_A
    config["destination_port"] = DEFAULT_PORT_A

    config["time_out_interval"] = 0.3
    config["packet_loss_chance"] = 0

    client_instance = Client(config)


    while True:
        print("Select your operation:")
        print("0 - Quit")

        print("1 - Access")
        print("2 - Create")
        print("3 - Delete")
        print("4 - Move")
        print("5 - Download")
        print("6 - Upload")

        opt = int(input(''))

        if opt == 0:
            break
        elif opt == 1:

            client_instance.startOp_view_tree()
            data = client_instance.endOp_get_data()
            print(data)

        elif opt == 2:
            pass
        elif opt == 3:
            pass
        elif opt == 4:
            pass
        elif opt == 5:
            pass
        elif opt == 6:
            pass
        else:
            print("Invalid option, pick again")

    client_instance.stop()