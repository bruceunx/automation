from PySide6.QtGui import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QTextEdit, QVBoxLayout, QWidget

from components.articlesetting import ShortNoteSetting
from components.publishcontrol import PublishControl


class ShortNote(QWidget):

    Style = """
    #content_frame {
        background-color: #fff;
        border-top-left-radius: 20px;
        border-top-right-radius: 20px;
    }
    QTextEdit {
        border: 1 solid #ccc;
        font-size: 13px;
        color: #777;
        padding: 5px;
        border-radius: 7px;
    } 
    #content_frame QLabel {
        font-size: 14px;
        color: #777;
    }
    #setting_frame {
        background-color: #fff;
    }
    """

    def __init__(self, parent=None):
        super(ShortNote, self).__init__(parent)
        self.addComponents()
        self.addStyle()

    def addComponents(self):
        self.setLayout(QHBoxLayout())

        center_frame = QFrame()
        center_frame.setLayout(QVBoxLayout())
        self.layout().addWidget(center_frame)

        content_frame = QFrame()
        content_frame.setLayout(QVBoxLayout())
        content_frame.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        content_frame.setObjectName("content_frame")
        center_frame.layout().addWidget(content_frame)

        setting_frame = QFrame()
        setting_frame.setFixedWidth(300)
        setting_frame.setObjectName("setting_frame")
        setting_frame.setLayout(QVBoxLayout())
        self.layout().addWidget(setting_frame)

        self.setting = ShortNoteSetting()
        setting_frame.layout().addWidget(self.setting)

        content_frame.layout().addWidget(QLabel("内容"))

        self.context = QTextEdit()
        self.context.setPlaceholderText("短文内容")
        content_frame.layout().addWidget(self.context)
        self.context_count = QLabel("0/2000")
        content_frame.layout().addWidget(self.context_count, 0,
                                         Qt.AlignmentFlag.AlignRight)

        self.publish_control = PublishControl()
        center_frame.layout().addWidget(self.publish_control)

        #############################################################
        # set margin and spacing
        center_frame.layout().setContentsMargins(0, 0, 0, 0)
        setting_frame.layout().setContentsMargins(0, 0, 0, 0)
        content_frame.layout().setContentsMargins(10, 10, 10, 0)
        self.layout().setContentsMargins(10, 8, 10, 10)

    def addStyle(self):
        self.setStyleSheet(self.Style)
