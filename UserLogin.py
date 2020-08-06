import json
import logging
import requests

class ABookLogin(object):
    def __init__(self):
        super().__init__()
        self.username = ''
        self.password = ''
        self.user_info = {}
        self.path = './temp/user_info.json'
        self.session = requests.session()
        self.login_url = "http://abook.hep.com.cn/loginMobile.action"
        self.login_status_url = "http://abook.hep.com.cn/verifyLoginMobile.action"
        self.headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.64"}

        # Attempt to read user info from file first
        if self.read_user_info_from_file():
            choice = input("User {} founded! Do you want to log in as {}? (y/n) ".format(self.username, self.username))
            if choice == 'n':
                self.user_info = {}

        # If no user info is read, ask for input
        if self.user_info == {}:
            self.input_user_info()

        # Attempt login, if failed, ask for login info again
        while True:
            self.attempt_login()
            if self.check_login_status():
                break
            self.input_user_info()

    def check_login_status(self):
        is_success =  self.session.post(self.login_status_url).json()["message"] == "已登录"
        logging.info("Login status: " + str(is_success))
        return is_success

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
        self.username = input("Please input username: ")
        self.password = input("Please input password: ")
        self.user_info = {'loginUser.loginName': self.username, 'loginUser.loginPassword': self.password}
        self.save_user_info_to_file()

    def attempt_login(self):
        self.session.post(url=self.login_url, data=self.user_info, headers=self.headers)