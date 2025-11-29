import asyncio

from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QStackedWidget, QVBoxLayout, QWidget

from PySide6 import QtSvg  # noqa

from components.engine import Engine
from components.headers import HeaderBar
from models.query import get_all_users_for_tests, update_user_state
from views.homeview import HomeView
from views.publishview import PublisView
from views.userview import AccountView
from workers.headlessbrowser import TestAccountWorker


class MainView(QWidget):
    Style = """
    *{
        font-family: "Microsoft YaHei";
        font-size: 12pt;
        color: #e0e0e0;
    }
    QStackedWidget {
        background-color: #e0e0e0;
    }
    QMessageBox QPushButton {
        background-color: #7EC9F1;
        color: #fff;
        border: none;
        border-radius: 5px;
        padding: 5px 10px;
    }
    QMessageBox QPushButton:hover {
        background-color: #5AB9ED;
    }

    QMessageBox QPushButton:pressed {
        background-color: #35AAE9;
    }
    """
    active_accounts = Signal(list)
    update_account_state = Signal(int, int)
    test_progress = Signal(float)

    def __init__(self, parent=None):
        super(MainView, self).__init__(parent)
        self.setWindowTitle("引流平台")
        self.resize(1600, 800)
        self.addComponents()
        self.addStyle()
        self.addWorkers()
        self.addConnections()
        self.afterInit()

        self._test_account_count = 1
        self._test_result_count = 0

    def addComponents(self):
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        self.headerBar = HeaderBar()
        self.headerBar.setObjectName("headerBar")
        self.layout().addWidget(self.headerBar)

        content_frame = QFrame()
        content_frame.setLayout(QHBoxLayout())
        self.layout().addWidget(content_frame)

        self.stack = QStackedWidget()
        content_frame.layout().addWidget(self.stack)

        self.home_view = HomeView()
        self.account_view = AccountView()
        self.publish_view = PublisView()
        self.stack.addWidget(self.home_view)
        self.stack.addWidget(self.account_view)
        self.stack.addWidget(self.publish_view)
        #
        content_frame.layout().setContentsMargins(0, 0, 0, 0)
        content_frame.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

    def addStyle(self):
        self.setStyleSheet(self.Style)

    def addWorkers(self):
        self.headless_worker = TestAccountWorker()

    def addConnections(self):
        self.home_view.user_manager.header_bar.test_accounts_state.clicked.connect(
            self.handle_test_all_accounts)
        self.headerBar.menu_group.idClicked.connect(self.handle_menu_button)

        self.headless_worker.result.connect(self.handle_test_result)

        self.active_accounts.connect(self.headless_worker.test_all_accounts)

        self.update_account_state.connect(
            self.home_view.user_manager.model.update_user_state)

        self.test_progress.connect(
            self.home_view.user_manager.header_bar.handle_test_progress)

        self.update_account_state.connect(
            self.account_view.left_menu.handle_update_account_active)

        self.home_view.user_manager.user_table.test_user.connect(
            self.headless_worker.test_account_state)

        self.headless_worker.test_result.connect(
            self.home_view.user_manager.user_table.handle_test_account_result)

    def handle_test_all_accounts(self):
        users = get_all_users_for_tests()
        self._test_account_count = len(users)
        self._test_result_count = 0
        self.active_accounts.emit(users)

    def afterInit(self):
        self.stack.setCurrentIndex(0)

    def handle_test(self, tag: str, video: bool = False):
        engine = Engine(tag=tag, video=video)
        engine.exec()

    def closeEvent(self, event):
        self.publish_view.close()
        event.accept()
        asyncio.get_event_loop().stop()

    @Slot(int)
    def handle_menu_button(self, idx: int):
        self.stack.setCurrentIndex(idx)

    @Slot(int, int)
    def handle_test_result(self, user_id, is_active):
        self._test_result_count += 1
        if update_user_state(user_id, is_active):
            if is_active != -1:
                self.update_account_state.emit(user_id, is_active)
        self.test_progress.emit(self._test_result_count /
                                self._test_account_count)
