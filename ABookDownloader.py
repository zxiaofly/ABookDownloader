import json
import logging
import os
import time
import tkinter.filedialog

import requests
from PySide2.QtWidgets import QApplication

from FileDownloader import file_downloader
from NameValidator import validate_file_name
from OSHandle import safe_mkdir
from Settings import Settings
from UserLogin import ABookLogin

session = requests.session()

COURSES_INFO_FILE = "./temp/course_info.json"
SETTINGS_PATH = "./temp/settings.json"
USER_INFO = "./temp/user_info.json"
DOWNLOAD_DIR = "./Downloads/"
ROOT = 0
courses_list = []
chapter_list = []

def change_download_path(settings):
    global DOWNLOAD_DIR
    new_download_path = tkinter.filedialog.askdirectory(title="Please select a folder:")
    new_download_path += "/"
    logging.info(new_download_path)
    DOWNLOAD_DIR = new_download_path
    settings['download_path'] = DOWNLOAD_DIR
    settings.save_settings_to_file()


def init():
    """This function will create temp and Downloads folders and display welcome. temp is for logs and information gathered while the program is running. The Downloads folder is where to save the downloaded file by default."""
    safe_mkdir("temp")
    safe_mkdir("Downloads")
    logger = logging.getLogger()
    logger.setLevel('DEBUG')
    chlr = logging.StreamHandler()
    chlr.setLevel('INFO')
    fhlr = logging.FileHandler('temp/ABookDownloaderLog.log')
    logger.addHandler(chlr)
    logger.addHandler(fhlr)
    logging.info("Started successfully!")

    print("ABookDownloader是由HEIGE-PCloud编写的开源Abook下载软件")
    print("当前版本 1.0.5 可前往项目主页检查更新")
    print("项目主页 https://github.com/HEIGE-PCloud/ABookDownloader")
    print("如果遇到任何问题，欢迎提交issue")
    print("如果这款软件帮到了您，欢迎前往该项目主页请作者喝奶茶QwQ")
    print("<========================================================>")


def get_courses_info(file_name):
    """Get courses info from login, need pass through the path to save the json file of courses information."""

    course_info_url = "http://abook.hep.com.cn/selectMyCourseList.action?mobile=true&cur=1"
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(session.get(course_info_url).json(), file, ensure_ascii=False, indent=4)
    logging.info("Courses info fetched!")

    global courses_list
    courses_list = []
    with open(file_name, 'r', encoding='utf-8') as courses_info:
        try:
            courses_data: list = json.load(courses_info)[0]['myMobileCourseList']
        except:
            logging.error("Cannot load courses.")
            return
        print('There are {} course(s) availaible.'.format(len(courses_data)))
        for course in courses_data:
            course['courseTitle'] = validate_file_name(course['courseTitle'])
            courses_list.append(course)
    logging.info("Courses info loaded.")


def get_chapter_info(course_id):
    """Get the chapter info by course_id"""
    global chapter_list
    chapter_list = []

    course_url = 'http://abook.hep.com.cn/resourceStructure.action?courseInfoId={}'.format(course_id)
    chapter_data = session.post(course_url).json()

    # Save chapter data
    with open("./temp/" + str(course_id) + '.json', 'w', encoding='utf-8') as file:
        json.dump(chapter_data, file, ensure_ascii=False, indent=4)
    logging.info("Chapter for course {} fetched".format(course_id))

    for chapter in chapter_data:
        chapter['name'] = validate_file_name(chapter['name'])
        chapter_list.append(chapter)
    logging.info("Chapter for {} loaded.".format(course_id))


def display_courses_info():
    print("0 下载全部")
    for i in range(len(courses_list)):
        print(i + 1, courses_list[i]['courseTitle'])
    print("o 打开下载文件夹")
    print("s 更改保存目录")
    print("q 退出")


def display_chapter_info(title_name, pid):
    """Display chapter info by selected course and parrent id."""
    print("> " + title_name + ":")
    print("0 下载全部")
    for i in range(len(chapter_list)):
        if chapter_list[i]['pId'] == pid:
            print(i + 1, chapter_list[i]['name'])
    print("q 返回上一级")


def chapter_has_child(selected_chapter):
    child_chapter = []
    for chapter in chapter_list:
        if chapter['pId'] == selected_chapter['id']:
            child_chapter.append(chapter)
    return child_chapter


