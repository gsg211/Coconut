from ClientCode import Client
import sys
import defines as d
from PyQt5.QtCore import Qt,QSize
from PyQt5.QtGui import QIcon,QColor
from PyQt5.QtWidgets import *

resource_path= "../../Resources/"



def load_button_stylesheet():
    file_path = f"{resource_path}/ButtonStyle.css"

    try:
        with open(file_path, 'r') as f:
            stylesheet = f.read()
        return stylesheet
    except FileNotFoundError:
        return f"File {file_path} not found."
    except Exception as e:
        return f"Error: {e}"



def view_tree(client_instance: Client):
        client_instance.startOp_view_tree()
        data = client_instance.endOp_get_data()
        print(data)
def create(client_instance: Client):
    print("SELECTED CREATE")
    client_instance.startOp_create_file("testDir/G/3456/testFile234")
    data = client_instance.endOp_get_data()
    print(data)

def delete(client_instance: Client):
    print("SELECTED DELETE")
    client_instance.startOp_delete_file("TestFile.txt")
    data = client_instance.endOp_get_data()
    print(data)

def move(client_instance: Client):
    print("SELECTED MOVE")
    client_instance.startOp_move_file("testDir/G/testFile","TestMove/testFile")
    data = client_instance.endOp_get_data()
    print(data)

def download(client_instance: Client):
    print("SELECTED DOWNLOAD")
    client_instance.startOp_download_file("TestMove/testFile")
    data = client_instance.endOp_get_data()
    print(data)

def upload(client_instance: Client):
    print("UPLOAD")
    client_instance.startOp_upload_file("TestUpload/testFile.txt","TestUpload/Test2/testFile.txt")
    data = client_instance.endOp_get_data()
    print(data)



if __name__ == '__main__':


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

    client = Client(config)

    # backround:#1a1a1e
    # text: #222327

    button_style=load_button_stylesheet()
    icon_size = 40

    app = QApplication(sys.argv)
    window = QWidget()
    palette = window.palette()
    palette.setColor(window.backgroundRole(), QColor("ds"))
    window.setPalette(palette)

    window.setStyleSheet("color: white; background-color: #1e2124;")

    window.setWindowTitle('Client UI')
    window.setGeometry(100, 100, 800, 700)


    quote_text = QLabel("Hello")
    quote = QLabel()
    text_field = QTextEdit()

    text_field.setStyleSheet("background-color: #36393e; color: white;")


    acces_btn = QCommandLinkButton("View Tree")
    acces_btn.clicked.connect(lambda: view_tree(client))
    acces_btn.setStyleSheet(button_style)
    acces_btn.setIcon(QIcon(f"{resource_path}/Icons/view tree.png"))
    acces_btn.setIconSize(QSize(icon_size,icon_size))

    create_btn = QCommandLinkButton("Create New File")
    create_btn.clicked.connect(lambda: create(client))
    create_btn.setStyleSheet(button_style)
    create_btn.setIcon(QIcon(f"{resource_path}/Icons/create.png"))
    create_btn.setIconSize(QSize(icon_size,icon_size))

    delete_btn = QCommandLinkButton("Delete file")
    delete_btn.clicked.connect(lambda: delete(client))
    delete_btn.setStyleSheet(button_style)
    delete_btn.setIcon(QIcon(f"{resource_path}/Icons/delete.png"))
    delete_btn.setIconSize(QSize(icon_size,icon_size))
    delete_btn.setIconSize(QSize(icon_size,icon_size))

    move_btn = QCommandLinkButton("Move File")
    move_btn.clicked.connect(lambda: move(client))
    move_btn.setStyleSheet(button_style)
    move_btn.setIcon(QIcon(f"{resource_path}/Icons/move.png"))
    move_btn.setIconSize(QSize(icon_size,icon_size))

    upload_btn = QCommandLinkButton("Upload File")
    upload_btn.clicked.connect(lambda: upload(client))
    upload_btn.setStyleSheet(button_style)
    upload_btn.setIcon(QIcon(f"{resource_path}/Icons/upload.png"))
    upload_btn.setIconSize(QSize(icon_size,icon_size))

    download_btn = QCommandLinkButton("Download File")
    download_btn.clicked.connect(lambda: download(client))
    download_btn.setStyleSheet(button_style)
    download_btn.setIcon(QIcon(f"{resource_path}/Icons/download.png"))
    download_btn.setIconSize(QSize(icon_size,icon_size))

    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignTop)

    layout.addWidget(quote_text)
    layout.addWidget(text_field)
    layout.addWidget(acces_btn)
    layout.addWidget(create_btn)
    layout.addWidget(delete_btn)
    layout.addWidget(move_btn)
    layout.addWidget(download_btn)
    layout.addWidget(upload_btn)

    window.setLayout(layout)
    window.show()
    sys.exit(app.exec_())

