import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from PySide6.QtCore import QUrl, Slot
from PySide6.QtNetwork import QNetworkCookie
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView

COOKIE_PATH = "xg.json"

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
        # self.browser.setUrl(QUrl("https://studio.ixigua.com/"))

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
        self.browser.load(QUrl("https://studio.ixigua.com"))

        self.resize(1200, 700)
        self.setWindowTitle("测试自动化")
        self.setStyleSheet(self.Style)

    def on_page_load(self):
        js_code = """
            var dialog = document.querySelector('div[class="Dialog-container"]');
            if(dialog){
                dialog.remove();
            }
            document.body.style.overflow = 'auto'; 
        """
        self.browser.page().runJavaScript(js_code)
        print("page loaded")

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
                self.cookie_store.setCookie(cookie,
                                            QUrl("https://studio.ixigua.com/"))

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
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.context.add_cookies(_cookies)
            page.goto("https://studio.ixigua.com/upload?from=post_article")
            page.click("svg.close")
            page.set_input_files('input[type="file"]', TEST_VIDEO)
            page.wait_for_function(
                "document.querySelector('.status') && document.querySelector('.status').innerText === '上传成功'"
            )
            page.click("div.mentionText")
            page.type("div.mentionText", "sample video")
            page.click("div.m-xigua-upload")
            page.click("li:has-text('本地上传')")
            page.set_input_files("div.byte-upload input[type='file']",
                                 TEST_IMAGE)
            try:
                page.wait_for_selector("div.clip-btn-content", 2000)
                page.click("div.clip-btn-content")
            except Exception:
                pass
            page.wait_for_selector("button.btn-sure")
            page.click("button.btn-sure")
            page.click("div.footer button:has-text('确定')")
            page.wait_for_selector("div.m-xigua-upload div.bg")
            page.uncheck("label.byte-checkbox input[type='checkbox']")
            page.click("button.action-footer-btn")
            page.wait_for_timeout(3000)
            page.screenshot(path='xg.png')
            print("发布成功")
            browser.close()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