def download_course_from_root(root_chapter, course_id, path):
    # for chapter in root_chapter:
    child_list = chapter_has_child(root_chapter)
    if len(child_list) != 0:
        for child in child_list:
            safe_mkdir(path + child['name'])
            download_course_from_root(
                child, course_id, path + child['name'] + '/')
    else:
        download_link_url = "http://abook.hep.com.cn/courseResourceList.action?courseInfoId={}&treeId={}&cur=1".format(course_id, root_chapter['id'])
        download_url_base = "http://abook.hep.com.cn/ICourseFiles/"
        while True:
            try:
                info = session.get(download_link_url).json()[0]
                break
            except:
                logging.error(
                    "Info fetched failed, will restart in 5 seconds.")
                time.sleep(5)
        if 'myMobileResourceList' in info:
            course = info['myMobileResourceList']
            print(len(course), "downloadable items found!")
            for i in range(len(course)):
                file_name = course[i]['resTitle']
                file_url = course[i]['resFileUrl']
                print(file_name)
                url = download_url_base + file_url
                print(url)
                file_type = file_url[str(file_url).find('.'):]
                location = path + str(file_name) + str(file_type)
                while True:
                    try:
                        file_downloader(location, url)
                        break
                    except:
                        logging.error(
                            "Download failed, will restart in 5 seconds.")
                        time.sleep(5)


def download_course(download_dir, selected_course, selected_root):
    safe_mkdir(download_dir + selected_course['courseTitle'])
    safe_mkdir(download_dir +
               selected_course['courseTitle'] + "/" + selected_root['name'])
    download_course_from_root(selected_root, selected_course['courseInfoId'], DOWNLOAD_DIR +
                              selected_course['courseTitle'] + "/" + selected_root['name'] + "/")

def select_chapter(title_name, pid):
    while True:
        display_chapter_info(title_name, pid)
        choice = input("Enter the chapter index to choose: ")
        if str(choice) == '0':
            return True
        if str(choice).isnumeric():
            choice = int(choice)
            selected_chapter = chapter_list[choice - 1]
            result = select_chapter(
                selected_chapter['name'], selected_chapter['id'])
            if result == False:
                continue
            elif result == True:
                return selected_chapter
            else:
                return result
        if str(choice) == 'q':
            return False


if __name__ == "__main__":
    init()
    app = QApplication(os.sys.argv)
    
    settings = Settings(SETTINGS_PATH)
    DOWNLOAD_DIR = settings["download_path"]

    user = ABookLogin(USER_INFO)
    session = user.session

    # Get and load courses infomation
    get_courses_info(COURSES_INFO_FILE)

    while True:
        display_courses_info()

        choice = input("Enter course index to choose: ")
        try:
            choice = int(choice)
        except ValueError:
            if choice == 'o':
                os.system("explorer " + DOWNLOAD_DIR.replace('/', '\\'))
                continue
            elif choice == 's':
                change_download_path(settings)
                continue
            else:
                logging.info("Bye~")
            break

        # Download All!
        if choice == 0:
            for selected_course in courses_list:
                get_chapter_info(selected_course['courseInfoId'])
                root_list = []
                for chapter in chapter_list:
                    if chapter['pId'] == 0:
                        root_list.append(chapter)
                for chapter in root_list:
                    download_course(DOWNLOAD_DIR, selected_course, chapter)
        else:
            try:
                selected_course = courses_list[choice - 1]
            except IndexError:
                print("Wrong Index!")
                continue
            # Get and load chapter information
            get_chapter_info(selected_course['courseInfoId'])

            # select_chapter(selected_course['courseTitle'], ROOT)
            # selected_root
            #               = True when user choose to download the entire course
            #               = course_info when user choose to download a specific sub-chapter
            selected_root = select_chapter(
                selected_course['courseTitle'], ROOT)

            if selected_root == False:
                continue
            if selected_root == True:
                root_list = []
                for chapter in chapter_list:
                    if chapter['pId'] == 0:
                        root_list.append(chapter)
                for chapter in root_list:
                    download_course(DOWNLOAD_DIR, selected_course, chapter)
            else:
                download_course(DOWNLOAD_DIR, selected_course, selected_root)
