import sys
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

from PySide6.QtCore import QUrl, Slot
from PySide6.QtNetwork import QNetworkCookie
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QPushButton, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView

COOKIE_PATH = "bili.json"

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
        self.cookies = []

        self.browser = QWebEngineView()
        self.page = QWebEnginePage(self)
        self.browser.setPage(self.page)

        # Add the browser to the window
        layout = QVBoxLayout()
        layout.addWidget(self.browser)

        self.browser.setUrl(QUrl("https://member.bilibili.com/platform/home"))
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.browser.loadFinished.connect(self.on_page_load)

        profile = self.browser.page().profile()

        self.cookie_store = profile.cookieStore()

        self.cookie_store.cookieAdded.connect(self.cookies_callback)

        self.load_cookie()

        btn = QPushButton("测试上传(需要先登录)")
        layout.addWidget(btn)

        btn.clicked.connect(self.handle_upload)

        self.browser.load(QUrl("https://member.bilibili.com/platform/home"))

        self.resize(1200, 700)
        self.setWindowTitle("测试自动化")
        self.setStyleSheet(self.Style)

    def on_page_load(self):
        pass

    @Slot(QNetworkCookie)
    def cookies_callback(self, cookie):
        name = cookie.name().data().decode('utf-8')
        value = cookie.value().data().decode('utf-8')
        domain = cookie.domain()
        path = cookie.path()
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
                    cookie, QUrl("https://member.bilibili.com"))

    def handle_upload(self):
        with open(COOKIE_PATH, "w") as file:
            json.dump(self.cookies, file)

        self.run_playwright()

    def run_playwright(self):
        if Path(COOKIE_PATH).exists():
            with open(COOKIE_PATH, "r") as file:
                _cookies = json.load(file)
        else:
            print("Login first!!!")
            return
        if not Path(EDGE_PATH).exists():
            QMessageBox.critical(self, "错误", "微软浏览器地址错误!")
            return
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=EDGE_PATH,
                                        headless=True)
            page = browser.new_page()
            page.context.add_cookies(_cookies)
            page.goto("https://t.bilibili.com/")
            page.click("input.bili-dyn-publishing__title__input")
            page.type(
                "input.bili-dyn-publishing__title__input",
                "first post",
            )
            page.click("div.bili-rich-textarea__inner")
            page.type(
                "div.bili-rich-textarea__inner",
                "first post is coming",
            )

            def handle_file_chooser(file_chooser):
                file_chooser.set_files(TEST_IMAGE)

            page.on('filechooser', handle_file_chooser)

            page.click("div.bili-dyn-publishing__tools__item.pic")
            page.wait_for_timeout(1000)

            page.click("div.bili-dyn-publishing__action.launcher")
            page.wait_for_selector(
                "button.bili-dyn-specification-popup__btn.bili-button.primary.bili-button--medium"
            )
            page.click(
                "button.bili-dyn-specification-popup__btn.bili-button.primary.bili-button--medium"
            )

            page.wait_for_timeout(3000)
            page.screenshot(path="bilibili.png")
            print("发布成功!")
            browser.close()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
