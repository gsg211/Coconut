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

        self.data_manager.clear_sending_packet_list()
        self.data_manager.prepare_data_packets(tree_view)
        self.data_manager.prepare_operation_packet(d.Flow_Header.H_OP_SUCCESS)
        self.data_manager.send_prepared_packets()

        # self.data_manager.clear_sending_packet_list()
        # self.data_manager.prepare_operation_packet(d.Flow_Header.H_OP_SUCCESS)
        # self.data_manager.send_prepared_packets()


        self.in_operation = False

    def endOp_create_file(self):
        if not self.in_operation:
            return
        self.data_manager.listen()
        file_path = self.data_manager.get_data()
        success = self.data_manager.getStorageManager().create_file(file_path)
        self.data_manager.clear_sending_packet_list()
        if success:
            self.data_manager.prepare_operation_packet(d.Flow_Header.H_OP_SUCCESS)
        else:
            self.data_manager.prepare_operation_packet(d.Flow_Header.H_OP_FAILED)
        self.data_manager.send_prepared_packets()

        self.in_operation = False

    def endOp_delete_file(self):
        if not self.in_operation:
            return

        # waiting for path
        self.data_manager.listen()
        file_path = self.data_manager.get_data()
        success = self.data_manager.getStorageManager().remove_file(file_path)
        self.data_manager.clear_sending_packet_list()

        if success:
            self.data_manager.prepare_operation_packet(d.Flow_Header.H_OP_SUCCESS)
        else:
            self.data_manager.prepare_operation_packet(d.Flow_Header.H_OP_FAILED)

        self.data_manager.send_prepared_packets()


        self.in_operation = False


    def endOp_move_file(self):
        if not self.in_operation:
            return
        op_failed = False

        self.data_manager.listen()
        combined = self.data_manager.get_data()

        if "|" not in combined:
            self.send_response(False)  # Helper to send H_OP_FAILED
            return

        src_path, dst_path = combined.split("|")
        src_path, dst_path = src_path.strip(), dst_path.strip()

        storage = self.data_manager.getStorageManager()
        op_success = False

        if storage.find(src_path):
            data = storage.read(src_path)
            if storage.write(dst_path, data):
                storage.remove_file(src_path)
                op_success = True

        self.data_manager.clear_sending_packet_list()
        header = d.Flow_Header.H_OP_SUCCESS if op_success else d.Flow_Header.H_OP_FAILED
        self.data_manager.prepare_operation_packet(header)
        self.data_manager.send_prepared_packets()
        self.in_operation = False


    def endOp_download_file(self):
        if not self.in_operation:
            return

        self.data_manager.listen()
        file_path = self.data_manager.get_data()
        file_found = self.data_manager.getStorageManager().find(file_path)
        if not file_found:
            self.data_manager.clear_sending_packet_list()
            self.data_manager.prepare_operation_packet(d.Flow_Header.H_OP_FAILED)
            self.data_manager.send_prepared_packets()
            self.in_operation = False
            return

        file_data = self.data_manager.getStorageManager().read(file_path)
        self.data_manager.clear_sending_packet_list()
        self.data_manager.prepare_data_packets(file_data)
        self.data_manager.prepare_operation_packet(d.Flow_Header.H_OP_SUCCESS)
        self.data_manager.send_prepared_packets()

        self.in_operation = False

    def endOp_upload_file(self):
        if not self.in_operation:
            return

        # path
        self.data_manager.listen()
        file_path = self.data_manager.get_data()

        # content
        self.data_manager.listen()
        file_content = self.data_manager.get_data()

        success = self.data_manager.getStorageManager().write(file_path,file_content)

        self.data_manager.clear_sending_packet_list()
        if success:
            self.data_manager.prepare_operation_packet(d.Flow_Header.H_OP_SUCCESS)
        else:
            self.data_manager.prepare_operation_packet(d.Flow_Header.H_OP_FAILED)
        self.data_manager.send_prepared_packets()

        self.in_operation = False



    def startOp_listen(self):
        if self.in_operation:
            return
        self.in_operation = True

        while True:
            self.data_manager.listen()
            headers = self.data_manager.get_custom_headers()

            if d.Operation_Header.H_OP_ACCESS in headers:
                self.endOp_view_tree()
                break
            elif d.Operation_Header.H_OP_CREATE in headers:
                self.endOp_create_file()
                break
            elif d.Operation_Header.H_OP_DELETE in headers:
                self.endOp_delete_file()
                break
            elif d.Operation_Header.H_OP_MOVE in headers:
                self.endOp_move_file()
                break
            elif d.Operation_Header.H_OP_DOWNLOAD in headers:
                self.endOp_download_file()
                break
            elif d.Operation_Header.H_OP_UPLOAD in headers:
                self.endOp_upload_file()
                break
            else:
                if not headers:
                    self.in_operation = False
                    break
                continue

if __name__ == "__main__":
    timeout = 0.2

    config = {}

    config["root_dir"] = d.SERVER_ROOT_PATH

    config["window_size"] = 2
    config["packet_data_size"] = 5

    config["sender_address"] = d.LOCAL_HOST_ADDR_A  # here the client - B is the sender and the server - A is the destination
    config["sender_port"] = d.DEFAULT_PORT_A

    config["destination_address"] = d.LOCAL_HOST_ADDR_B
    config["destination_port"] = d.DEFAULT_PORT_B

    config["time_out_interval"] = timeout
    config["packet_loss_chance"] = 0

    server_instance = Server(config)

    while True:
        server_instance.startOp_listen()






