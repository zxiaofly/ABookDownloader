import os
import sys
import json
import logging
import requests

from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
from UserLogin import ABookLogin
from Settings import Settings
from OSHandle import *


class ABook(object):
    def __init__(self, path: str, settings: Settings, user: ABookLogin):
        super().__init__()
        self.settings = settings
        self.session = user.session
        self.path = path

        self.course_list = []
        self.course_list_path = '{}course_list({}).json'.format(self.path, user.username)
        

        if os.path.exists(self.course_list_path):
            with open(self.course_list_path, 'r', encoding='utf-8') as file:
                self.course_list = json.load(file)
        else:
            self.refresh_course_list()

    def refresh_course_list(self):
        self.get_courses_info()
        
        for index in range(len(self.course_list)):
            print("Fetching course #{} as total of {} course(s).".format(index + 1, len(self.course_list)))
            self.get_chapter_info(index)

    def get_courses_info(self):

        course_list_url = "http://abook.hep.com.cn/selectMyCourseList.action?mobile=true&cur=1"
        self.course_list = self.session.get(course_list_url).json()

        try:
            self.course_list = self.course_list[0]['myMobileCourseList']
            self.save_json_to_file(self.course_list_path, self.course_list)
            logging.info("Courses info fetched!")
        except:
            pass

    def get_chapter_info(self, index):
        course_id = self.course_list[index]['courseInfoId']        
        course_url = 'http://abook.hep.com.cn/resourceStructure.action?courseInfoId={}'.format(course_id)
        chapter_list = self.session.post(course_url).json()
        for chapter_index in range(len(chapter_list)):
            print("Course: {}. Fetching chapter #{} as total of {} chapter(s).".format(course_id, chapter_index + 1, len(chapter_list)))
            resource_url = "http://abook.hep.com.cn/courseResourceList.action?courseInfoId={}&treeId={}&cur=1".format(course_id, chapter_list[chapter_index]['id'])
            resource_list = self.session.post(resource_url).json()
            try:
                resource_list = resource_list[0]["myMobileResourceList"]
            except:
                resource_list = None
            chapter_list[chapter_index]['resource'] = resource_list
        self.course_list[index]['chapter'] = chapter_list
        self.save_json_to_file(self.course_list_path, self.course_list)

    def get_resource_info(self, course_id, chapter_id):
        resource_list = self.course_list
        for course in resource_list:
            if str(course["courseInfoId"]) == course_id:
                resource_list = course["chapter"]
                break
        for chapter in resource_list:
            if str(chapter["id"]) == chapter_id:
                resource_list = chapter["resource"]
                break
        return resource_list

    def save_json_to_file(self, path, data):
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

