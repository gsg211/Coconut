import sys
from ClientCode import Client
import defines as d

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QColor, QFont
from PyQt5.QtWidgets import *

resource_path = "../../Resources/"


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
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Client UI")
        self.setGeometry(100, 100, 800, 700)
        self.setStyleSheet("color: white; background-color: #1e2124;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)


        self.output_label = QLabel("Output:")
        self.output_label.setFont(QFont("Arial", 12))

        self.output_text = QTextBrowser()
        self.output_text.setFont(QFont("Arial", 12))
        self.output_text.setStyleSheet("background-color: #36393e; color: white;")


        self.file_path_label = QLabel("Enter file path here:")
        self.file_path_label.setFont(QFont("Arial", 12))

        self.file_path_text_box = QLineEdit()
        self.file_path_text_box.setMinimumHeight(50)
        self.file_path_text_box.setFont(QFont("Arial", 12))
        self.file_path_text_box.setStyleSheet("background-color: #36393e; color: white;" )


        self.view_btn = self.create_button("View Tree", "Icons/view tree.png", self.view_tree)
        self.create_btn = self.create_button("Create New File", "Icons/create.png", self.create_file)
        self.delete_btn = self.create_button("Delete File", "Icons/delete.png", self.delete_file)
        self.move_btn = self.create_button("Move File", "Icons/move.png", self.move_file )
        self.download_btn = self.create_button("Download File", "Icons/download.png", self.download_file)
        self.upload_btn = self.create_button("Upload File", "Icons/upload.png", self.upload_file)


        layout.addWidget(self.output_label)
        layout.addWidget(self.output_text)
        layout.addWidget(self.file_path_label)
        layout.addWidget(self.file_path_text_box)
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

    def get_file_path(self) -> str:
        return self.file_path_text_box.text()

    def write_result(self, result: str):
        self.output_text.clear()
        self.output_text.setText(result)


    def view_tree(self):
        self.client.startOp_view_tree()
        data = self.client.endOp_get_data()
        self.write_result(data)

    def create_file(self):
        self.client.startOp_create_file(self.get_file_path())
        data = self.client.endOp_get_data()
        self.write_result(data)

    def delete_file(self):
        self.client.startOp_delete_file(self.get_file_path())
        data = self.client.endOp_get_data()
        self.write_result(data)

    def move_file(self):
        filepaths = self.get_file_path().split(" ")
        self.client.startOp_move_file(filepaths[0], filepaths[1])
        data = self.client.endOp_get_data()
        self.write_result(data)

    def download_file(self):
        self.client.startOp_download_file(self.get_file_path())
        data = self.client.endOp_get_data()
        self.write_result(data)

    def upload_file(self):
        filepaths = self.get_file_path().split(" ")
        self.client.startOp_upload_file(filepaths[0],filepaths[1])
        data = self.client.endOp_get_data()
        self.write_result(data)




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
