from PySide6.QtGui import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QWidget


class PublishControl(QWidget):

    def __init__(self, parent=None):
        super(PublishControl, self).__init__(parent)

        self.setLayout(QHBoxLayout())
        content = QFrame()
        content.setObjectName("content")
        content.setLayout(QHBoxLayout())
        content.layout().setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.layout().addWidget(content)

        self.save_btn = QPushButton("保存")
        self.publish_btn = QPushButton("发布")
        self.timer_publish_btn = QPushButton("定时发布")
        self.mem_btn = QPushButton("选择记忆")
        self.clear_men_btn = QPushButton("清楚记忆")

        content.layout().addWidget(self.save_btn)
        content.layout().addWidget(self.publish_btn)
        content.layout().addWidget(self.timer_publish_btn)
        content.layout().addWidget(self.mem_btn)
        content.layout().addWidget(self.clear_men_btn)

        self.setFixedHeight(50)
        content.layout().setSpacing(20)
        content.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.setStyleSheet("""
            QPushButton{
                padding: 5px;
                border: none;
                border-radius: 10px;
                width: 100px;
                background-color: #0C6291;
            }
            QPushButton:hover {
                background-color: #118DD0;
            }
            QPushButton:pressed {
                background-color: #094D71 
            }
        """)
