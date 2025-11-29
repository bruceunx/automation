import sys
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

from PySide6.QtCore import QUrl, Slot
from PySide6.QtNetwork import QNetworkCookie
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView

COOKIE_PATH = "xhs.json"

TEST_IMAGE = "test.jpg"
TEST_VIDEO = "test.mp4"


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
        self.browser.load(QUrl("https://creator.xiaohongshu.com"))

        self.resize(1200, 700)
        self.setWindowTitle("测试自动化")
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
                    cookie, QUrl("https://www.xiaohongshu.com"))

    def handle_upload(self):
        with open(COOKIE_PATH, "w") as file:
            json.dump(self.cookies, file)
        self.run_playwright()

    def run_playwright(self):

        # need title, author, content, image, qrcode

        if Path(COOKIE_PATH).exists():
            with open(COOKIE_PATH, "r") as file:
                _cookies = json.load(file)
        else:
            print("Login first!!!")
            return

        # publish video
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.context.add_cookies(_cookies)
            page.goto("https://creator.xiaohongshu.com/publish/publish")

            page.set_input_files("input.upload-input", TEST_VIDEO)

            page.locator("input.el-input__inner").nth(0).fill(
                "beautiful image title")

            page.locator("div.topic-container").click()

            page.type(
                "div.topic-container",
                "beautiful image is coming",
            )

            is_checked = False
            if is_checked is False:
                page.locator("div.flexbox.mt12 div label").nth(1).click()
            page.locator("button.publishBtn").click()
            page.wait_for_timeout(2000)
            print("发布成功")
            browser.close()

        # publish image
        # with sync_playwright() as p:
        #     browser = p.chromium.launch(headless=False)
        #     page = browser.new_page()
        #     page.context.add_cookies(_cookies)
        #     page.goto("https://creator.xiaohongshu.com/publish/publish")
        #
        #     second_creator_tab = page.locator('div.creator-tab').nth(1)
        #     second_creator_tab.click()
        #     page.set_input_files("input.upload-input", TEST_IMAGE)
        #
        #     page.locator("input.el-input__inner").nth(0).fill(
        #         "beautiful image title")
        #
        #     page.locator("div.topic-container").click()
        #
        #     page.type(
        #         "div.topic-container",
        #         "beautiful image is coming",
        #     )
        #
        #     is_checked = False
        #     if is_checked is False:
        #         page.locator("div.flexbox.mt12 div label").nth(1).click()
        #     page.locator("button.publishBtn").click()
        #     page.wait_for_timeout(2000)
        #     print("发布成功")
        #     browser.close()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
