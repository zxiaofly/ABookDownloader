import requests


keyword = "resourses"
block_keyword = "style"
url_base = "http://abook.hep.com.cn/ICourseFiles/"
cnt = 1

session = requests.session()

def downloader(url, file_type, name):
    r = requests.get(url)
    with open(str(cnt) + str(file_type),"wb") as f:
        f.write(r.content)

def Abook_login(loginName, loginPassword):
    """Log in and create a session"""
    login_url = "http://abook.hep.com.cn/loginMobile.action"
    login_status_url = "http://abook.hep.com.cn/verifyLoginMobile.action"
    login_data = {"loginUser.loginName": loginName, "loginUser.loginPassword": loginPassword}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.64"}
    session.post(url=login_url, data=login_data, headers=headers)
    if session.post(login_status_url).json()["message"] == "已登录":
        print("Successfully login in!")
    else:
        print("Login failed, please try again.")



if __name__ == "__main__":
    loginName = input("Please input loginName: ")
    loginPassword = input("Please input loginPassword: ")
    Abook_login(loginName, loginPassword)
    # file = open("Sol.html", "r", encoding="utf-8")
    # for lines in file:
    #     if str(lines).find(keyword) != -1 and str(lines).find(block_keyword) == -1:
    #         index_start = str(lines).find("value=\"")
    #         index_end = str(lines).find(".")
    #         url_detail = str(lines)[index_start + 7 : index_end + 4]
    #         url = url_base + url_detail
    #         ext_end = str(lines).find("\"", index_end)
    #         ext = lines[index_end : ext_end]
    #         print(url)
    #         print(ext)
    #         # downloader(url, ext, cnt)
    #         cnt += 1
    # file.close()

