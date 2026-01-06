import sys
from ClientCode import Client
import defines as d
from PyQt5.QtCore import QThread, pyqtSignal

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QColor, QFont
from PyQt5.QtWidgets import *

resource_path = "../../Resources/"




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
                self.client.startOp_download_file(*self.args)
            elif self.op_name == "upload":
                self.client.startOp_upload_file(*self.args)

            data = self.client.endOp_get_data()


            self.result_ready.emit(data)
        except Exception as e:
            self.error_occurred.emit(str(e))




def load_button_stylesheet():
    file_path = f"{resource_path}/ButtonStyle.css"
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error loading stylesheet: {e}"


class ClientWindow(QWidget):
    def __init__(self, client: Client):
        super().__init__()
        self.client = client
        self.button_style = load_button_stylesheet()
        self.icon_size = 40
        self.worker = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Client UI")
        self.setGeometry(100, 100, 800, 700)
        self.setStyleSheet("color: white; background-color: #1e2124;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        self.output_label = QLabel("Output:")
        self.output_label.setFont(QFont("Consolas", 12))

        self.output_text = QTextBrowser()
        self.output_text.setFont(QFont("Consolas", 12))
        self.output_text.setStyleSheet("background-color: #36393e; color: white;")

        self.source_path_label = QLabel("Source Path:")
        self.source_path_label.setFont(QFont("Consolas", 12))

        self.destination_path_label = QLabel("Destination Path:")
        self.destination_path_label.setFont(QFont("Consolas", 12))

        self.source_path_text_box = QLineEdit()
        self.source_path_text_box.setMinimumHeight(50)
        self.source_path_text_box.setFont(QFont("Consolas", 12))
        self.source_path_text_box.setStyleSheet("background-color: #36393e; color: white;")

        self.destination_path_text_box = QLineEdit()
        self.destination_path_text_box.setMinimumHeight(50)
        self.destination_path_text_box.setFont(QFont("Consolas", 12))
        self.destination_path_text_box.setStyleSheet("background-color: #36393e; color: white;")

        # Buttons
        self.view_btn = self.create_button("View Tree", "Icons/view tree.png", self.view_tree)
        self.create_btn = self.create_button("Create New File", "Icons/create.png", self.create_file)
        self.delete_btn = self.create_button("Delete File", "Icons/delete.png", self.delete_file)
        self.move_btn = self.create_button("Move File", "Icons/move.png", self.move_file)
        self.download_btn = self.create_button("Download File", "Icons/download.png", self.download_file)
        self.upload_btn = self.create_button("Upload File", "Icons/upload.png", self.upload_file)

        layout.addWidget(self.output_label)
        layout.addWidget(self.output_text)
        layout.addWidget(self.source_path_label)
        layout.addWidget(self.source_path_text_box)
        layout.addWidget(self.destination_path_label)
        layout.addWidget(self.destination_path_text_box)
        layout.addWidget(self.view_btn)
        layout.addWidget(self.create_btn)
        layout.addWidget(self.delete_btn)
        layout.addWidget(self.move_btn)
        layout.addWidget(self.download_btn)
        layout.addWidget(self.upload_btn)

        self.setLayout(layout)

    def create_button(self, text, icon_path, callback):
        btn = QCommandLinkButton(text)
        btn.setStyleSheet(self.button_style)
        btn.setIcon(QIcon(f"{resource_path}/{icon_path}"))
        btn.setIconSize(QSize(self.icon_size, self.icon_size))
        btn.clicked.connect(callback)
        return btn

    def get_source_file(self) -> str:
        return self.source_path_text_box.text().strip()

    def get_destination_file(self) -> str:
        return self.destination_path_text_box.text().strip()

    def clear_file_paths(self):
        # FIXED: Removed recursive call
        self.source_path_text_box.clear()
        self.destination_path_text_box.clear()

    def write_result(self, result: str):
        # Combined logic and cleared input fields
        self.output_text.setText(result)
        self.clear_file_paths()

    def run_operation(self, op_name, *args):
        self.write_result(f"Executing {op_name.upper()}... please wait.")
        self.set_ui_enabled(False)

        self.worker = ClientWorker(self.client, op_name, *args)
        self.worker.result_ready.connect(self.on_operation_success)
        self.worker.error_occurred.connect(self.on_operation_error)
        self.worker.start()

    def on_operation_success(self, data):
        self.write_result(data)
        self.set_ui_enabled(True)

    def on_operation_error(self, err):
        self.write_result(f"CRITICAL ERROR: {err}")
        self.set_ui_enabled(True)

    def view_tree(self):
        self.run_operation("view")

    def create_file(self):
        path = self.get_source_file()
        if path:
            self.run_operation("create", path)
        else:
            self.write_result("Error: Provide path")

    def delete_file(self):
        path = self.get_source_file() # FIXED typo
        if path:
            self.run_operation("delete", path)
        else:
            self.write_result("Error: Provide path")

    def move_file(self):
        source = self.get_source_file()
        destination = self.get_destination_file()
        # FIXED: Check for empty strings
        if not source:
            self.write_result("Error: Provide 'source'")
        elif not destination:
            self.write_result("Error: Provide 'destination'")
        else:
            self.run_operation("move", source, destination)

    def download_file(self):
        path = self.get_source_file() # FIXED typo
        if path:
            self.run_operation("download", path)

    def upload_file(self):
        source = self.get_source_file()
        destination = self.get_destination_file()
        if not source or not destination:
            self.write_result("Error: Provide both source and destination")
        else:
            self.run_operation("upload", source, destination)

    def set_ui_enabled(self, enabled: bool):
        self.view_btn.setEnabled(enabled)
        self.create_btn.setEnabled(enabled)
        self.delete_btn.setEnabled(enabled)
        self.move_btn.setEnabled(enabled)
        self.download_btn.setEnabled(enabled)
        self.upload_btn.setEnabled(enabled)
        self.source_path_text_box.setEnabled(enabled)
        self.destination_path_text_box.setEnabled(enabled)




if __name__ == "__main__":
    config = {
        "root_dir": d.CLIENT_ROOT_PATH,
        "window_size": 2,
        "packet_data_size": 5,
        "sender_address": d.LOCAL_HOST_ADDR_B,
        "sender_port": d.DEFAULT_PORT_B,
        "destination_address": d.LOCAL_HOST_ADDR_A,
        "destination_port": d.DEFAULT_PORT_A,
        "time_out_interval": 0.3,
        "packet_loss_chance": 0,
    }

    client = Client(config)

    app = QApplication(sys.argv)
    window = ClientWindow(client)
    window.show()
    sys.exit(app.exec_())
