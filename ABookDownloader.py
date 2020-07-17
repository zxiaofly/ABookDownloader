import json
import getpass
import requests

session = requests.session()

COURSES_INFO_FILE = "course_info.json"
DOWNLOAD_LINK = "download_link.json"
USER_INFO = "user_info.json"
courses_list = []
chapter_list = []

def downloader():
    download_url_base = "http://abook.hep.com.cn/ICourseFiles/"
    with open(DOWNLOAD_LINK, 'r', encoding='utf-8') as courses_info:
        download_data: list = json.load(courses_info)[0]['myMobileResourceList']
    print(len(download_data), "downloadable items found!")
    for i in range(len(download_data)):
        file_name = download_data[i]['resTitle']
        file_url = download_data[i]['resFileUrl']
        print(file_name)
        url = download_url_base + file_url
        print(url)
        file_type = file_url[str(file_url).find('.'):]
        r = requests.get(url)
        location =  str(file_name) + str(file_type)
        print(location)
        with open(location, "wb") as f:
            f.write(r.content)

def Abook_login(login_name, login_password):
    login_url = "http://abook.hep.com.cn/loginMobile.action"
    login_status_url = "http://abook.hep.com.cn/verifyLoginMobile.action"
    login_data = {"loginUser.loginName": login_name, "loginUser.loginPassword": login_password}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.64"}
    session.post(url=login_url, data=login_data, headers=headers)
    if session.post(login_status_url).json()["message"] == "已登录":
        print("Successfully login in!")
    else:
        print("Login failed, please try again.")

def get_courses_info():
    course_info_url = "http://abook.hep.com.cn/selectMyCourseList.action?mobile=true&cur=1"
    with open(COURSES_INFO_FILE, 'w', encoding='utf-8') as file:
        json.dump(session.get(course_info_url).json(), file, ensure_ascii=False, indent=4)
    print("Courses fetched!")

def load_courses_info():
    with open(COURSES_INFO_FILE, 'r', encoding='utf-8') as courses_info:
        courses_data: list = json.load(courses_info)[0]['myMobileCourseList']
        print('There are {} course(s) availaible.'.format(len(courses_data)))
        for i in range(len(courses_data)):
            course_title = eval('courses_data[{}]'.format(i))['courseTitle']
            course_id = eval('courses_data[{}]'.format(i))['courseInfoId']
            courses_list.append({'course_id': course_id, 'course_title': course_title})

def get_chapter_info(course_id):
    course_url = 'http://abook.hep.com.cn/resourceStructure.action?courseInfoId={}'.format(course_id)
    with open(str(course_id) + '.json', 'w', encoding='utf-8') as file:
        json.dump(session.post(course_url).json(), file, ensure_ascii=False, indent=4)

def display_courses_info():
    for i in range(len(courses_list)):
        print(i + 1, courses_list[i]['course_title'])

def load_chapter_info(course_id):
    with open(str(course_id) + '.json', 'r', encoding='utf-8') as chapter_info:
        chapter_data: list = json.load(chapter_info)
    for chapter in chapter_data:
        chapter_list.append({'chapter_id': chapter['id'], 'chapter_name': chapter['name']})

def display_chapter_info():
    for i in range(len(chapter_list)):
        print(i + 1, chapter_list[i]['chapter_name'])

def get_download_link(course_id, chapter_id):
    download_link_url = "http://abook.hep.com.cn/courseResourceList.action?courseInfoId={}&treeId={}&cur=1".format(course_id, chapter_id)
    with open(DOWNLOAD_LINK, 'w', encoding='utf-8') as file:
        json.dump(session.get(download_link_url).json(), file, ensure_ascii=False, indent=4)

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
    Abook_login(user_info['login_name'], user_info['login_password'])

    ### Get and load courses infomation
    get_courses_info()
    load_courses_info()
    
    display_courses_info()

    choice = int(input("Enter course index to choose: "))
    selected_course_id = courses_list[choice - 1]['course_id']

    ### Get and load chapter information
    get_chapter_info(selected_course_id)
    load_chapter_info(selected_course_id)

    display_chapter_info()
    
    choice = int(input("Enter chapter index to choose: "))
    selected_chapter_id = chapter_list[choice - 1]['chapter_id']
    
    ### Fetch the download links
    get_download_link(selected_course_id, selected_chapter_id)
    ### Download the links
    downloader()