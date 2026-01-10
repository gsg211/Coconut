import json
import os

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import *

def get_resource_path() -> str:
    return  "../../Resources/"




def load_stylesheet(stylesheet:str):
    file_path = f"{get_resource_path() }/{stylesheet}"
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
        self.full_config = {}
        self.init_ui()
        self.load_config_into_ui()

    def init_ui(self):
        self.setStyleSheet("color: white; background-color: #1e2124;")
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("CONFIGURATION")
        title.setFont(QFont("Consolas", 18, QFont.Bold))
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        text_box_style = load_stylesheet("TextBox.css")


        self.edit_window_size = QLineEdit()
        self.edit_window_size.setStyleSheet(text_box_style)
        form_layout.addRow(self.create_label("Window Size:"), self.edit_window_size)

        # 2. Packet Data Size
        self.edit_packet_size = QLineEdit()
        self.edit_packet_size.setStyleSheet(text_box_style)
        form_layout.addRow(self.create_label("Packet Data Size:"), self.edit_packet_size)

        self.edit_timeout = QLineEdit()
        self.edit_timeout.setStyleSheet(text_box_style)
        form_layout.addRow(self.create_label("Timeout Interval (s):"), self.edit_timeout)


        self.edit_loss_chance = QLineEdit()
        self.edit_loss_chance.setStyleSheet(text_box_style)
        form_layout.addRow(self.create_label("Packet Loss Chance:"), self.edit_loss_chance)

        layout.addLayout(form_layout)
        layout.addStretch()

        btn_layout = QHBoxLayout()
        self.back_btn = QCommandLinkButton("Back")
        self.save_btn = QCommandLinkButton("Apply Config")

        for btn in [self.back_btn, self.save_btn]:
            btn.setFont(QFont("Consolas", 12, QFont.Bold))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setIcon(QIcon(f"{get_resource_path()}/Icons/Coconut.png"))
            btn.setIconSize(QSize(60, 60))
            btn.setStyleSheet(load_stylesheet("ButtonStyle.css"))

        self.back_btn.clicked.connect(self.back_requested.emit)
        self.save_btn.clicked.connect(self.save_config)

        btn_layout.addWidget(self.back_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def create_label(self, text):
        lbl = QLabel(text)
        lbl.setFont(QFont("Consolas", 12))
        return lbl

    def load_config_into_ui(self):
        if os.path.exists("clientConfig.json"):
            try:
                with open("clientConfig.json", "r") as f:
                    self.full_config = json.load(f)

                self.edit_window_size.setText(str(self.full_config.get("window_size", 16)))
                self.edit_packet_size.setText(str(self.full_config.get("packet_data_size", 50)))
                self.edit_timeout.setText(str(self.full_config.get("time_out_interval", 0.5)))
                self.edit_loss_chance.setText(str(self.full_config.get("packet_loss_chance", 0.1)))
            except:
                pass

    def save_config(self):
        try:
            self.full_config["window_size"] = int(self.edit_window_size.text().strip())
            self.full_config["packet_data_size"] = int(self.edit_packet_size.text().strip())
            self.full_config["time_out_interval"] = float(self.edit_timeout.text().strip())
            self.full_config["packet_loss_chance"] = float(self.edit_loss_chance.text().strip())

            config_str = json.dumps(self.full_config, indent=4)
            with open("clientConfig.json", "w") as f:
                f.write(config_str)

            self.client.apply_new_config(self.full_config)
            self.config_updated.emit(config_str)
            QMessageBox.information(self, "Success", "Configuration Applied.")
        except ValueError:
            QMessageBox.critical(self, "Error", "Invalid input! Please enter numbers only.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))