import time

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
        self.data_manager.clear_sending_packet_list()

    def startOp_create_file(self,file_path:str):
        if self.in_operation:
            return
        self.in_operation = True

        self.data_manager.clear_sending_packet_list()
        self.data_manager.prepare_operation_packet(d.Operation_Header.H_OP_CREATE)
        self.data_manager.send_prepared_packets()

        time.sleep(0.2)

        self.data_manager.clear_sending_packet_list()
        self.data_manager.prepare_data_packets(file_path)
        self.data_manager.send_prepared_packets()


    def startOp_upload_file(self,file_path:str):
        if not self.data_manager.getStorageManager().find(file_path):
            return

        # sends filepath
        self.data_manager.clear_sending_packet_list()
        self.data_manager.prepare_data_packets(file_path)
        self.data_manager.prepare_operation_packet(d.Operation_Header.H_OP_UPLOAD)
        self.data_manager.send_prepared_packets()

        self.data_manager.clear_sending_packet_list()
        file_data = self.data_manager.getStorageManager().read(file_path)
        self.data_manager.prepare_data_packets(file_data)
        self.data_manager.prepare_operation_packet(d.Operation_Header.H_OP_UPLOAD)
        self.data_manager.send_prepared_packets()

    def startOp_download_file(self,file_path:str):
        pass

    def startOp_move_file(self, file_path: str):
        pass

    def startOp_delete_file(self, file_path: str):
        pass


    def endOp_get_data(self)->str:
        if not self.in_operation:
            return ""
        self.data_manager.listen()
        data = self.data_manager.get_data()
        self.in_operation = False

        headers = self.data_manager.get_custom_headers()
        while True:
            if d.Flow_Header.H_OP_SUCCESS in headers:
                print("OPERATION SUCCESS")
                break
            elif d.Flow_Header.H_OP_FAILED in headers:
                print("OPERATION FAILED")
                break
            else:
                print(headers)
                self.data_manager.listen()
                headers = self.data_manager.get_custom_headers()

        return data



