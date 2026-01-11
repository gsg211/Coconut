from PyQt5.QtCore import QThread, pyqtSignal

from SlidingWindowProtocol import DataTransferManager as dtm
import defines as d


class Client:
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

    def startOp_update_config(self, config_json_str: str):
        if self.in_operation:
            return
        self.in_operation = True
        self.data_manager.clear_receiving_queue()

        self.data_manager.clear_sending_packet_list()
        self.data_manager.prepare_operation_packet(d.Operation_Header.H_OP_CONFIG)
        self.data_manager.send_prepared_packets()

        self.data_manager.clear_sending_packet_list()
        self.data_manager.prepare_data_packets(config_json_str)
        self.data_manager.send_prepared_packets()

    def apply_new_config(self, config_data: dict):
        dtm = self.data_manager
        sw = dtm._window_manager._sw
        rw = dtm._window_manager._rw

        if "window_size" in config_data:
            ws = config_data["window_size"]
            sw._window_size = ws
            rw._window_size = ws

        if "packet_data_size" in config_data:
            pds = config_data["packet_data_size"]
            sw._packet_data_size = pds
            rw._packet_data_size = pds

        if "time_out_interval" in config_data:
            toi = config_data["time_out_interval"]
            sw._time_out_interval = toi
            # Usually only sender needs timeout, but good for consistency
            rw._time_out_interval = toi

        if "packet_loss_chance" in config_data:  # Fixed: was 'config' (missing _data)
            plc = config_data["packet_loss_chance"]
            sw._packet_loss_chance = plc  # Fixed: was setting _time_out_interval
            rw._packet_loss_chance = plc

    def stop(self):
        self.data_manager.stop()

    def startOp_view_tree(self):
        if self.in_operation:
            return
        self.in_operation = True
        self.data_manager.clear_receiving_queue()

        self.data_manager.clear_sending_packet_list()
        self.data_manager.prepare_operation_packet(d.Operation_Header.H_OP_ACCESS)
        self.data_manager.send_prepared_packets()

    def startOp_create_file(self,file_path:str):
        if self.in_operation:
            return
        self.in_operation = True
        self.data_manager.clear_receiving_queue()

        self.data_manager.clear_sending_packet_list()
        self.data_manager.prepare_operation_packet(d.Operation_Header.H_OP_CREATE)
        self.data_manager.send_prepared_packets()

        self.data_manager.clear_sending_packet_list()
        self.data_manager.prepare_data_packets(file_path)
        self.data_manager.send_prepared_packets()


    def startOp_upload_file(self,src_path:str, dst_path:str):
        if self.in_operation:
            return
        self.in_operation = True
        if not self.data_manager.getStorageManager().find(src_path):
            return
        self.data_manager.clear_receiving_queue()

        # sends header
        self.data_manager.clear_sending_packet_list()
        self.data_manager.prepare_operation_packet(d.Operation_Header.H_OP_UPLOAD)
        self.data_manager.send_prepared_packets()
        # consumed in server -- startOp listen

        # sends dst path
        self.data_manager.clear_sending_packet_list()
        self.data_manager.prepare_data_packets(dst_path)
        self.data_manager.send_prepared_packets()
        # consumed by first opListen in server

        # sends content
        file_data = self.data_manager.getStorageManager().read(src_path)

        self.data_manager.clear_sending_packet_list()
        self.data_manager.prepare_data_packets(file_data)
        self.data_manager.send_prepared_packets()
        # consumed by second listen in server

    def startOp_download_file(self,file_path:str):
        if self.in_operation:
            return ""
        self.in_operation = True
        self.data_manager.clear_receiving_queue()

        self.data_manager.clear_sending_packet_list()
        self.data_manager.prepare_operation_packet(d.Operation_Header.H_OP_DOWNLOAD)
        self.data_manager.send_prepared_packets()

        self.data_manager.clear_sending_packet_list()
        self.data_manager.prepare_data_packets(file_path)
        self.data_manager.send_prepared_packets()


    def startOp_move_file(self, src_path:str, dst_path:str):
        if self.in_operation:
            return ""
        self.in_operation = True
        self.data_manager.clear_receiving_queue()

        self.data_manager.clear_sending_packet_list()
        self.data_manager.prepare_operation_packet(d.Operation_Header.H_OP_MOVE)
        self.data_manager.send_prepared_packets()

        combined_paths = f"{src_path.strip()}|{dst_path.strip()}"
        self.data_manager.clear_sending_packet_list()
        self.data_manager.prepare_data_packets(combined_paths)
        self.data_manager.send_prepared_packets()


    def startOp_delete_file(self, file_path: str):
        if self.in_operation:
            return ""
        self.in_operation = True
        self.data_manager.clear_receiving_queue()

        self.data_manager.clear_sending_packet_list()
        self.data_manager.prepare_operation_packet(d.Operation_Header.H_OP_DELETE)
        self.data_manager.send_prepared_packets()

        self.data_manager.clear_sending_packet_list()
        self.data_manager.prepare_data_packets(file_path)
        self.data_manager.send_prepared_packets()

    def endOp_get_data(self) -> str:
        if not self.in_operation:
            return ""

        chunks = []
        while True:
            self.data_manager.listen()

            headers = self.data_manager.get_custom_headers()
            chunk = self.data_manager.get_data()

            if chunk:
                chunks.append(chunk)

            if d.Flow_Header.H_OP_SUCCESS in headers:
                print("OPERATION SUCCESS")
                break
            elif d.Flow_Header.H_OP_FAILED in headers:
                print("OPERATION FAILED")
                break

        self.in_operation = False
        self.data_manager.clear_receiving_queue()
        self.data_manager.clear_sending_packet_list()
        return "".join(chunks)

    def get_data_manager(self) -> dtm.DataTransferManager:
        return self.data_manager


