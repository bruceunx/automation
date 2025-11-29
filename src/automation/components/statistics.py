from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from components.statisticswidgets.leftmenu import StatisticsLeftBar
from components.statisticswidgets.table import (
    AccountStatistic,
    ContentStatistic,
    PlatformStatistic,
    StatisticsTable,
)


class Statistic(QWidget):
    def __init__(self, parent=None):
        super(Statistic, self).__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("Statistic")
        self.addComponents()
        self.addConnections()
        self.addStyle()

    def addComponents(self):
        self.left_bar = StatisticsLeftBar()

        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(self.left_bar)
        right_layout = QVBoxLayout()
        layout.addLayout(right_layout)

        self.stack = QStackedLayout()
        right_layout.addLayout(self.stack)

        self.stack.addWidget(StatisticsTable())
        self.stack.addWidget(PlatformStatistic())
        self.stack.addWidget(AccountStatistic())
        self.stack.addWidget(ContentStatistic())

    def addConnections(self):
        self.left_bar.button_groups.idClicked.connect(self.handle_switch)

    @Slot(int)
    def handle_switch(self, idx: int):
        self.stack.setCurrentIndex(idx)

    def addStyle(self):
        self.setStyleSheet("""
        #Statistic {
            background-color: #fff;
            border-radius: 12px;
        }
        """)
