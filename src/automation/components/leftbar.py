from enum import Enum, auto
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import QButtonGroup, QFrame, QPushButton, QVBoxLayout, QWidget


class LeftBarType(Enum):
    PublishLeftBar = auto()
    ManagerLeftBar = auto()

    @property
    def meta_data(self) -> list:
        match self:
            case LeftBarType.PublishLeftBar:
                return [
                    ("图文", "file.svg"),  # 2165bf
                    ("横版短视频", "camera.svg"),
                    ("竖版小视频", "film.svg"),
                    ("短内容", "message-square.svg"),
                    ("历史记录", "archive.svg"),
                ]
            case LeftBarType.ManagerLeftBar:
                return [
                    ("账号管理", "grid-leftbar.svg"),
                    ("用户中心", "user-d.svg"),
                    ("会员中心", "lock.svg"),
                    ("系统设置", "settings.svg"),
                    ("数据统计", "pie-chart.svg"),
                ]


class LeftBar(QWidget):
    def __init__(self, meta_data: list, parent=None):
        super(LeftBar, self).__init__(parent)
        self.meta_data = meta_data
        self.addComponents()
        self.addStyle()
        self.setFixedWidth(170)

    def addComponents(self):
        self.setLayout(QVBoxLayout())
        content = QFrame()
        content.setLayout(QVBoxLayout())
        content.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        content.setObjectName("content")
        self.layout().addWidget(content)

        self.btn_groups = QButtonGroup()
        for idx, (title, svg) in enumerate(self.meta_data):
            button = QPushButton(title)
            button.setIcon(QIcon(f"assets/{svg}"))
            button.setIconSize(QSize(15, 15))
            button.setCheckable(True)
            self.btn_groups.addButton(button, idx)
            content.layout().addWidget(button)

        self.btn_groups.button(0).setChecked(True)

        content.layout().setSpacing(0)
        content.layout().setContentsMargins(0, 10, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)

    def addStyle(self):
        self.setStyleSheet("""
        #content{
            background-color: #fff;
        }
        QPushButton {
            background-color: transparent;
            border: none;
            font-size: 14px;
            border-radius: 0;
            padding: 9 10;
            color: #555;
            text-align: left;
        }
        QPushButton:checked {
            background-color: #F7F4EA;
            color: rgba(0, 0, 200, 100);
            border-left: 2 solid rgba(0, 0, 200, 100);
        }
        """)

    @classmethod
    def create_leftbar(cls, leftbar_type: LeftBarType):
        return cls(leftbar_type.meta_data)