class ClientWorker(QThread):
    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, client, op_name, *args):
        super().__init__()
        self.client = client
        self.op_name = op_name
        self.args = args

    def run(self):
        try:
            if self.op_name == "view":
                self.client.startOp_view_tree()
            elif self.op_name == "create":
                self.client.startOp_create_file(*self.args)
            elif self.op_name == "delete":
                self.client.startOp_delete_file(*self.args)
            elif self.op_name == "move":
                self.client.startOp_move_file(*self.args)
            elif self.op_name == "download":
                self.client.startOp_download_file(self.args[0])
            elif self.op_name == "update_config":
                self.client.startOp_update_config(*self.args)
            elif self.op_name == "upload":
                self.client.startOp_upload_file(*self.args)

            data = self.client.endOp_get_data()

            if self.op_name == "download":
                self.client.get_data_manager().getStorageManager().write(self.args[1], data)
                result_message = f"SUCCESS: File downloaded to {self.args[1]}"
                self.result_ready.emit(result_message)
            else:
                self.result_ready.emit(data)

        except Exception as e:
            self.error_occurred.emit(str(e))


if __name__ == "__main__":
    config = {}

    config["root_dir"] = d.CLIENT_ROOT_PATH

    config["window_size"] = 2
    config["packet_data_size"] = 5

    config["sender_address"] = d.LOCAL_HOST_ADDR_B
    config["sender_port"] = d.DEFAULT_PORT_B

    config["destination_address"] = d.LOCAL_HOST_ADDR_A
    config["destination_port"] = d.DEFAULT_PORT_A

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

        opt = int(input('>>'))

        if opt == 0:
            break
        elif opt == 1:

            client_instance.startOp_view_tree()
            data = client_instance.endOp_get_data()
            print(data)

        elif opt == 2:
            print("SELECTED CREATE")
            client_instance.startOp_create_file("testDir/G/3456/testFile234")
            data = client_instance.endOp_get_data()
            print(data)

        elif opt == 3:
            print("SELECTED DELETE")
            client_instance.startOp_delete_file("TestFile.txt")
            data = client_instance.endOp_get_data()
            print(data)

            pass
        elif opt == 4:
            print("SELECTED MOVE")
            client_instance.startOp_move_file("testDir/G/testFile","TestMove/testFile")
            data = client_instance.endOp_get_data()
            print(data)
            pass
        elif opt == 5:
            print("SELECTED DOWNLOAD")
            client_instance.startOp_download_file("TestMove/testFile")
            data = client_instance.endOp_get_data()
            print(data)

            pass
        elif opt == 6:
            print("UPLOAD")
            client_instance.startOp_upload_file("TestUpload/testFile.txt","TestUpload/Test2/testFile.txt")
            data = client_instance.endOp_get_data()
            pass
        else:
            print("Invalid option, pick again")

    client_instance.stop()


