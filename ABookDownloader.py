import json
import requests


keyword = "resourses"
block_keyword = "style"
url_base = "http://abook.hep.com.cn/ICourseFiles/"
cnt = 1

COURSES_INFO_FILE = "course_info.json"
session = requests.session()
courses_list = []

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

def get_course_info():
    """get course info from web and save it to json"""
    course_info_url = "http://abook.hep.com.cn/selectMyCourseList.action?mobile=true&cur=1"
    with open(COURSES_INFO_FILE, 'w', encoding='utf-8') as file:
        json.dump(session.get(course_info_url).json(), file, ensure_ascii=False, indent=4)
    print("Courses fetched!")

def load_courses_info():
    """load courses info from local"""
    with open(COURSES_INFO_FILE, 'r', encoding='utf-8') as courses_info:
        courses_data: list = json.load(courses_info)[0]['myMobileCourseList']
        print('There are {} course(s) availaible.'.format(len(courses_data)))
        for i in range(len(courses_data)):
            course_title = eval('courses_data[{}]'.format(i))['courseTitle']
            course_id = eval('courses_data[{}]'.format(i))['courseInfoId']
            print('{}. {}'.format(i + 1, c_title))
            courses_list.append({'serial': i + 1, 'course_id': course_id, 'course_title': course_title})

if __name__ == "__main__":
    loginName = input("Please input loginName: ")
    loginPassword = input("Please input loginPassword: ")
    Abook_login(loginName, loginPassword)
    get_course_info()
    load_courses_info()
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

