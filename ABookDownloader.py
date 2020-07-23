import os
import json
import time
import getpass
import requests

session = requests.session()

COURSES_INFO_FILE = ".\\temp\\course_info.json"
DOWNLOAD_LINK = ".\\temp\\download_link.json"
USER_INFO = ".\\temp\\user_info.json"
courses_list = []
chapter_list = []
download_info = []

def safe_mkdir(dir_name):
    try:
        os.mkdir(str(dir_name))
    except FileExistsError:
        pass

def safe_remove(dir_name):
    try:
        os.remove(str(dir_name))
    except FileNotFoundError:
        pass

def init():
    safe_mkdir("temp")
    safe_mkdir("Downloads")
    print("启动成功！")
    print("ABookDownloader是由HEIGE-PCloud编写的开源Abook下载软件")
    print("当前版本 1.0.2 可前往项目主页检查更新")
    print("项目主页 https://github.com/HEIGE-PCloud/ABookDownloader")
    print("如果遇到任何问题，欢迎提交issue")
    print("如果这款软件帮到了您，欢迎前往该项目主页请作者喝奶茶QwQ")
    print("<========================================================>")

def file_downloader(file_name, url):
    headers = {'Proxy-Connection':'keep-alive'}
    r = requests.get(url, stream=True, headers=headers)
    content_length = float(r.headers['content-length'])
    with open(file_name, 'wb') as file:
        downloaded_length = 0
        last_downloaded_length = 0
        time_start = time.time()
        for chunk in r.iter_content(chunk_size = 512):
            if chunk:
                file.write(chunk)
                downloaded_length += len(chunk)
                if time.time() - time_start > 1:
                    percentage = downloaded_length / content_length * 100
                    speed = (downloaded_length - last_downloaded_length) / 2097152
                    last_downloaded_length = downloaded_length
                    print("\r Downloading: " + file_name + ': ' + '{:.2f}'.format(percentage) + '% Speed: ' + '{:.2f}'.format(speed) + 'MB/S', end="")
                    time_start = time.time()
    print("\nDownload {} successfully!".format(file_name))


def download_course(selected_course, selected_chapter):
    safe_mkdir(".\\Downloads\\" + selected_course['course_title'])
    safe_mkdir(".\\Downloads\\" + selected_course['course_title'] + "\\" + selected_chapter['name'])
    download_url_base = "http://abook.hep.com.cn/ICourseFiles/"
    with open(DOWNLOAD_LINK, 'r', encoding='utf-8') as courses_info:
        try:
            download_data: list = json.load(courses_info)
        except KeyError:
            print("No content. Skipped")
    for course in download_data:
        if "myMobileResourceList" not in course:
            continue
        course = course['myMobileResourceList']
        print(len(course), "downloadable items found!")
        for i in range(len(course)):
            file_name = course[i]['resTitle']
            file_url = course[i]['resFileUrl']
            print(file_name)
            url = download_url_base + file_url
            print(url)
            file_type = file_url[str(file_url).find('.'):]
            location = ".\\Downloads\\" + selected_course['course_title'] + "\\" + selected_chapter['name'] + "\\" + str(file_name) + str(file_type)
            file_downloader(location, url)
    global download_info
    download_info = []

def Abook_login(login_name, login_password):
    login_url = "http://abook.hep.com.cn/loginMobile.action"
    login_status_url = "http://abook.hep.com.cn/verifyLoginMobile.action"
    login_data = {"loginUser.loginName": login_name, "loginUser.loginPassword": login_password}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.64"}
    session.post(url=login_url, data=login_data, headers=headers)
    if session.post(login_status_url).json()["message"] == "已登录":
        print("Successfully login in!")
        return True
    else:
        print("Login failed, please try again.")
        safe_remove(".\\temp\\user_info.json")
        return False

def get_courses_info():
    course_info_url = "http://abook.hep.com.cn/selectMyCourseList.action?mobile=true&cur=1"
    with open(COURSES_INFO_FILE, 'w', encoding='utf-8') as file:
        json.dump(session.get(course_info_url).json(), file, ensure_ascii=False, indent=4)
    print("Courses fetched!")

def load_courses_info():
    global courses_list
    courses_list = []
    with open(COURSES_INFO_FILE, 'r', encoding='utf-8') as courses_info:
        courses_data: list = json.load(courses_info)[0]['myMobileCourseList']
        print('There are {} course(s) availaible.'.format(len(courses_data)))
        for i in range(len(courses_data)):
            course_title = eval('courses_data[{}]'.format(i))['courseTitle']
            course_id = eval('courses_data[{}]'.format(i))['courseInfoId']
            courses_list.append({'course_id': course_id, 'course_title': course_title})

def get_chapter_info(course_id):
    course_url = 'http://abook.hep.com.cn/resourceStructure.action?courseInfoId={}'.format(course_id)
    with open(".\\temp\\" + str(course_id) + '.json', 'w', encoding='utf-8') as file:
        json.dump(session.post(course_url).json(), file, ensure_ascii=False, indent=4)

