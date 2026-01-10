import sys
import json
import os

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import *

import defines as d
from ClientCode import Client, ClientWorker

resource_path = "../../Resources/"



def load_button_stylesheet(stylesheet:str):
    file_path = f"{resource_path}/{stylesheet}"
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error loading stylesheet: {e}"

class ConfigWindow(QWidget):
    back_requested = pyqtSignal()
    config_updated = pyqtSignal(str)

    def __init__(self, client):
        super().__init__()
        self.client = client
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("color: white; background-color: #1e2124;")
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("CONFIGURATION")
        title.setFont(QFont("Consolas", 16, QFont.Bold))
        layout.addWidget(title)


        self.config_editor = QTextEdit()
        self.config_editor.setFont(QFont("Consolas", 12))
        self.config_editor.setStyleSheet("background-color: #36393e; color: white; border: 1px solid #4f545c;")

        try:
            with open("clientConfig.json", "r") as f:
                self.config_editor.setText(f.read())
        except:
            self.config_editor.setText("{}")

        layout.addWidget(QLabel("Edit JSON directly:"))
        layout.addWidget(self.config_editor)

        btn_layout = QHBoxLayout()

        self.back_btn = QCommandLinkButton("Back")
        self.save_btn = QCommandLinkButton("Apply config")

        for btn in [self.back_btn, self.save_btn]:
            btn.setFont(QFont("Consolas", 10, QFont.Bold))
            btn.setFixedHeight(40)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(load_button_stylesheet("ButtonStyle.css"))
            btn.setIcon(QIcon(f"{resource_path}/Icons/Coconut.png"))
            btn.setIconSize(QSize(60, 60))

        self.back_btn.clicked.connect(self.back_requested.emit)
        self.save_btn.clicked.connect(self.save_config)

        btn_layout.addWidget(self.back_btn)
        btn_layout.addWidget(self.save_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def save_config(self):
        config_str = self.config_editor.toPlainText()
        try:
            config_data = json.loads(config_str)
            with open("clientConfig.json", "w") as f:
                f.write(config_str)

            self.client.apply_new_config(config_data)
            self.config_updated.emit(config_str)
            QMessageBox.information(self, "Success", "Configuration Applied.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Invalid JSON: {e}")


class ClientWindow(QWidget):
    switch_to_config = pyqtSignal()

    def __init__(self, client: Client):
        super().__init__()
        self.client = client
        self.button_style = load_button_stylesheet("ButtonStyle.css")
        self.icon_size = 40
        self.worker = None
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("color: white; background-color: #1e2124;")
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        top_container = QWidget()
        top_layout = QHBoxLayout(top_container)
        top_layout.setContentsMargins(0, 0, 0, 0)

        self.output_label = QLabel("Output:")
        self.output_label.setFont(QFont("Consolas", 12))

        self.config_btn = QPushButton()
        self.config_btn.setIcon(QIcon(f"{resource_path}/Icons/Coconut.png"))
        self.config_btn.setIconSize(QSize(60, 60))
        self.config_btn.setFixedSize(60, 60)
        self.config_btn.setStyleSheet(load_button_stylesheet("ImageBtn.css"))
        self.config_btn.setCursor(Qt.PointingHandCursor)
        self.config_btn.clicked.connect(self.switch_to_config.emit)

        top_layout.addWidget(self.output_label)
        top_layout.addStretch()
        top_layout.addWidget(self.config_btn)

        self.output_text = QTextBrowser()
        self.output_text.setFont(QFont("Consolas", 12))
        self.output_text.setStyleSheet("background-color: #36393e; color: white; border: none;")

        self.source_path_label = QLabel("Source Path:")
        self.source_path_label.setFont(QFont("Consolas", 12))
        self.source_path_text_box = QLineEdit()
        self.source_path_text_box.setStyleSheet("background-color: #36393e; color: white; padding: 5px;")
        self.source_path_text_box.setMinimumHeight(40)

        self.destination_path_label = QLabel("Destination Path:")
        self.destination_path_label.setFont(QFont("Consolas", 12))
        self.destination_path_text_box = QLineEdit()
        self.destination_path_text_box.setStyleSheet("background-color: #36393e; color: white; padding: 5px;")
        self.destination_path_text_box.setMinimumHeight(40)

        self.view_btn = self.create_button("View Tree", "Icons/view tree.png", self.view_tree)
        self.create_btn = self.create_button("Create New File", "Icons/create.png", self.create_file)
        self.delete_btn = self.create_button("Delete File", "Icons/delete.png", self.delete_file)
        self.move_btn = self.create_button("Move File", "Icons/move.png", self.move_file)
        self.download_btn = self.create_button("Download File", "Icons/download.png", self.download_file)
        self.upload_btn = self.create_button("Upload File", "Icons/upload.png", self.upload_file)

        layout.addWidget(top_container)
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
        self.source_path_text_box.clear()
        self.destination_path_text_box.clear()

    def write_result(self, result: str):
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
        self.write_result(f"ERROR: {err}")
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
        path = self.get_source_file()
        if path:
            self.run_operation("delete", path)
        else:
            self.write_result("Error: Provide path")

    def move_file(self):
        source = self.get_source_file()
        destination = self.get_destination_file()
        if not source:
            self.write_result("Error: Provide 'source'")
        elif not destination:
            self.write_result("Error: Provide 'destination'")
        else:
            self.run_operation("move", source, destination)

    def download_file(self):
        source = self.get_source_file()
        destination = self.get_destination_file()

        if not source:
            self.write_result("Error: Provide 'source'")
        elif not destination:
            self.write_result("Error: Provide 'destination'")
        else:
            self.run_operation("download", source, destination)

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
        self.config_btn.setEnabled(enabled)


class MainWindowContainer(QMainWindow):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.setWindowTitle("Client UI")
        self.setGeometry(100, 100, 800, 800)
        self.setStyleSheet("background-color: #1e2124;")

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.client_page = ClientWindow(self.client)
        self.config_page = ConfigWindow(self.client)

        self.stacked_widget.addWidget(self.client_page)
        self.stacked_widget.addWidget(self.config_page)

        self.client_page.switch_to_config.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.config_page.back_requested.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.config_page.config_updated.connect(lambda cfg: self.client_page.run_operation("update_config", cfg))


if __name__ == "__main__":
    config = {
        "root_dir": d.CLIENT_ROOT_PATH,
        "window_size": 7,
        "packet_data_size": 64,
        "sender_address": d.LOCAL_HOST_ADDR_B,
        "sender_port": d.DEFAULT_PORT_B,
        "destination_address": d.LOCAL_HOST_ADDR_A,
        "destination_port": d.DEFAULT_PORT_A,
        "time_out_interval": 0.5,
        "packet_loss_chance": 0.1
    }

    if not os.path.exists("clientConfig.json"):
        with open("clientConfig.json", "w") as f: json.dump(config, f, indent=4)

    app = QApplication(sys.argv)
    client_logic = Client(config)
    main_window = MainWindowContainer(client_logic)
    main_window.show()
    sys.exit(app.exec_())