class CourseTreeWidget(QtWidgets.QWidget, ABook):

    def __init__(self, path, settings, session):
        QtWidgets.QWidget.__init__(self)
        ABook.__init__(self, path, settings, session)
        self.selected_list = []
        
        self.TreeWidget = QtWidgets.QTreeWidget()
        self.TreeWidget.setHeaderLabels(['Name', "Course ID", "Chapter ID"])
        self.TreeWidget.setAlternatingRowColors(True)
        self.TreeWidget.itemChanged.connect(self.checkbox_toggled)
        self.TreeWidget.doubleClicked.connect(self.get_resource_info_from_item)

        self.download_button = QtWidgets.QPushButton("Download Selected")
        self.download_button.clicked.connect(self.download_selected)

        self.refresh_button = QtWidgets.QPushButton("Refresh Course List")
        self.refresh_button.clicked.connect(self.refresh_course_list_tree)


        self.ListView = QtWidgets.QListView()
        # self.ListView.setViewMode(QtWidgets.QListView.IconMode)
        self.resource_list = QtGui.QStandardItemModel()
        self.ListView.setModel(self.resource_list)
        self.ListView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.ListView.doubleClicked.connect(self.open_resource)

        list_widget_layout = QtWidgets.QHBoxLayout()
        list_widget_layout.addWidget(self.TreeWidget)
        list_widget_layout.addWidget(self.ListView)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(list_widget_layout)
        main_layout.addWidget(self.download_button)
        main_layout.addWidget(self.refresh_button)
        self.setLayout(main_layout)

        for index in range(len(self.course_list)):
            self.create_tree(self.TreeWidget, self.course_list[index], 'course', index)

    def checkbox_toggled(self, node: QtWidgets.QTreeWidgetItem, column: int):
        if node.checkState(column) == QtCore.Qt.Checked:
            self.selected_list.append([node.text(0), node.text(1), node.text(2)])
        elif node.checkState(column) == QtCore.Qt.Unchecked:
            self.selected_list.remove([node.text(0), node.text(1), node.text(2)])

    def create_item(self, node_name: str, course_id: str, chapter_id: str, has_child: bool):
        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, str(node_name))
        item.setText(1, str(course_id))
        item.setText(2, str(chapter_id))
        if has_child == True:
            item.setFlags(item.flags() | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
        else:
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(0, QtCore.Qt.Unchecked)
        return item

    def child(self, chapter_list, parrent_chapter):
        child_chapter = []
        for chapter in chapter_list:
            if chapter['pId'] == parrent_chapter['id']:
                child_chapter.append(chapter)
        return child_chapter
            
    def create_tree(self, parent_node, node_data, node_type, course_index):
        if node_type == 'course':
            tree_item = self.create_item(node_data['courseTitle'], node_data['courseInfoId'], None, True)
            parent_node.addTopLevelItem(tree_item)
            root_chapter = {'id': 0}
            child_chapter = self.child(self.course_list[course_index]['chapter'], root_chapter)
            self.create_tree(tree_item, child_chapter, 'chapter', course_index)
        elif node_type == 'chapter':
            for item in node_data:
                child_chapter = self.child(self.course_list[course_index]['chapter'], item)
                tree_item = self.create_item(item['name'], self.course_list[course_index]['courseInfoId'], item['id'], len(child_chapter) > 0)
                parent_node.addChild(tree_item)
                if len(child_chapter) > 0:
                    self.create_tree(tree_item, child_chapter, 'chapter', course_index)
    
    def download_selected(self):
        print(self.selected_list)
    
    def refresh_course_list_tree(self):
        self.refresh_course_list()
        self.TreeWidget.clear()
        for index in range(len(self.course_list)):
            self.create_tree(self.TreeWidget, self.course_list[index], 'course', index)

    def get_resource_info_from_item(self):
        course_id = self.sender().currentItem().text(1)
        chapter_id = self.sender().currentItem().text(2)
        if course_id != "None" and chapter_id != "None":
            resource_list = self.get_resource_info(course_id, chapter_id)
            self.resource_list.clear()
            for resource in resource_list:
                res_name = resource["resTitle"]
                url_base = "http://abook.hep.com.cn/ICourseFiles/"
                res_file_url = url_base + resource["resFileUrl"]
                res_logo_url = url_base + resource["picUrl"]
                logo = requests.get(res_logo_url).content
                res_logo = QtGui.QImage()
                res_logo.loadFromData(logo)
                resource_item = QtGui.QStandardItem(res_name)
                resource_item.setData(res_logo, QtCore.Qt.DecorationRole)
                resource_item.setData(res_file_url, QtCore.Qt.ToolTipRole)
                self.resource_list.appendRow(resource_item)

    def open_resource(self):
        item = self.resource_list.itemFromIndex(self.sender().currentIndex())
        url = item.data(QtCore.Qt.ToolTipRole)
        os.system("explorer " + url)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, path, settings, session):
        QtWidgets.QMainWindow.__init__(self)
        course_tree_widget = CourseTreeWidget(path, settings, session)

        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(course_tree_widget)
        
        main_frame = QtWidgets.QWidget()
        main_frame.setLayout(main_layout)
        self.setCentralWidget(main_frame)

        self.setWindowTitle("ABookDownloader Dev")
        self.resize(1920, 1080)


if __name__ == "__main__":
    app = QtWidgets.QApplication(os.sys.argv)
    user = ABookLogin('./temp/user_info.json')
    settings = Settings('./temp/settings.json')
    abook = MainWindow('./temp/', settings, user)
    abook.show()
    sys.exit(app.exec_())

