import sys
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

from PySide6.QtCore import QUrl, Slot
from PySide6.QtNetwork import QNetworkCookie
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QPushButton, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView

COOKIE_PATH = "zh.json"

TEST_IMAGE = "test.jpg"
TEST_VIDEO = "test.mp4"

EDGE_PATH = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


class MainWindow(QMainWindow):

    Style = """
        *{
            font-family: "Microsoft YaHei";
            font-size: 12pt;
            color: #e0e0e0;
        }
        QPushButton {
            border: none;
            background-color: #6c757d;
            font-size:12pt;
            padding: 5px 30px 5px 5px;
            border-radius: 5px;
        }

        QPushButton::hover {
            background-color: #778899;
        }

        QPushButton::pressed {
            background-color: #36454f;
        }
        
    """

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("测试自动化")
        self.cookies = []
        # Create a WebEngine view
        self.browser = QWebEngineView()
        self.page = QWebEnginePage(self)
        self.browser.setPage(self.page)
        # Load the Ixigua Studio URL
        # self.browser.setUrl(QUrl("https://www.zhihu.com/creator"))

        # Add the browser to the window
        layout = QVBoxLayout()
        layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Set up the callback for handling file input requests
        # self.browser.page().fileDialog = self.handle_file_upload

        # Load the page and set input text when the page loads
        self.browser.loadFinished.connect(self.on_page_load)

        profile = self.browser.page().profile()

        self.cookie_store = profile.cookieStore()

        self.cookie_store.cookieAdded.connect(self.cookies_callback)

        self.load_cookie()

        btn = QPushButton("测试上传(需要先登录)")
        layout.addWidget(btn)

        btn.clicked.connect(self.handle_upload)
        self.browser.load(QUrl("https://www.zhihu.com/creator"))

        self.resize(1200, 700)
        self.setStyleSheet(self.Style)

    def on_page_load(self):
        print('page loaded')

    @Slot(QNetworkCookie)
    def cookies_callback(self, cookie):
        name = cookie.name().data().decode('utf-8')
        value = cookie.value().data().decode('utf-8')
        domain = cookie.domain()
        path = cookie.path()
        # Store cookie details in a dictionary
        self.cookies.append({
            "name": name,
            "value": value,
            "domain": domain,
            "path": path,
        })

    def load_cookie(self):
        if Path(COOKIE_PATH).exists():
            with open(COOKIE_PATH, "r") as file:
                _cookies = json.load(file)
            for _cookie in _cookies:
                cookie = QNetworkCookie()
                cookie.setName(_cookie["name"].encode('utf-8'))
                cookie.setValue(_cookie["value"].encode('utf-8'))
                cookie.setDomain(_cookie["domain"])
                cookie.setPath(_cookie["path"])
                self.cookie_store.setCookie(
                    cookie, QUrl("https://www.zhihu.com/creator"))

    def handle_upload(self):
        with open(COOKIE_PATH, "w") as file:
            json.dump(self.cookies, file)

        # automate image
        self.run_playwright()
        # automate video
        self.run_playwright_upload_video()

    def run_playwright(self):

        if Path(COOKIE_PATH).exists():
            with open(COOKIE_PATH, "r") as file:
                _cookies = json.load(file)
        else:
            print("Login first!!!")
            return

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.context.add_cookies(_cookies)
            page.goto("https://zhuanlan.zhihu.com/write")

            page.click('.Input.i7cW1UcwT6ThdhTakqFm')
            page.type(".Input.i7cW1UcwT6ThdhTakqFm", "sample video")
            page.click('div.DraftEditor-root')
            page.type('div.DraftEditor-root', "sample video content")

            page.set_input_files("input[type='file']", TEST_IMAGE)
            page.set_input_files("input.UploadPicture-input", TEST_IMAGE)

            page.click('button.css-1gtqxw0')
            page.wait_for_selector('input[aria-label="搜索话题"]')
            page.type('input[aria-label="搜索话题"]', "1FD")
            page.wait_for_selector('div.css-ogem9c')
            page.click('div.css-ogem9c button:first-child')

            page.click('button:has-text("发布")')

            page.wait_for_timeout(3000)
            page.screenshot(path="zh_image.png")
            print("发布成功")
            browser.close()

    def run_playwright_upload_video(self):

        if Path(COOKIE_PATH).exists():
            with open(COOKIE_PATH, "r") as file:
                _cookies = json.load(file)
        else:
            QMessageBox.critical(self, "错误", "需要先登录!!!")
            return
        if not Path(EDGE_PATH).exists():
            QMessageBox.critical(self, "错误", "微软浏览器地址错误!")
            return
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=EDGE_PATH,
                                        headless=True)
            page = browser.new_page()
            page.context.add_cookies(_cookies)
            page.goto("https://www.zhihu.com/zvideo/upload-video")

            page.set_input_files('input.VideoUploadButton-fileInput',
                                 TEST_VIDEO)

            page.wait_for_selector('div:has-text("上传成功")')

            #######################################################################
            #
            page.click("div.VideoUploadForm-imageEditButton")

            page.wait_for_selector('div.VideoCoverEditor-Modal')
            page.click('div.css-fmjg5z')

            page.set_input_files("input[type='file'].css-1s4ntcx", TEST_IMAGE)
            page.wait_for_selector("button:has-text('确认选择')")
            page.click("button:has-text('确认选择')")
            page.wait_for_timeout(1000)
            page.fill('input[placeholder="输入视频标题"]', 'New video title')

            page.click(
                ".VideoUploadForm-input.VideoUploadForm-input--multiline")
            page.type(
                ".VideoUploadForm-input.VideoUploadForm-input--multiline",
                "video content")

            #
            page.click('button#Popover8-toggle.Button')
            page.wait_for_selector('div#Popover8-content')

            # button_text = '科技数码'
            #
            # page.click(f'div.Select-list.VideoUploadForm-selectList button:has-text("{button_text}")')
            page.click('div#Popover8-content button:nth-of-type(2)')

            page.wait_for_selector('button#Popover10-toggle.Button')
            page.click('button#Popover10-toggle.Button')

            page.wait_for_selector('div#Popover10-content')

            page.click('div#Popover10-content button:nth-of-type(2)')

            page.click("button.TopicInputAlias-placeholderButton")

            page.type('div.TopicInputAlias-autocomplete', "1FD")

            page.wait_for_selector('div.AutoComplete-menu')
            page.click('div.AutoComplete-menu div:first-child')

            page.click('label.VideoUploadForm-radioLabel')
            page.click('button:has-text("发布视频")')

            page.wait_for_timeout(3000)
            page.screenshot(path="zh_video.png")
            print("发布成功")
            browser.close()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
