from PySide6.QtCore import QSize
from PySide6.QtGui import QColor, QIcon, Qt
from PySide6.QtWidgets import QButtonGroup, QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QPushButton, QToolButton, QWidget


class HeaderBar(QWidget):

    Style = """
    #content_frame{
        font-size: 12pt;
        font-family: "Microsoft YaHei";
        color: #e0e0e0;
        background-color: rgba(11, 42, 73, 200);
    }
    #title_label{
        font-size: 17pt;
        font-weight: bold;
    }
    #menu_frame QToolButton{
        background-color: rgba(11, 42, 73, 0);
        padding: 5px 10px;
        border: none;
        font-size: 12pt;
    }
    #menu_frame QToolButton:hover{
        background-color: rgba(31, 62, 93, 200);
    }
    #menu_frame QToolButton:pressed{
        background-color: rgba(31, 62, 93, 200);
    }
    #menu_frame QToolButton:checked{
        background-color: rgba(31, 62, 93, 200);
    }
    #user_frame QPushButton {
        border: none;
        padding: 2px;
        background-color: transparent;
    }
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.addComponents()
        self.addStyles()
        self.addConnects()
        self.afterInit()

        self.setGlow()
        self.alter_msg = []

    def setGlow(self):
        self.effect = QGraphicsDropShadowEffect(self)
        self.effect.setColor(QColor(135, 206, 235, 255))
        self.effect.setBlurRadius(20)
        self.effect.setOffset(0, 0)
        self.setGraphicsEffect(self.effect)

    def addComponents(self):
        self.setLayout(QHBoxLayout())
        content_frame = QFrame()
        content_frame.setLayout(QHBoxLayout())
        content_frame.setObjectName("content_frame")
        self.layout().addWidget(content_frame)

        title_label = QLabel(" 引流平台")
        title_label.setObjectName("title_label")
        content_frame.layout().addWidget(title_label)

        menu_frame = QFrame()
        menu_frame.setLayout(QHBoxLayout())
        menu_frame.setObjectName("menu_frame")
        menu_frame.layout().setAlignment(Qt.AlignmentFlag.AlignLeft)
        content_frame.layout().addWidget(menu_frame, 0,
                                         Qt.AlignmentFlag.AlignHCenter)

        self.manager_btn = QToolButton()
        self.manager_btn.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.manager_btn.setText("管理中心")
        self.manager_btn.setIcon(QIcon("assets/globe.svg"))
        self.manager_btn.setIconSize(QSize(30, 30))
        menu_frame.layout().addWidget(self.manager_btn)

        self.accounts_btn = QToolButton()
        self.accounts_btn.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.accounts_btn.setText("账户中心")
        self.accounts_btn.setIcon(QIcon("assets/users.svg"))
        self.accounts_btn.setIconSize(QSize(30, 30))
        menu_frame.layout().addWidget(self.accounts_btn)

        self.publish_btn = QToolButton()
        self.publish_btn.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.publish_btn.setText("一键发布")
        self.publish_btn.setIcon(QIcon("assets/feather.svg"))
        self.publish_btn.setIconSize(QSize(30, 30))
        menu_frame.layout().addWidget(self.publish_btn)

        self.menu_group = QButtonGroup()
        self.menu_group.addButton(self.manager_btn, 0)
        self.menu_group.addButton(self.accounts_btn, 1)
        self.menu_group.addButton(self.publish_btn, 2)

        for button in self.menu_group.buttons():
            button.setCheckable(True)
            button.setFixedHeight(60)
        self.manager_btn.setChecked(True)

        user_frame = QFrame()
        user_frame.setObjectName("user_frame")
        user_frame.setLayout(QHBoxLayout())
        user_frame.layout().setAlignment(Qt.AlignmentFlag.AlignRight)
        content_frame.layout().addWidget(user_frame)

        self.user_btn = QPushButton()
        self.user_btn.setIcon(QIcon('assets/user.svg'))
        self.user_btn.setIconSize(self.user_btn.sizeHint())

        self.logout_btn = QPushButton()
        self.logout_btn.setIcon(QIcon('assets/log-out.svg'))
        self.logout_btn.setIconSize(self.logout_btn.sizeHint())

        user_frame.layout().addWidget(self.user_btn)
        user_frame.layout().addWidget(self.logout_btn)

        self.setFixedHeight(60)
        user_frame.layout().setSpacing(2)
        user_frame.layout().setContentsMargins(0, 0, 0, 0)
        content_frame.layout().setContentsMargins(0, 0, 0, 0)
        menu_frame.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)

    def addStyles(self):
        self.setStyleSheet(self.Style)

    def addConnects(self):
        pass

    def afterInit(self):
        pass
