from PyQt6 import QtCore, QtWidgets
import sys
import os

from client import Client
from server import Server


class Logger:
    def __init__(self, model):
        self.model = model
        self.logs = []

    def log(self, message):
        self.logs.append(message)
        self.model.setStringList(self.logs)

    def error(self, message):
        self.logs.append(f'[ERR]: {message}')
        self.model.setStringList(self.logs)


def upload_files(host, port, parent=None, logger=None):
    if not host or not port:
        logger.error("Host and port are required")
        return

    try:
        int(port)
    except ValueError:
        logger.error("Port must be an integer")
        return

    files, _ = QtWidgets.QFileDialog.getOpenFileNames(
        parent,
        "Select files to upload",
        "",
        "All Files (*.*)"
    )

    if not files:
        logger.error("No files selected")
        return

    logger.log(f"Connecting to {host}:{port}")
    client = Client(host, port, logger)
    client.send_files(files)


def select_directory(parent=None):
    directory = QtWidgets.QFileDialog.getExistingDirectory(
        parent,
        "Select Dropbox Directory",
        "",
        QtWidgets.QFileDialog.Option.ShowDirsOnly
    )
    return directory


def start_server(port, dropbox_dir, parent=None, logger=None):
    if not port:
        logger.error("Port is required")
        return

    try:
        int(port)
    except ValueError:
        logger.error("Port must be an integer")
        return

    if not dropbox_dir:
        logger.error("Dropbox directory is required")
        return

    if not os.path.exists(dropbox_dir):
        logger.error("Dropbox directory does not exist")
        return

    server = Server(port, dropbox_dir, logger)
    server.start()


class Ui_MainWindow():
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(739, 985)
        self.Central = QtWidgets.QWidget(parent=MainWindow)
        self.Central.setObjectName("Central")
        self.gridLayout = QtWidgets.QGridLayout(self.Central)
        self.gridLayout.setObjectName("gridLayout")
        self.tabs = QtWidgets.QTabWidget(parent=self.Central)
        self.tabs.setMaximumSize(QtCore.QSize(300, 16777215))
        self.tabs.setObjectName("tabs")
        self.client = QtWidgets.QWidget()
        self.client.setObjectName("client")
        self.gridLayoutWidget_2 = QtWidgets.QWidget(parent=self.client)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(0, 0, 291, 81))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.clientGrid = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.clientGrid.setContentsMargins(0, 0, 0, 0)
        self.clientGrid.setObjectName("clientGrid")
        self.addressGrid = QtWidgets.QGridLayout()
        self.addressGrid.setObjectName("addressGrid")
        self.hostLabel = QtWidgets.QLabel(parent=self.gridLayoutWidget_2)
        self.hostLabel.setObjectName("hostLabel")
        self.addressGrid.addWidget(self.hostLabel, 1, 1, 1, 1)
        self.hostEdit = QtWidgets.QLineEdit(parent=self.gridLayoutWidget_2)
        self.hostEdit.setObjectName("hostEdit")
        self.addressGrid.addWidget(self.hostEdit, 0, 1, 1, 1)
        self.portLabel = QtWidgets.QLabel(parent=self.gridLayoutWidget_2)
        self.portLabel.setObjectName("portLabel")
        self.addressGrid.addWidget(self.portLabel, 1, 2, 1, 1)
        self.portEdit = QtWidgets.QLineEdit(parent=self.gridLayoutWidget_2)
        self.portEdit.setObjectName("portEdit")
        self.addressGrid.addWidget(self.portEdit, 0, 2, 1, 1)
        self.clientGrid.addLayout(self.addressGrid, 0, 0, 1, 1)
        self.upload = QtWidgets.QPushButton(parent=self.gridLayoutWidget_2)
        self.upload.setObjectName("upload")
        self.clientGrid.addWidget(self.upload, 1, 0, 1, 1)
        self.tabs.addTab(self.client, "")
        self.server = QtWidgets.QWidget()
        self.server.setObjectName("server")
        self.gridLayoutWidget_4 = QtWidgets.QWidget(parent=self.server)
        self.gridLayoutWidget_4.setGeometry(QtCore.QRect(0, 0, 291, 81))
        self.gridLayoutWidget_4.setObjectName("gridLayoutWidget_4")
        self.serverGrid = QtWidgets.QGridLayout(self.gridLayoutWidget_4)
        self.serverGrid.setContentsMargins(0, 0, 0, 0)
        self.serverGrid.setObjectName("serverGrid")
        self.serverButton = QtWidgets.QPushButton(parent=self.gridLayoutWidget_4)
        self.serverButton.setObjectName("serverButton")
        self.serverGrid.addWidget(self.serverButton, 1, 0, 1, 1)
        self.dropboxGrid = QtWidgets.QGridLayout()
        self.dropboxGrid.setObjectName("dropboxGrid")
        self.dropboxButton = QtWidgets.QPushButton(parent=self.gridLayoutWidget_4)
        self.dropboxButton.setObjectName("dropboxButton")
        self.dropboxGrid.addWidget(self.dropboxButton, 0, 1, 1, 1)
        self.dropboxLabel = QtWidgets.QLabel(parent=self.gridLayoutWidget_4)
        self.dropboxLabel.setObjectName("dropboxLabel")
        self.dropboxGrid.addWidget(self.dropboxLabel, 1, 0, 1, 1)
        self.dropboxEdit = QtWidgets.QLineEdit(parent=self.gridLayoutWidget_4)
        self.dropboxEdit.setObjectName("dropboxEdit")
        self.dropboxGrid.addWidget(self.dropboxEdit, 0, 0, 1, 1)
        self.serverGrid.addLayout(self.dropboxGrid, 0, 0, 1, 1)
        self.tabs.addTab(self.server, "")
        self.gridLayout.addWidget(self.tabs, 0, 0, 1, 1)
        self.logs = QtWidgets.QListView(parent=self.Central)
        self.logs.setObjectName("logs")
        self.gridLayout.addWidget(self.logs, 0, 1, 1, 1)
        MainWindow.setCentralWidget(self.Central)

        self.logs_model = QtCore.QStringListModel()
        self.logs.setModel(self.logs_model)
        self.logger = Logger(self.logs_model)

        self.retranslateUi(MainWindow)
        self.tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "File Transfer"))
        self.portLabel.setText(_translate("MainWindow", "Port"))
        self.hostLabel.setText(_translate("MainWindow", "Host"))
        self.upload.setText(_translate("MainWindow", "Upload files"))
        self.upload.clicked.connect(
            lambda: upload_files(
                self.hostEdit.text(),
                self.portEdit.text(),
                MainWindow,
                self.logger
            )
        )
        self.tabs.setTabText(self.tabs.indexOf(self.client), _translate("MainWindow", "Client"))
        self.serverButton.setText(_translate("MainWindow", "Start server"))
        self.serverButton.clicked.connect(
            lambda: start_server(
                8040,
                self.dropboxEdit.text(),
                MainWindow,
                self.logger
            )
        )
        self.dropboxButton.setText(_translate("MainWindow", "Select Dropbox"))
        self.dropboxButton.clicked.connect(
            lambda: self.dropboxEdit.setText(select_directory(MainWindow))
        )
        self.dropboxLabel.setText(_translate("MainWindow", "Dropbox Directory"))
        self.tabs.setTabText(self.tabs.indexOf(self.server), _translate("MainWindow", "Server"))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())