from PySide6.QtCore import Slot
from PySide6.QtWidgets import QHBoxLayout, QStackedLayout, QWidget

from components.leftbar import LeftBar, LeftBarType
from components.membercenter import MemeberCenter
from components.statistics import Statistic
from components.systemsetting import SystemSetting
from components.usergroup import UserGroupManager
from usercenter import UserCenter


class HomeView(QWidget):
    def __init__(self, parent=None):
        super(HomeView, self).__init__(parent)
        self.setMinimumHeight(400)
        self.addComponents()
        self.addStyle()
        self.addConnections()

    def addComponents(self):
        layout = QHBoxLayout()
        self.leftmenu = LeftBar.create_leftbar(LeftBarType.ManagerLeftBar)
        layout.addWidget(self.leftmenu)

        self.stack = QStackedLayout()

        layout.addLayout(self.stack)
        self.setLayout(layout)

        self.user_manager = UserGroupManager()

        self.stack.addWidget(self.user_manager)
        self.stack.addWidget(UserCenter())
        self.stack.addWidget(MemeberCenter())
        self.stack.addWidget(SystemSetting())
        self.stack.addWidget(Statistic())

        layout.setContentsMargins(10, 10, 10, 10)

    def addConnections(self):
        self.leftmenu.btn_groups.idClicked.connect(self.handle_switch)

    @Slot(int)
    def handle_switch(self, idx: int):
        self.stack.setCurrentIndex(idx)

    def addStyle(self):
        self.setStyleSheet("""
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
        """)
