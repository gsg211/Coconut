from SlidingWindowProtocol import DataTransferManager as dtm
import defines as d
import signal
import sys

class Server:
    def __init__(self, config:{}):
        self.data_manager = dtm.DataTransferManager(
            config["root_dir"],

            config["window_size"],
            config["packet_data_size"],

            config["sender_address"], # here the server - B is the sender and the client - A is the destination
            config["sender_port"],

            config["destination_address"],
            config["destination_port"],

            config["time_out_interval"],
            config["packet_loss_chance"]
        )

        self.in_operation = False

        self.root_dir = config["root_dir"]
        signal.signal(signal.SIGINT,self.handle_sigint)



    def handle_sigint(self,signal,frame):
        print("RECEIVED SIGINT, QUITTING")
        self.data_manager.stop()
        sys.exit(0)


    def endOp_view_tree(self):
        if not self.in_operation:
            return
        tree_view = self.data_manager.getStorageManager().generate_tree_view(self.root_dir)
        self.data_manager.prepare_data_packets(tree_view)
        self.data_manager.send_prepared_packets()

        self.in_operation = False

    def startOp_listen(self):
        if self.in_operation:
            return
        self.in_operation = True
        self.data_manager.listen()
        headers = self.data_manager.get_custom_headers()
        for header in headers:
            print(str(header) + "\n")

        if d.Operation_Header.H_OP_ACCESS in headers:
            self.endOp_view_tree()
        else:
            print("No valid op headers found")
            self.in_operation = False

