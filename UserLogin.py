import json
import logging
import requests
import sys
from PySide2.QtWidgets import *
from PySide2.QtCore import *


class login_dialog(QDialog):

    def __init__(self, parent=None):
        super(login_dialog, self).__init__(parent)

        # Set Window
        self.setWindowTitle("ABook Login")

        # Set widgets
        self.username_label = QLabel("Username: ")
        self.username_input = QLineEdit("")
        
        self.password_label = QLabel("Password: ")
        self.password_input = QLineEdit("")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.button = QPushButton("Login")

        self.checkbox = QCheckBox("Show")

        # Set layout
        self.username_layout = QHBoxLayout()
        self.username_layout.addWidget(self.username_label)
        self.username_layout.addWidget(self.username_input)

        self.password_layout = QHBoxLayout()
        self.password_layout.addWidget(self.password_label)
        self.password_layout.addWidget(self.password_input)
        self.password_layout.addWidget(self.checkbox)

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.username_layout)
        self.layout.addLayout(self.password_layout)
        self.layout.addWidget(self.button)

        # Set dialog layout
        self.setLayout(self.layout)
        
        # Set signals
        self.button.clicked.connect(self.user_login)
        self.checkbox.stateChanged.connect(self.password_echo)

    def password_echo(self, state):
        if state == Qt.Checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)

    def user_login(self):
        pass

    def login_failed(self):
        QMessageBox.critical(self, 'Error', 'Login failed.')

class ABookLogin(login_dialog):
    def __init__(self, path):
        super().__init__()
        self.username = ''
        self.password = ''
        self.user_info = {'loginUser.loginName': '', 'loginUser.loginPassword': ''}
        self.path = path
        self.session = requests.session()
        self.login_url = "http://abook.hep.com.cn/loginMobile.action"
        self.login_status_url = "http://abook.hep.com.cn/verifyLoginMobile.action"
        self.headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.64"}
        self.login_status = False

        # Attempt to read user info from file first
        if self.read_user_info_from_file() == False:
            self.user_info = {'loginUser.loginName': '', 'loginUser.loginPassword': ''}

        self.username_input.setText(self.username)
        self.password_input.setText(self.password)
        self.exec_()

    def check_login_status(self):
        self.login_status =  self.session.post(self.login_status_url).json()["message"] == "已登录"
        logging.info("Login status: " + str(self.login_status))
        return self.login_status

    def read_user_info_from_file(self):
        try:
            with open(self.path, 'r', encoding='utf-8') as file:
                self.user_info = json.load(file)
                self.username = self.user_info['loginUser.loginName']
                self.password = self.user_info['loginUser.loginPassword']
            return True
        except:
            return False
        
    def save_user_info_to_file(self):
        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(self.user_info, file, ensure_ascii=False, indent=4)

    def input_user_info(self):
        self.username_input.setText(self.username)
        self.password_input.setText(self.password)
        self.exec_()
        self.username = self.username_input.text()
        self.password = self.password_input.text()
        self.user_info = {'loginUser.loginName': self.username, 'loginUser.loginPassword': self.password}
        self.save_user_info_to_file()

    def attempt_login(self):
        self.session.post(url=self.login_url, data=self.user_info, headers=self.headers)

    def user_login(self):
        self.username = self.username_input.text()
        self.password = self.password_input.text()
        self.user_info = {'loginUser.loginName': self.username, 'loginUser.loginPassword': self.password}
        self.save_user_info_to_file()
        self.attempt_login()
        if self.check_login_status():
            self.close()
        else:
            self.username = ''
            self.password = ''
            self.user_info = {'loginUser.loginName': '', 'loginUser.loginPassword': ''}
            self.login_failed()
    
    def closeEvent(self, event):
        if self.login_status == False:
            sys.exit(0)