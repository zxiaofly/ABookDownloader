import json
import logging
import requests
import sys
from PySide2 import QtCore, QtWidgets

class ABookLogin(QtCore.QThread):

    # Two signals
    #   update_status is for sending the login log
    update_status = QtCore.Signal(str)
    #   login_response is for sending the login state
    login_response = QtCore.Signal(bool)

    def __init__(self):
        super().__init__()

        # init constant variables
        self.user_info = {'loginUser.loginName': '', 'loginUser.loginPassword': ''}
        self.path = './temp/user_info.json'
        self.session = requests.session()
        self.login_url = "http://abook.hep.com.cn/loginMobile.action"
        self.login_status_url = "http://abook.hep.com.cn/verifyLoginMobile.action"
        self.headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.64"}

        # try to read user info from local file first
        self.read_user_info_from_file()

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

    def run(self):
        # Step 1: save user info to local file
        self.update_status.emit("Saving user's info to file... (Step 1/3)")
        self.save_user_info_to_file()
        
        # Step 2: post user info to ABook
        self.update_status.emit("Posting user's info to ABook... (Stpe 2/3)")
        self.session.post(url=self.login_url, data=self.user_info, headers=self.headers)
        
        # Step 3: check login status
        self.update_status.emit("Checking login status... (Step 3/3)")
        login_status_msg = self.session.post(self.login_status_url).json()
        
        # send login status signal
        self.login_response.emit(login_status_msg["message"] == "已登录")


class LoginWidget(QtWidgets.QWidget):
    
    def __init__(self, parent=None):
        super(LoginWidget, self).__init__(parent)

        # username label
        self.username_label = QtWidgets.QLabel("Username: ")
        self.username_input = QtWidgets.QLineEdit(self.parent().login_worker.user_info["loginUser.loginName"])
        
        # password label
        self.password_label = QtWidgets.QLabel("Password: ")
        self.password_input = QtWidgets.QLineEdit(self.parent().login_worker.user_info["loginUser.loginPassword"])
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        # button
        self.button = QtWidgets.QPushButton("Login")
        self.button.clicked.connect(self.parent().btn_user_login)

        # checkbox
        self.checkbox = QtWidgets.QCheckBox("Show")
        self.checkbox.stateChanged.connect(self.password_echo)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.username_label, 0, 0)
        layout.addWidget(self.username_input, 0, 1)
        layout.addWidget(self.password_label, 1, 0)
        layout.addWidget(self.password_input, 1, 1)
        layout.addWidget(self.checkbox, 2, 1, QtCore.Qt.AlignRight)
        layout.addWidget(self.button, 3, 1)

        self.setLayout(layout)

    def password_echo(self, state):
        if state == QtCore.Qt.Checked:
            self.password_input.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)

class LoginLogWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(LoginLogWidget, self).__init__(parent)

        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

    def add_log(self, log: str):
        log_label = QtWidgets.QLabel(log)
        self.layout.addWidget(log_label)
    
    def delete_log(self):
        for i in range(self.layout.count()):
            self.layout.itemAt(i).widget().deleteLater()

class UserLoginDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self)

        self.login_worker = ABookLogin()

        # set window
        self.setWindowTitle("ABook Login")

        # two widget
        self.login_widget = LoginWidget(self)
        self.loginlog_widget = LoginLogWidget(self)

        # stack widget
        self.central_widget = QtWidgets.QStackedWidget()
        self.central_widget.addWidget(self.login_widget)
        self.central_widget.addWidget(self.loginlog_widget)

        # set layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.central_widget)
        self.setLayout(self.layout)


        self.login_worker.update_status.connect(self.loginlog_widget.add_log)
        self.login_worker.login_response.connect(self.handle_login_response)

        self.exec_()

    def btn_user_login(self):

        self.central_widget.setCurrentWidget(self.loginlog_widget)
        self.login_worker.user_info = {'loginUser.loginName': self.login_widget.username_input.text(), 'loginUser.loginPassword': self.login_widget.password_input.text()}
        self.login_worker.start()

    def handle_login_response(self, response: bool):
        if response:
            self.close()
        else:
            # a cute message box for a failing login
            QtWidgets.QMessageBox.critical(self, 'Error', 'Login failed.')
            # delete login logs
            self.loginlog_widget.delete_log()
            # switch back to login input layout
            self.central_widget.setCurrentWidget(self.login_widget)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    login = UserLoginDialog()
