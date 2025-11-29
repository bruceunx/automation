import json
import base64

from PySide6.QtCore import QSize, QTimer, QUrl, Signal, Slot
from PySide6.QtGui import QCursor, QIcon, Qt
from PySide6.QtNetwork import (
    QNetworkAccessManager,
    QNetworkCookie,
    QNetworkProxy,
    QNetworkReply,
    QNetworkRequest,
)
from PySide6.QtSql import QSqlQuery
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QLabel,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
)

from models.query import check_if_user_exists, update_cookies
from utils import Platform, LOGIN_METADATA


class PlatformButton(QToolButton):
    platform_type = Signal(Platform)

    def __init__(self, platform_type: Platform, parent=None):
        super(PlatformButton, self).__init__()
        self._platform_type = platform_type
        meta_data = LOGIN_METADATA[platform_type]
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.setText(meta_data["title"])
        self.setIcon(QIcon(meta_data["icon"]))
        self.setIconSize(QSize(30, 30))

    def enterEvent(self, event) -> None:
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        return super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self.unsetCursor()
        return super().leaveEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            self.platform_type.emit(self._platform_type)
        return super().mouseReleaseEvent(event)


class AddAccount(QDialog):
    Style = """
    QLabel {
        font-size: 17px;
        font-weight: bold;
        color: #555;
    }
    QToolButton{
        padding: 5 5;
        border-radius: 5;
        background-color: transparent;
        font-size: 10pt;
        color: #555;
    }
    QToolButton:hover{
        border: 1px solid #1E90FF;
    }
    QToolButton:pressed{
        border: 1px solid #1E90FF;
    }

    """

    def __init__(self, parent=None):
        super(AddAccount, self).__init__(parent)
        self.setWindowTitle("选择添加账号")
        self.setWindowIcon(QIcon("assets/key.svg"))
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint)

        self.choose_plafform = None
        self.setFixedSize(700, 300)
        self.addComponents()
        self.addStyle()

    def addComponents(self):
        self.setLayout(QVBoxLayout())
        title = QLabel("选择平台")

        self.layout().addWidget(title, 0, Qt.AlignmentFlag.AlignTop)

        content = QFrame()
        content.setLayout(QGridLayout())
        content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        for idx, platform in enumerate(Platform):
            btn = PlatformButton(platform)
            btn.platform_type.connect(self.handleSelect)
            btn.setFixedSize(80, 80)

            row, col = divmod(idx, 5)

            content.layout().addWidget(btn, row, col)

        self.layout().addWidget(content)

    def addStyle(self):
        self.setStyleSheet(self.Style)

    @Slot(Platform)
    def handleSelect(self, value: Platform):
        self.choose_plafform = value
        self.accept()


class LoginandSave(QDialog):
    new_account = Signal(int)
    update_cookie = Signal(int, list)

    def __init__(self, platform_type: Platform, parent=None):
        super(LoginandSave, self).__init__(parent)
        self.setWindowTitle("登录账号")
        self.setWindowIcon(QIcon("assets/key.svg"))
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint)
        self.cookies: dict[str, dict] = {}
        self.setFixedSize(1200, 500)
        self.addComponents()

        self._platform = platform_type
        self._meta_data = LOGIN_METADATA[platform_type]

        self._timer = QTimer()
        self._timer.timeout.connect(self.check_element_existence)

        self.browser.setUrl(QUrl(self._meta_data["url"]))

        self._network_manager = QNetworkAccessManager()
        self._network_manager.setProxy(QNetworkProxy(QNetworkProxy.ProxyType.NoProxy))
        self._network_manager.finished.connect(self._on_finished)

    def addComponents(self):
        self.setLayout(QVBoxLayout())

        self.browser = QWebEngineView()
        self.page = QWebEnginePage(self)
        self.browser.setPage(self.page)
        self.layout().addWidget(self.browser)
        self.cookie_store = self.page.profile().cookieStore()
        self.cookie_store.deleteAllCookies()
        self.browser.loadFinished.connect(self.on_page_load)

        self.cookie_store = self.page.profile().cookieStore()
        self.cookie_store.cookieAdded.connect(self.cookies_callback)
        self._close_delay = QTimer()
        self._close_delay.timeout.connect(self.close)

    def on_page_load(self):
        self._timer.start(1000)

    @Slot(QNetworkCookie)
    def cookies_callback(self, cookie):
        name = cookie.name().data().decode("utf-8")
        value = cookie.value().data().decode("utf-8")
        domain = (
            ".bilibili.com" if self._platform == Platform.BiliBili else cookie.domain()
        )
        path = cookie.path()
        self.cookies[name] = {
            "name": name,
            "value": value,
            "domain": domain,
            "path": path,
        }

    @Slot()
    def check_element_existence(self):
        self.page.runJavaScript(
            self._meta_data["script"], 0, self.handle_element_existence_result
        )

    def handle_element_existence_result(self, result):
        account_data = json.loads(result)
        if len(account_data["name"]) != 0:
            self._timer.stop()
            self._account_data = account_data
            self._close_delay.start(2000)
            self._network_manager.get(QNetworkRequest(QUrl(account_data["avatar"])))

    def _on_finished(self, reply):
        if reply.error() == QNetworkReply.NoError:
            image_data = reply.readAll()
            base64_image = base64.b64encode(image_data).decode("utf-8")
        else:
            base64_image = None

        cookies = [value for value in self.cookies.values()]

        if check_if_user_exists(self._account_data["name"], self._platform.value):
            idx = update_cookies(
                self._account_data["name"], self._platform.value, json.dumps(cookies)
            )
            if idx is not None:
                self.update_cookie.emit(idx, cookies)
        else:
            query = QSqlQuery()
            query.prepare("""
                INSERT INTO User (name, platform, cookies, icon_raw)
                VALUES (?, ?, ?, ?)
                """)
            query.addBindValue(self._account_data["name"])
            query.addBindValue(self._platform.value)
            query.addBindValue(json.dumps(cookies))
            query.addBindValue(base64_image)
            query_success = query.exec_()
            if not query_success:
                print(f"Query execution failed: {query.lastError().text()}")
            else:
                db_id = query.lastInsertId()
                self.new_account.emit(db_id)
        self.accept()
