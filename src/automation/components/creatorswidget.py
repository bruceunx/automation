from PySide6.QtCore import QSize, QUrl, Signal, Slot
from PySide6.QtGui import QIcon, Qt
from PySide6.QtNetwork import QNetworkCookie
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QLabel, QPushButton, QTabBar, QTabWidget, QVBoxLayout, QWidget

from components.addaccount import Platform, LOGIN_METADATA


class SingleWebTab(QWidget):

    def __init__(self, url: str, cookie_url: str, cookies: list, parent=None):
        super(SingleWebTab, self).__init__(parent)

        self.setLayout(QVBoxLayout())
        web_view = QWebEngineView()
        self.layout().addWidget(web_view) # type: ignore

        cookie_store = web_view.page().profile().cookieStore()

        for cookie in cookies:
            temp = QNetworkCookie()
            temp.setName(cookie["name"].encode("utf-8"))
            temp.setValue(cookie["value"].encode('utf-8'))
            temp.setDomain(cookie["domain"])
            temp.setPath(cookie["path"])
            cookie_store.setCookie(temp, QUrl(cookie_url))
        web_view.setUrl(url)

        self.layout().setContentsMargins(0, 0, 0, 0) # type: ignore


class ClosableTabWidget(QTabWidget):

    Style = """
        *{
            color: #666;
        }
        QTabWidget::pane {
            border: 0;
        }
        QTabBar::tab {
            background-color: transparent;
            border: 0;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
            padding: 3px 17px;
            margin: 2px;
            font-size: 13px;
        }
        QTabBar::tab:selected {
            background-color: white;
        }
        QTabBar::close-button {
            image: url("assets/x.svg");
            border: none;
            border-radius: 8px;
        }
        QTabBar::close-button:hover {
            background: lightgray;
        }

        QPushButton {
            background-color: transparent;
            border: none;
            color: #777;
            font-size: 13px;
        }
        QPushButton:hover {
            color: #ff6961;
        }
    """
    show_label = Signal(bool)
    close_account = Signal(str, Platform)
    close_all = Signal()

    def __init__(self):
        super().__init__()

        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.close_all_btn = QPushButton("关闭所有")
        self.close_all_btn.clicked.connect(self.close_all_tabs)
        self.setCornerWidget(self.close_all_btn, corner=Qt.TopRightCorner)

        self._widget_cache = []

        self.setStyleSheet(self.Style)

    @Slot(str, list, Platform)
    def add_new_tab(self, username: str, cookies: list,
                    platform_type: Platform):
        meta_data = LOGIN_METADATA[platform_type]
        url = meta_data["creator_url"]
        cookie_url = meta_data["cookie_url"]
        new_tab = SingleWebTab(url, cookie_url, cookies)
        index = self.addTab(new_tab, QIcon(meta_data["icon"]), username)
        self.setCurrentIndex(index)
        self._widget_cache.append((username, platform_type))

        tab_bar = self.tabBar()
        close_button = tab_bar.tabButton(index,
                                         QTabBar.ButtonPosition.RightSide)
        close_button.setToolTip("")
        close_button.resize(QSize(16, 16))
        self.setVisible(True)
        self.show_label.emit(False)

    def close_tab(self, index):
        self.close_account.emit(*self._widget_cache.pop(index))
        self.removeTab(index)
        if self.count() == 0:
            self.setVisible(False)
            self.show_label.emit(True)

    def close_all_tabs(self):
        self.close_all.emit()
        while self.count() > 0:
            self.removeTab(0)
        self.setVisible(False)
        self.show_label.emit(True)


class CreatorsWidget(QWidget):

    def __init__(self, parent=None):
        super(CreatorsWidget, self).__init__()

        self.setLayout(QVBoxLayout())

        self.webviews = ClosableTabWidget()
        self.layout().addWidget(self.webviews)
        self.label = QLabel("如何添加用户说明")
        self.label.setStyleSheet("""
            QLabel {
                font-size: 30px;
                color: #555;
            }
        """)
        self.layout().addWidget(self.label, 0, Qt.AlignmentFlag.AlignCenter)

        self.label.setVisible(True)
        self.webviews.setVisible(False)

        self.layout().setContentsMargins(0, 0, 0, 0)

        self.webviews.show_label.connect(self.handle_label_visible)

    @Slot(bool)
    def handle_label_visible(self, visible):
        self.label.setVisible(visible)
