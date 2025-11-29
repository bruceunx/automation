import json
from pathlib import Path
from typing import Callable

from playwright.sync_api import sync_playwright

from PySide6.QtCore import QUrl, Slot
from PySide6.QtNetwork import QNetworkCookie
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWidgets import QDialog, QMessageBox, QPushButton, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView

TEST_IMAGE = "test.jpg"
TEST_VIDEO = "test.mp4"

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def automation_bili(publish_url: str, cookies: list):
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=EDGE_PATH, headless=True)
        page = browser.new_page()
        page.context.add_cookies(cookies)
        page.goto(publish_url)
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

        page.on("filechooser", handle_file_chooser)

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
        browser.close()


def automation_zh_image(publish_url: str, cookies: list):
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=EDGE_PATH, headless=False)
        page = browser.new_page()
        page.context.add_cookies(cookies)
        page.goto(publish_url)

        page.click(".Input.i7cW1UcwT6ThdhTakqFm")
        page.type(".Input.i7cW1UcwT6ThdhTakqFm", "sample video")
        page.click("div.DraftEditor-root")
        page.type("div.DraftEditor-root", "sample video content")

        page.set_input_files("input[type='file']", TEST_IMAGE)
        page.set_input_files("input.UploadPicture-input", TEST_IMAGE)

        page.click("button.css-1gtqxw0")
        page.wait_for_selector('input[aria-label="搜索话题"]')
        page.type('input[aria-label="搜索话题"]', "1FD")
        page.wait_for_selector("div.css-ogem9c")
        page.click("div.css-ogem9c button:first-child")

        page.click('button:has-text("发布")')

        page.wait_for_timeout(3000)
        page.screenshot(path="zh_image.png")
        browser.close()


def automation_zh_video(publish_url: str, cookies: list):
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=EDGE_PATH, headless=False)
        page = browser.new_page()
        page.context.add_cookies(cookies)

        page.goto(publish_url)

        page.set_input_files("input.VideoUploadButton-fileInput", TEST_VIDEO)

        page.wait_for_selector('div:has-text("上传成功")')

        #######################################################################
        #
        page.click("div.VideoUploadForm-imageEditButton")

        page.wait_for_selector("div.VideoCoverEditor-Modal")
        page.click("div.css-fmjg5z")

        page.set_input_files("input[type='file'].css-1s4ntcx", TEST_IMAGE)
        page.wait_for_selector("button:has-text('确认选择')")
        page.click("button:has-text('确认选择')")
        page.wait_for_timeout(1000)
        page.fill('input[placeholder="输入视频标题"]', "New video title")

        page.click(".VideoUploadForm-input.VideoUploadForm-input--multiline")
        page.type(
            ".VideoUploadForm-input.VideoUploadForm-input--multiline", "video content"
        )

        #
        page.click("button#Popover8-toggle.Button")
        page.wait_for_selector("div#Popover8-content")

        # button_text = '科技数码'
        #
        # page.click(f'div.Select-list.VideoUploadForm-selectList button:has-text("{button_text}")')
        page.click("div#Popover8-content button:nth-of-type(2)")

        page.wait_for_selector("button#Popover10-toggle.Button")
        page.click("button#Popover10-toggle.Button")

        page.wait_for_selector("div#Popover10-content")

        page.click("div#Popover10-content button:nth-of-type(2)")

        page.click("button.TopicInputAlias-placeholderButton")

        page.type("div.TopicInputAlias-autocomplete", "1FD")

        page.wait_for_selector("div.AutoComplete-menu")
        page.click("div.AutoComplete-menu div:first-child")

        page.click("label.VideoUploadForm-radioLabel")

        page.wait_for_timeout(3000)
        page.click('button:has-text("发布视频")')
        page.wait_for_timeout(3000)
        page.screenshot(path="zh_video.png")
        browser.close()


def automation_wx_image(publish_url: str, cookies: list):
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=EDGE_PATH, headless=False)
        page = browser.new_page()
        page.context.add_cookies(cookies)
        page.goto(publish_url)

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

        second_li_selector = ".pop-opr__group.js_cover_null_pop ul > li:nth-child(2)"

        new_page.click(second_li_selector)
        new_page.wait_for_selector(
            "a.weui-desktop-menu__link.weui-desktop-menu__link_current", timeout=10000
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
        browser.close()


def automation_xg_video(publish_url: str, cookies: list):
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=EDGE_PATH, headless=True)
        page = browser.new_page()
        page.context.add_cookies(cookies)
        page.goto(publish_url)

        page.click("svg.close")
        page.set_input_files('input[type="file"]', TEST_VIDEO)
        page.wait_for_function(
            "document.querySelector('.status') && document.querySelector('.status').innerText === '上传成功'"
        )
        page.click("div.mentionText")
        page.type("div.mentionText", "sample video")
        page.click("div.m-xigua-upload")
        page.click("li:has-text('本地上传')")
        page.set_input_files("div.byte-upload input[type='file']", TEST_IMAGE)
        try:
            page.wait_for_selector("div.clip-btn-content", timeout=2000)
            page.click("div.clip-btn-content")
        except Exception:
            pass
        page.wait_for_selector("button.btn-sure")
        page.click("button.btn-sure")
        page.click("div.footer button:has-text('确定')")
        page.wait_for_selector("div.m-xigua-upload div.bg")

        checkbox = page.locator(
            "label.byte-checkbox:has-text('同步到抖音') input[type='checkbox']"
        )
        if checkbox.is_checked():
            page.click("label.byte-checkbox")
        page.click("button.action-footer-btn")
        page.wait_for_timeout(3000)
        page.screenshot(path="xg.png")
        browser.close()


