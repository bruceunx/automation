import sys
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

from PySide6.QtCore import QUrl, Slot
from PySide6.QtNetwork import QNetworkCookie
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtWebEngineWidgets import QWebEngineView

COOKIE_PATH = "wx.json"

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
        self.browser.load(QUrl("https://mp.weixin.qq.com"))

        self.resize(1200, 700)
        self.setWindowTitle("测试自动化")
        self.setStyleSheet(self.Style)

    def on_page_load(self):
        print("page loaded")

    @Slot(QNetworkCookie)
    def cookies_callback(self, cookie):
        name = cookie.name().data().decode("utf-8")
        value = cookie.value().data().decode("utf-8")
        domain = cookie.domain()
        path = cookie.path()
        # Store cookie details in a dictionary
        self.cookies.append(
            {
                "name": name,
                "value": value,
                "domain": domain,
                "path": path,
            }
        )

    def load_cookie(self):
        if Path(COOKIE_PATH).exists():
            with open(COOKIE_PATH, "r") as file:
                _cookies = json.load(file)
            for _cookie in _cookies:
                cookie = QNetworkCookie()
                cookie.setName(_cookie["name"].encode("utf-8"))
                cookie.setValue(_cookie["value"].encode("utf-8"))
                cookie.setDomain(_cookie["domain"])
                cookie.setPath(_cookie["path"])
                self.cookie_store.setCookie(cookie, QUrl("https://mp.weixin.qq.com/"))

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

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.context.add_cookies(_cookies)
            page.goto("https://mp.weixin.qq.com/")

            page.click("div.new-creation__menu > div:nth-of-type(2)")

            new_page = page.context.wait_for_event("page")
            new_page.wait_for_load_state("load")

            new_page.click("div#js_title_main")
            new_page.type("div#js_title_main", "the second post")

            new_page.click("div#js_author_area")
            new_page.type("div#js_author_area", "admin")

            new_page.click("div#edui1_iframeholder")
            new_page.type("div#edui1_iframeholder", "the second post is coming")

            new_page.hover("#js_cover_area")
            new_page.wait_for_selector(".pop-opr__group.js_cover_null_pop")

            second_li_selector = (
                ".pop-opr__group.js_cover_null_pop ul > li:nth-child(2)"
            )

            new_page.click(second_li_selector)
            new_page.wait_for_selector(
                "a.weui-desktop-menu__link.weui-desktop-menu__link_current",
                timeout=10000,
            )
            new_page.click("a.weui-desktop-menu__link.weui-desktop-menu__link_current")

            def handle_file_chooser(file_chooser):
                file_chooser.set_files(TEST_IMAGE)

            new_page.on("filechooser", handle_file_chooser)
            new_page.click(
                "div.js_upload_btn_container.weui-desktop-upload-input__wrp.webuploader-container"
            )

            new_page.wait_for_timeout(5000)
            new_page.click(
                "button.weui-desktop-btn.weui-desktop-btn_primary:has-text('下一步')"
            )
            new_page.wait_for_timeout(2000)
            new_page.click(
                "button.weui-desktop-btn.weui-desktop-btn_primary:has-text('完成')"
            )
            new_page.wait_for_timeout(3000)
            new_page.wait_for_selector("button.mass_send", timeout=10000)
            new_page.click("button.mass_send")

            #############################################################
            # first post
            # new_page.wait_for_selector(
            #     'a.btn.btn_primary.js_btn:has-text("同意以上声明")', timeout=10000)
            #
            # new_page.click('a.btn.btn_primary.js_btn')

            new_page.wait_for_selector("div.mass-send__td")

            if new_page.query_selector(
                "label.weui-desktop-form__label:has-text('分组通知')"
            ):
                new_page.click("div.mass-send__timer-wrp")

            new_page.wait_for_timeout(1000)
            new_page.click(
                "button.weui-desktop-btn.weui-desktop-btn_primary:has-text('发表')"
            )

            new_page.wait_for_timeout(1000)  # Adjust wait time as necessary
            new_page.click(
                "button.weui-desktop-btn.weui-desktop-btn_primary:has-text('继续发表')"
            )
            new_page.wait_for_selector(".js_qrcode", timeout=5000)

            image_element = new_page.query_selector(".js_qrcode")
            if image_element:
                image_element.screenshot(path="wx_screenshot.png")
            new_page.wait_for_timeout(3000)
            print("发布成功")
            browser.close()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
