from PySide6.QtGui import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from components.publishaccountlist import PublishAccountList
from utils.accounttype import PublishAccountType


class PublishAccounts(QWidget):

    Style = """
    #content {
        background-color: #fff;
    }
    #head_frame QPushButton {
        padding: 5px;
        font-weight: bold;
        color: #1789FC;
        background-color: #eee;
        border-radius: 10px;
        font-size: 14px;
    }
    #head_frame QPushButton:hover,QPushButton:pressed {
        background-color: #ddd;
    }
    #hline {
        background-color: #eeeeee;
        border: none;
        max-height: 1px;
    }
    """

    def __init__(self, parent=None):
        super(PublishAccounts, self).__init__(parent)

        self._accounts = []
        self.addComponents()
        self.addStyle()
        self.setFixedWidth(300)

    def addComponents(self):
        self.setLayout(QVBoxLayout())
        content = QFrame()
        content.setLayout(QVBoxLayout())
        content.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        content.setObjectName("content")
        self.layout().addWidget(content)

        head_frame = QFrame()
        head_frame.setLayout(QHBoxLayout())
        head_frame.setObjectName("head_frame")

        content.layout().addWidget(head_frame)

        self.choose_group_btn = QPushButton("选择分组")
        self.choose_user_btn = QPushButton("添加账号")
        self.user_last_btn = QPushButton("选择记忆")

        head_frame.layout().addWidget(self.choose_group_btn)
        head_frame.layout().addWidget(self.choose_user_btn)
        head_frame.layout().addWidget(self.user_last_btn)

        hline = QFrame()
        hline.setObjectName("hline")
        hline.setFrameShape(QFrame.HLine)
        hline.setFrameShadow(QFrame.Sunken)
        content.layout().addWidget(hline)

        self.account_list = PublishAccountList(PublishAccountType.Article)
        content.layout().addWidget(self.account_list)

        self.layout().setContentsMargins(0, 0, 0, 0)

    def addStyle(self):
        self.setStyleSheet(self.Style)

    def addConnections(self):
        pass