ENGINE_DATA: dict[str, dict[str, str | Callable]] = {
    "bili": {
        "cookie_path": "bili.json",
        "login_url": "https://member.bilibili.com/platform/home",
        "cookie_url": "https://member.bilibili.com",
        "publish_url_image": "https://t.bilibili.com",
        "fn_publish_image": automation_bili,
    },
    "zh": {
        "cookie_path": "zh.json",
        "login_url": "https://www.zhihu.com/creator",
        "cookie_url": "https://www.zhihu.com/creator",
        "publish_url_image": "https://zhuanlan.zhihu.com/write",
        "publish_url_video": "https://www.zhihu.com/zvideo/upload-video",
        "fn_publish_image": automation_zh_image,
        "fn_publish_video": automation_zh_video,
    },
    "wx": {
        "cookie_path": "wx.json",
        "login_url": "https://mp.weixin.qq.com",
        "cookie_url": "https://mp.weixin.qq.com/",
        "publish_url_image": "https://mp.weixin.qq.com/",
        "fn_publish_image": automation_wx_image,
    },
    "xg": {
        "cookie_path": "xg.json",
        "login_url": "https://studio.ixigua.com",
        "cookie_url": "https://studio.ixigua.com/",
        "publish_url_video": "https://studio.ixigua.com/upload?from=post_article",
        "fn_publish_video": automation_xg_video,
    },
}


class Engine(QDialog):
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
        QMessageBox {
            background-color: #353535;
            color: #ffffff;
            font: 14pt "Arial";
        }

        QMessageBox QPushButton {
            background-color: #555555;
            color: #ffffff;
            border: 1px solid #888888;
            padding: 5px 10px;
            font: 12pt "Arial";
        }

        QMessageBox QPushButton:hover {
            background-color: #777777;
        }

        QMessageBox QPushButton:pressed {
            background-color: #aaaaaa;
        }
    """

    def __init__(self, tag: str = "", video: bool = False):
        super(Engine, self).__init__()

        self._engine_data = ENGINE_DATA[tag]
        self._publish_url = (
            self._engine_data["publish_url_video"]
            if video
            else self._engine_data["publish_url_image"]
        )

        self._auto_fn = (
            self._engine_data["fn_publish_video"]
            if video
            else self._engine_data["fn_publish_image"]
        )

        self.cookies: list[dict[str, str]] = []

        self.browser = QWebEngineView()
        self.page = QWebEnginePage(self)
        self.browser.setPage(self.page)

        layout = QVBoxLayout()
        layout.addWidget(self.browser)

        self.setLayout(layout)

        self.browser.loadFinished.connect(self.on_page_load)

        profile = self.browser.page().profile()

        self.cookie_store = profile.cookieStore()

        self.cookie_store.cookieAdded.connect(self.cookies_callback)

        self.load_cookie()

        btn = QPushButton("测试上传(需要先登录)")
        layout.addWidget(btn)

        btn.clicked.connect(self.handle_upload)

        self.browser.load(self._engine_data["login_url"])  # type: ignore

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
        name = cookie.name().data().decode("utf-8")
        value = cookie.value().data().decode("utf-8")
        domain = cookie.domain()
        path = cookie.path()
        self.cookies.append(
            {
                "name": name,
                "value": value,
                "domain": domain,
                "path": path,
            }
        )

    def load_cookie(self):
        if Path(self._engine_data["cookie_path"]).exists():
            with open(self._engine_data["cookie_path"], "r") as file:
                _cookies = json.load(file)
            for _cookie in _cookies:
                cookie = QNetworkCookie()
                cookie.setName(_cookie["name"].encode("utf-8"))
                cookie.setValue(_cookie["value"].encode("utf-8"))
                cookie.setDomain(_cookie["domain"])
                cookie.setPath(_cookie["path"])
                self.cookie_store.setCookie(
                    cookie, QUrl(self._engine_data["cookie_url"])
                )

    def handle_upload(self):
        with open(self._engine_data["cookie_path"], "w") as file:
            json.dump(self.cookies, file)
        self.run_playwright()

    def run_playwright(self):
        if Path(self._engine_data["cookie_path"]).exists():
            with open(self._engine_data["cookie_path"], "r") as file:
                _cookies = json.load(file)
        else:
            QMessageBox.critical(self, "错误", "需要先登录!!!")
            return
        if not Path(EDGE_PATH).exists():
            QMessageBox.critical(self, "错误", "微软浏览器地址错误!")
            return
        self._auto_fn(self._publish_url, _cookies)
        QMessageBox.information(self, "成功", "成功发布!")
