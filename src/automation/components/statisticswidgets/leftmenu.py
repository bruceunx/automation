from PySide6.QtCore import Qt
from PySide6.QtWidgets import QButtonGroup, QPushButton, QVBoxLayout, QWidget


class StatisticsLeftBar(QWidget):
    def __init__(self, parent=None):
        super(StatisticsLeftBar, self).__init__(parent)
        self.setFixedWidth(150)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.button_groups = QButtonGroup()

        titles = ("数据总览", "平台数据", "账号数据", "作品数据")
        for idx, title in enumerate(titles):
            button = QPushButton(title)
            button.setCheckable(True)
            self.button_groups.addButton(button, idx)
            layout.addWidget(button)

        self.button_groups.button(0).setChecked(True)
        self.setLayout(layout)

        self.setStyleSheet("""
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
