from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QFileDialog
import asyncio

from client import Client
from server import Server

# User interface generated using Qt Designer
class ui_main_window(object):
    def __init__(self):
        self.central = None
        self.grid_layout = None
        self.tabs = None
        self.client_tab = None
        self.client_grid_layout = None
        self.client_grid = None
        self.address_grid = None
        self.client_port_label = None
        self.client_host_edit = None
        self.client_port_edit = None
        self.client_host_label = None
        self.upload_button = None
        self.server_tab = None
        self.server_grid_layout = None
        self.server_grid = None
        self.dropbox_grid = None
        self.server_button = None
        self.server_port_edit = None
        self.dropbox_label = None
        self.dropbox_edit = None
        self.dropbox_button = None
        self.server_port_label = None
        self.logs = None
        self.logs_model = None
        self.internal_logs = []
        self.server = Server(self)

    def select_uploads(self):
        host = self.client_host_edit.text()
        port = self.client_port_edit.text()

        if not host or not port:
            self.error("You must specify a host and port for uploading.")
            return

        try:
            int(port)
        except ValueError:
            self.error("You must specify a valid port for uploading.")
            return

        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            main_window,
            "Select files to upload",
            "",
            "All Files (*.*)"
        )

        if not files:
            self.warn("No files selected")
            return

        self.log(f"Selected {len(files)} file(s)")
        self.log("Launching file transfer client...")
        asyncio.run(self.launch_upload_client(host, port, files))

    def select_dropbox_directory(self):
        directory = QFileDialog.getExistingDirectory(
            main_window,
            "Select Dropbox Directory",
            "",
            QtWidgets.QFileDialog.Option.ShowDirsOnly
        )
        self.dropbox_edit.setText(directory)

    async def launch_upload_client(self, host, port, files):
        client = Client(self, host, port)
        client.send_files(files)

    def toggle_server(self):
        if self.server.running:
            self.log("Stopping server...")
            self.server.stop()
            self.log("Stopped server")
        else:
            port = self.server_port_edit.text()
            dropbox = self.dropbox_edit.text()

            if not port or not dropbox:
                self.error("You must specify a dropbox directory and port for listening.")
                return

            try:
                int(port)
            except ValueError:
                self.error("You must specify a valid port for listening.")
                return

            self.server.set_port(port)
            self.server.set_dropbox(dropbox)
            self.log(f"Starting server at port: {port} with dropbox: {dropbox}")
            self.server.start()
            self.log("Server started")

    def setup_ui(self, main_window):
        main_window.setObjectName("main_window")
        main_window.resize(740, 985)
        self.central = QtWidgets.QWidget(parent=main_window)
        self.central.setObjectName("central")
        self.grid_layout = QtWidgets.QGridLayout(self.central)
        self.grid_layout.setObjectName("gridLayout")
        self.tabs = QtWidgets.QTabWidget(parent=self.central)
        self.tabs.setMaximumSize(QtCore.QSize(300, 16777215))
        self.tabs.setObjectName("tabs")
        self.client_tab = QtWidgets.QWidget()
        self.client_tab.setObjectName("client_tab")
        self.client_grid_layout = QtWidgets.QWidget(parent=self.client_tab)
        self.client_grid_layout.setGeometry(QtCore.QRect(0, 0, 291, 81))
        self.client_grid_layout.setObjectName("client_grid_layout")
        self.client_grid = QtWidgets.QGridLayout(self.client_grid_layout)
        self.client_grid.setContentsMargins(0, 0, 0, 0)
        self.client_grid.setObjectName("client_grid")
        self.address_grid = QtWidgets.QGridLayout()
        self.address_grid.setObjectName("address_grid")
        self.client_port_label = QtWidgets.QLabel(parent=self.client_grid_layout)
        self.client_port_label.setObjectName("client_port_label")
        self.address_grid.addWidget(self.client_port_label, 1, 2, 1, 1)
        self.client_host_edit = QtWidgets.QLineEdit(parent=self.client_grid_layout)
        self.client_host_edit.setObjectName("client_host_edit")
        self.address_grid.addWidget(self.client_host_edit, 0, 1, 1, 1)
        self.client_port_edit = QtWidgets.QLineEdit(parent=self.client_grid_layout)
        self.client_port_edit.setObjectName("client_port_edit")
        self.address_grid.addWidget(self.client_port_edit, 0, 2, 1, 1)
        self.client_host_label = QtWidgets.QLabel(parent=self.client_grid_layout)
        self.client_host_label.setObjectName("client_host_label")
        self.address_grid.addWidget(self.client_host_label, 1, 1, 1, 1)
        self.client_grid.addLayout(self.address_grid, 0, 0, 1, 1)
        self.upload_button = QtWidgets.QPushButton(parent=self.client_grid_layout)
        self.upload_button.setObjectName("upload_button")
        self.client_grid.addWidget(self.upload_button, 1, 0, 1, 1)
        self.tabs.addTab(self.client_tab, "")
        self.server_tab = QtWidgets.QWidget()
        self.server_tab.setObjectName("server_tab")
        self.server_grid_layout = QtWidgets.QWidget(parent=self.server_tab)
        self.server_grid_layout.setGeometry(QtCore.QRect(0, 0, 291, 101))
        self.server_grid_layout.setObjectName("server_grid_layout")
        self.server_grid = QtWidgets.QGridLayout(self.server_grid_layout)
        self.server_grid.setContentsMargins(0, 0, 0, 0)
        self.server_grid.setObjectName("server_grid")
        self.dropbox_grid = QtWidgets.QGridLayout()
        self.dropbox_grid.setObjectName("dropbox_grid")
        self.server_button = QtWidgets.QPushButton(parent=self.server_grid_layout)
        self.server_button.setObjectName("serverButton")
        self.dropbox_grid.addWidget(self.server_button, 2, 1, 1, 1)
        self.server_port_edit = QtWidgets.QLineEdit(parent=self.server_grid_layout)
        self.server_port_edit.setObjectName("server_port_edit")
        self.dropbox_grid.addWidget(self.server_port_edit, 2, 0, 1, 1)
        self.dropbox_label = QtWidgets.QLabel(parent=self.server_grid_layout)
        self.dropbox_label.setObjectName("dropbox_label")
        self.dropbox_grid.addWidget(self.dropbox_label, 1, 0, 1, 1)
        self.dropbox_edit = QtWidgets.QLineEdit(parent=self.server_grid_layout)
        self.dropbox_edit.setObjectName("dropbox_edit")
        self.dropbox_grid.addWidget(self.dropbox_edit, 0, 0, 1, 1)
        self.dropbox_button = QtWidgets.QPushButton(parent=self.server_grid_layout)
        self.dropbox_button.setObjectName("dropbox_button")
        self.dropbox_grid.addWidget(self.dropbox_button, 0, 1, 1, 1)
        self.server_port_label = QtWidgets.QLabel(parent=self.server_grid_layout)
        self.server_port_label.setObjectName("server_port_label")
        self.dropbox_grid.addWidget(self.server_port_label, 3, 0, 1, 1)
        self.server_grid.addLayout(self.dropbox_grid, 0, 1, 1, 1)
        self.tabs.addTab(self.server_tab, "")
        self.grid_layout.addWidget(self.tabs, 0, 0, 1, 1)
        self.logs = QtWidgets.QListView(parent=self.central)
        self.logs.setObjectName("logs")
        self.grid_layout.addWidget(self.logs, 0, 1, 1, 1)
        main_window.setCentralWidget(self.central)

        self.translate_ui(main_window)
        self.tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def translate_ui(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("main_window", "File Transfer"))
        self.client_port_label.setText(_translate("main_window", "Port"))
        self.client_host_label.setText(_translate("main_window", "Host"))
        self.upload_button.setText(_translate("main_window", "Upload files"))
        self.tabs.setTabText(self.tabs.indexOf(self.client_tab), _translate("main_window", "Client"))
        self.server_button.setText(_translate("main_window", "Start server"))
        self.dropbox_label.setText(_translate("main_window", "Dropbox Directory"))
        self.dropbox_button.setText(_translate("main_window", "Select Dropbox"))
        self.server_port_label.setText(_translate("main_window", "Port"))
        self.tabs.setTabText(self.tabs.indexOf(self.server_tab), _translate("main_window", "Server"))

        # Logging

        self.logs_model = QtCore.QStringListModel()
        self.logs.setModel(self.logs_model)

        # Functionality

        self.upload_button.clicked.connect(lambda: self.select_uploads())
        self.dropbox_button.clicked.connect(lambda: self.select_dropbox_directory())
        self.server_button.clicked.connect(lambda: self.toggle_server())

    def log(self, message):
        self.internal_logs.append(message)
        self.logs_model.setStringList(self.internal_logs)

    def warn(self, message):
        self.internal_logs.append("[WARN]: " + message)
        self.logs_model.setStringList(self.internal_logs)

    def error(self, message):
        self.internal_logs.append("[ERR]: " + message)
        self.logs_model.setStringList(self.internal_logs)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    ui = ui_main_window()
    ui.setup_ui(main_window)
    main_window.show()
    sys.exit(app.exec())
