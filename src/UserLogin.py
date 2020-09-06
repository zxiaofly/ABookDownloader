import json
import logging
import requests
import sys
from PySide2 import QtCore, QtWidgets

class ABookLogin(QtCore.QThread):
    def __init__(self):
        self.username = ''
        self.password = ''
        self.user_info = {'loginUser.loginName': '', 'loginUser.loginPassword': ''}
        self.path = './temp/user_info.json'
        self.session = requests.session()
        self.login_url = "http://abook.hep.com.cn/loginMobile.action"
        self.login_status_url = "http://abook.hep.com.cn/verifyLoginMobile.action"
        self.headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.64"}
        self.login_status = False

        # Attempt to read user info from file first
        self.read_user_info_from_file()

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

    def user_login(self):
        self.save_user_info_to_file()
        self.session.post(url=self.login_url, data=self.user_info, headers=self.headers)
        return self.check_login_status()

class LoginWidget(QtWidgets.QWidget):
    
    def __init__(self, parent=None):
        super(LoginWidget, self).__init__(parent)

        self.username_label = QtWidgets.QLabel("Username: ")
        self.username_input = QtWidgets.QLineEdit(self.parent().user_info["loginUser.loginName"])
        
        self.password_label = QtWidgets.QLabel("Password: ")
        self.password_input = QtWidgets.QLineEdit(self.parent().user_info["loginUser.loginPassword"])
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        self.button = QtWidgets.QPushButton("Login")

        self.checkbox = QtWidgets.QCheckBox("Show")

        self.username_layout = QtWidgets.QHBoxLayout()
        self.username_layout.addWidget(self.username_label)
        self.username_layout.addWidget(self.username_input)

        self.password_layout = QtWidgets.QHBoxLayout()
        self.password_layout.addWidget(self.password_label)
        self.password_layout.addWidget(self.password_input)
        self.password_layout.addWidget(self.checkbox)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.username_layout)
        self.layout.addLayout(self.password_layout)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

        self.button.clicked.connect(self.parent().btn_user_login)
        self.checkbox.stateChanged.connect(self.password_echo)

    def password_echo(self, state):
        if state == QtCore.Qt.Checked:
            self.password_input.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)

class LoginLogWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self)

class UserLoginDialog(QtWidgets.QDialog, ABookLogin):

    def __init__(self, parent=None):

        # Init
        QtWidgets.QDialog.__init__(self)
        ABookLogin.__init__(self)

        # Set window
        self.setWindowTitle("ABook Login")

        self.central_widget = QtWidgets.QStackedWidget()
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.central_widget)
        self.setLayout(self.layout)

        self.login_widget = LoginWidget(self)
        self.central_widget.addWidget(self.login_widget)

        self.exec_()



    def btn_user_login(self):
        self.user_info = {'loginUser.loginName': self.login_widget.username_input.text(), 'loginUser.loginPassword': self.login_widget.password_input.text()}
        if self.user_login():
            print("success")
            self.close()
        else:
            self.login_failed()
        

    def login_failed(self):
        QtWidgets.QMessageBox.critical(self, 'Error', 'Login failed.')

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    login = UserLoginDialog()

    print("now here")
