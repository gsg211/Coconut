from SlidingWindowProtocol import DataTransferManager as dtm
import defines as d
import signal
import sys

class Client:
    def __init__(self, config:{}):
        self.data_manager = dtm.DataTransferManager(
            config["root_dir"],

            config["window_size"],
            config["packet_data_size"],

            config["sender_address"], # here the client - A is the sender and the server - B is the destination
            config["sender_port"],

            config["destination_address"],
            config["destination_port"],

            config["time_out_interval"],
            config["packet_loss_chance"]
        )

        self.in_operation = False
        signal.signal(signal.SIGINT,self.handle_sigint)

    def handle_sigint(self, signal, frame):
        print("RECEIVED SIGINT, QUITTING")
        self.stop()
        sys.exit(0)

    def stop(self):
        self.data_manager.stop()

    def startOp_view_tree(self):
        if self.in_operation:
            return
        self.in_operation = True
        self.data_manager.prepare_operation_packet(d.Operation_Header.H_OP_ACCESS)
        self.data_manager.send_prepared_packets()

    def endOp_get_data(self)->str:
        if not self.in_operation:
            return ""
        self.data_manager.listen()
        data = self.data_manager.get_data()
        self.in_operation = False
        return data



