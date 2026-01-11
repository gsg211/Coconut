from SlidingWindowProtocol import DataTransferManager as dtm
import defines as d
import json

class Server:
    def __init__(self, config:{}):
        self.data_manager = dtm.DataTransferManager(
            config["root_dir"],

            config["window_size"],
            config["packet_data_size"],

            config["sender_address"],
            config["sender_port"],

            config["destination_address"],
            config["destination_port"],

            config["time_out_interval"],
            config["packet_loss_chance"]
        )

        self.in_operation = False


        self.root_dir = config["root_dir"]


    def endOp_view_tree(self):
        if not self.in_operation:
            return
        tree_view = self.data_manager.getStorageManager().generate_tree_view(self.root_dir)

        self.data_manager.clear_sending_packet_list()
        self.data_manager.prepare_data_packets(tree_view)
        self.data_manager.prepare_operation_packet(d.Flow_Header.H_OP_SUCCESS)
        self.data_manager.send_prepared_packets()

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
        print(f"DEBUG: Server searching for: '{file_path}'")
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

    def apply_new_config(self, config_data: dict):
        dtm = self.data_manager

        if "window_size" in config_data:
            ws = config_data["window_size"]
            dtm._window_manager._sw._window_size = ws
            dtm._window_manager._rw._window_size = ws

        if "packet_data_size" in config_data:
            pds = config_data["packet_data_size"]
            dtm._window_manager._sw._packet_data_size = pds
            dtm._window_manager._rw._packet_data_size = pds

        if "time_out_interval" in config_data:
            toi = config_data["time_out_interval"]
            dtm._window_manager._sw._time_out_interval = toi
            dtm._window_manager._rw._time_out_interval = toi


        if "packet_loss_chance" in config_data:
            plc = config_data["packet_loss_chance"]
            dtm._window_manager._sw.packet_loss_chance = plc
            dtm._window_manager._rw.packet_loss_chance = plc

        try:
            with open("ServerConfig.json", "w") as f:
                json.dump(config_data, f, indent=2)
            print(f"SERVER CONFIG UPDATED AND SAVED: {config_data}")
        except Exception as e:
            print(f"Failed to write ServerConfig.json: {e}")


    def endOp_update_config(self):
        if not self.in_operation:
            return

        self.data_manager.listen()
        config_json_str = self.data_manager.get_data()

        try:
            config_data = json.loads(config_json_str)
            self.apply_new_config(config_data)

            self.data_manager.clear_sending_packet_list()
            self.data_manager.prepare_operation_packet(d.Flow_Header.H_OP_SUCCESS)
        except Exception as e:
            print(f"Failed to update config: {e}")
            self.data_manager.clear_sending_packet_list()
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
            elif d.Operation_Header.H_OP_CONFIG in headers:
                self.endOp_update_config()
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

def main():
    timeout = 0.5

    initial_config = {}

    initial_config["root_dir"] = d.SERVER_ROOT_PATH

    initial_config["window_size"] = 7
    initial_config["packet_data_size"] = 50

    initial_config["sender_address"] = d.LOCAL_HOST_ADDR_A
    initial_config["sender_port"] = d.DEFAULT_PORT_A

    initial_config["destination_address"] = d.LOCAL_HOST_ADDR_B
    initial_config["destination_port"] = d.DEFAULT_PORT_B

    initial_config["time_out_interval"] = timeout
    initial_config["packet_loss_chance"] = 0.1

    server_instance = Server(initial_config)

    while True:
        server_instance.startOp_listen()

if __name__ == "__main__":
    main()