def display_courses_info():
    print("0 下载全部")
    for i in range(len(courses_list)):
        print(i + 1, courses_list[i]['course_title'])
    print("o 打开下载文件夹")
    print("q 退出")

def load_chapter_info(course_id):
    global chapter_list
    chapter_list = []
    with open(".\\temp\\" + str(course_id) + '.json', 'r', encoding='utf-8') as chapter_info:
        chapter_data: list = json.load(chapter_info)
    remove_list = []
    for chapter in chapter_data:
        if chapter["type"] == 5:
            for child_chapter in chapter_data:
                if child_chapter["pId"] == chapter["id"]:
                    remove_list.append(child_chapter)
                    if 'child' not in chapter:
                        chapter["child"] = []
                    chapter["child"].append(child_chapter)

    for chapter in remove_list:
        chapter_data.remove(chapter)
    chapter_list = chapter_data

def display_chapter_info(selected_course):
    print("> " + selected_course['course_title'] + ":")
    print("0 下载全部")
    for i in range(len(chapter_list)):
        print(i + 1, chapter_list[i]['name'])
        if 'child' in chapter_list[i]:
            for child_chapter in chapter_list[i]['child']:
                print(" - " + child_chapter['name'])
    print("q 返回上一级")

def get_download_link(selected_course, selected_chapter):
    global download_info
    if 'child' in selected_chapter:
        for chapter in selected_chapter['child']:
            get_download_link(selected_course, chapter)
    download_link_url = "http://abook.hep.com.cn/courseResourceList.action?courseInfoId={}&treeId={}&cur=1".format(selected_course['course_id'], selected_chapter['id'])
    info = session.get(download_link_url).json()[0]
    download_info.append(info)
    with open(DOWNLOAD_LINK, 'w', encoding='utf-8') as file:
        json.dump(download_info, file, ensure_ascii=False, indent=4)

def read_login_info():
    try:
        with open(USER_INFO, 'r', encoding='utf-8') as file:
            try:
                login_info: list = json.load(file)
                return login_info
            except json.decoder.JSONDecodeError:
                return False
    except FileNotFoundError:
        return False

def write_login_info(login_name, login_password):
    with open(USER_INFO, 'w', encoding='utf-8') as file:
        json.dump({'login_name': login_name, 'login_password': login_password}, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    init()
    ### First check if there is user information stored locally.
    ###     If there is, then ask whether the user will use it or not.
    ###     If there isn't, ask user type in information directly.
    user_info = read_login_info()
    if user_info != False:
        choice = input("User {} founded! Do you want to log in as {}? (y/n) ".format(user_info['login_name'], user_info['login_name']))
        if choice == 'n':
            user_info = False
    if user_info == False:
        login_name = input("Please input login name: ")
        login_password = getpass.getpass("Please input login password: ")
        user_info = {'login_name': login_name, 'login_password': login_password}
        write_login_info(login_name, login_password)

    ### User login
    while True:
        if Abook_login(user_info['login_name'], user_info['login_password']):
            break
        login_name = input("Please input login name: ")
        login_password = getpass.getpass("Please input login password: ")
        user_info = {'login_name': login_name, 'login_password': login_password}
        write_login_info(login_name, login_password)
        

    ### Get and load courses infomation
    get_courses_info()
    load_courses_info()

    while True:
        display_courses_info()

        
        choice = input("Enter course index to choose: ")
        try:
            choice = int(choice)
        except ValueError:
            if choice == 'o':
                os.system("explorer .\\Downloads\\")
                continue
            else:
                print("Bye~")
            break

        ### Download All!
        if choice == 0:
            for i in range(len(courses_list)):
                selected_course = courses_list[i]
                get_chapter_info(selected_course['course_id'])
                load_chapter_info(selected_course['course_id'])
                for i in range(len(chapter_list)):
                    selected_chapter = chapter_list[i]
                    get_download_link(selected_course, selected_chapter)
                    download_course(selected_course, selected_chapter)
        else:
            try:
                selected_course = courses_list[choice - 1]
            except IndexError:
                print("Wrong Index!")
                continue
            ### Get and load chapter information
            get_chapter_info(selected_course['course_id'])
            load_chapter_info(selected_course['course_id'])

            display_chapter_info(selected_course)
            try:
                choice = int(input("Enter chapter index to choose: "))
            except ValueError:
                continue
            if choice == 0:
                for i in range(len(chapter_list)):
                    selected_chapter = chapter_list[i]
                    get_download_link(selected_course, selected_chapter)
                    download_course(selected_course, selected_chapter)
            else:
                try:
                    selected_chapter = chapter_list[choice - 1]
                    ### Fetch the download links
                    get_download_link(selected_course, selected_chapter)
                    ### Download the links
                    download_course(selected_course, selected_chapter)
                except IndexError:
                    print("Wrong Index!")
