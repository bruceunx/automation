from PySide6.QtCore import QAbstractTableModel, QDate, QLocale, QModelIndex, Qt, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QButtonGroup,
    QDateEdit,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedLayout,
    QTableView,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ContactUs(QWidget):
    def __init__(self, parent=None):
        super(ContactUs, self).__init__(parent)
        self.setLayout(QVBoxLayout())
        content = QFrame()
        content.setMinimumWidth(500)
        content.setMinimumHeight(600)
        self.layout().addWidget(
            content, 0, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop
        )
        layout = QVBoxLayout()
        qrcode = QLabel()
        qrcode.setPixmap(QIcon("assets/icons/qrcode.svg").pixmap(500, 500))
        layout.addWidget(qrcode)

        content.setLayout(layout)


class FeedBack(QWidget):
    def __init__(self, parent=None):
        super(FeedBack, self).__init__(parent)
        self.setLayout(QVBoxLayout())
        content = QFrame()
        content.setMinimumWidth(800)
        content.setMinimumHeight(500)
        self.layout().addWidget(
            content, 0, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop
        )
        layout = QFormLayout()
        self.title = QLineEdit()
        self.title.setPlaceholderText("输入主题")
        self.content = QTextEdit()
        self.content.setPlaceholderText("输入反馈内容")
        self.submit = QPushButton("提交")

        layout.addRow("主题: ", self.title)
        layout.addRow("内容: ", self.content)
        layout.addWidget(self.submit)

        content.setLayout(layout)

        self.setStyleSheet("""
        QLabel {
            color: #555;
        }
        QLineEdit, QTextEdit {
            outline: none;
            border: 1px solid #c0b9dd;
            border-radius: 5px;
            color: #777;
            padding: 2px;
        }
        QPushButton {
            border: none;
            border-radius: 5px;
            width: 200px;
            padding: 5 10;
            background-color: #c0b9dd;
            color: #fff;
        }
        QPushButton:hover {
            background-color: #8575bd;
        }
        QPushButton:pressed {
            background-color: #a675a1;
        }

        """)


class OrderModel(QAbstractTableModel):
    def __init__(self):
        super(OrderModel, self).__init__()

        self._data = []
        self._headers = [
            "序号",
            "订单",
            "时间",
            "订单类型",
        ]

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            row_data = self._data[index.row()]
            column = index.column()
            print(row_data, column)
            return None

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

    def flags(self, index):
        return Qt.ItemIsEnabled


class OrderTableView(QTableView):
    def __init__(self, parent=None):
        super(OrderTableView, self).__init__(parent)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(30)
        self.setShowGrid(False)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


class OrderTable(QWidget):
    def __init__(self, parent=None):
        super(OrderTable, self).__init__(parent)

        self.addComponents()
        self.addStyle()
        # self.addConnections()
        # self.afterInit()

    def addComponents(self):
        self.start_time = QDateEdit()
        self.end_time = QDateEdit()
        self.refresh_btn = QPushButton("查询")
        self.export_btn = QPushButton("导出数据")

        self.start_time.setCalendarPopup(True)
        self.end_time.setCalendarPopup(True)
        self.start_time.setDate(QDate.currentDate())
        self.end_time.setDate(QDate.currentDate())
        self.start_time.setLocale(QLocale(QLocale.Chinese, QLocale.China))
        self.start_time.calendarWidget().setMinimumSize(400, 200)
        self.end_time.setLocale(QLocale(QLocale.Chinese, QLocale.China))
        self.end_time.calendarWidget().setMinimumSize(400, 200)
        self.start_time.setDisplayFormat("yyyy年MM月dd日")
        self.end_time.setDisplayFormat("yyyy年MM月dd日")

        layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        top_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        top_layout.addWidget(QLabel("开始时间"))
        top_layout.addWidget(self.start_time)
        top_layout.addWidget(QLabel("结束时间"))
        top_layout.addWidget(self.end_time)
        top_layout.addWidget(self.refresh_btn)
        top_layout.addStretch()
        top_layout.addWidget(self.export_btn)

        layout.addLayout(top_layout)

        self.table = OrderTableView()
        self.model = OrderModel()
        self.table.setModel(self.model)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def addStyle(self):
        self.setStyleSheet("""
        QLabel {
            font-size: 10pt;
            color: #555;
            padding: 2px;
        }
        QTableView {
            background-color: #F5F5F5;
            border: none;
        }

        QTableView QHeaderView {
            border: none;
            background-color: #e0e0e0;
            color: #555;
        }
        QTableView::item {
            border-bottom: 1px solid #e0e0e0;
            padding: 10px 5px;
        }
        QTableView::item:hover {
            background-color: #E0E0E0;
        }
        QScrollBar:vertical {
            background: transparent;
            width: 10px;
        }
        QScrollBar::handle:vertical {
            background: #ECF7FD;
            border-radius: 3px;
            min-height: 20px;
        }
        QScrollBar::add-line:vertical {
            height: 0px;
        }
        QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
            width: 0px;
            height: 0px;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }

        QDateEdit {
            color: #555;
            font-size: 10pt;
        }

        QCalendarWidget QAbstractItemView { 
            font-size: 14px; 
            color: #4CAF50;
            background-color: #F0F0F0; 
            selection-background-color: #4CAF50;
            selection-color: white;
            outline: none;
        }
        
        QCalendarWidget QToolButton {
            background-color: #4CAF50; 
            color: white; 
            font-size: 14px;
            border-radius: 5px;
            padding: 5px;
        }
        QCalendarWidget QToolButton:hover {
            background-color: #388E3C;
        }
        
        QCalendarWidget QHeaderView {  
            font-size: 10px;
            background-color: #4CAF50;
        }

        QCalendarWidget QWidget#qt_calendar_navigationbar { 
            background-color: #4CAF50;
        }

        QPushButton {
            border: none;
            border-radius: 5px;
            background-color: #006ba6;
            padding: 5px;
            font-size: 10pt;
            color: #fff;
            width: 100px;
        }
        QPushButton:hover {
            background-color: #0088cc;
        }
        QPushButton:pressed {
            background-color: #005280;
        }
        QComboBox {
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 5px;
            color: #555;
            font-size: 12px;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 15px;
            border-left-width: 1px;
            border-left-color: gray;
            border-left-style: solid;
        }
        QComboBox::down-arrow {
            image: url(assets/down.svg); 
            width: 10px;
            height: 10px;
        }
        QComboBox QAbstractItemView {
            background-color: #fff;
            border: none;
            selection-background-color: rgba(0, 0, 220, 100);
        }
        QScrollArea {
            border: none;
        }
        """)


class AccountSetting(QWidget):
    def __init__(self, parent=None):
        super(AccountSetting, self).__init__(parent)
        self.setLayout(QVBoxLayout())
        content = QFrame()
        content.setMinimumWidth(800)
        content.setMinimumHeight(500)
        self.layout().addWidget(
            content, 0, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop
        )

        layout = QFormLayout()

        self.phone_num = QLineEdit("12345678910")
        self.old_password = QLineEdit()
        self.new_password = QLineEdit()
        self.old_password.setEchoMode(QLineEdit.Password)
        self.new_password.setEchoMode(QLineEdit.Password)

        self.old_password.setPlaceholderText("输入旧密码")
        self.new_password.setPlaceholderText("输入新密码")

        self.conform_btn = QPushButton("确认修改")

        layout.addRow("手机号: ", self.phone_num)
        layout.addRow("旧密码: ", self.old_password)
        layout.addRow("新密码: ", self.new_password)
        layout.addWidget(self.conform_btn)

        layout.setSpacing(10)
        content.setLayout(layout)
        self.conform_btn.clicked.connect(self.handle_change_password)

        self.setStyleSheet("""
        QLabel {
            color: #555;
        }
        QLineEdit {
            outline: none;
            border: 1px solid #c0b9dd;
            border-radius: 5px;
            color: #777;
            padding: 2px;
        }
        QPushButton {
            border: none;
            border-radius: 5px;
            width: 200px;
            padding: 5 10;
            background-color: #c0b9dd;
            color: #fff;
        }
        QPushButton:hover {
            background-color: #8575bd;
        }
        QPushButton:pressed {
            background-color: #a675a1;
        }
        """)

    def handle_change_password(self):
        pass


class UserCenterLeftBar(QWidget):
    def __init__(self, parent=None):
        super(UserCenterLeftBar, self).__init__(parent)
        self.setFixedWidth(150)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.button_groups = QButtonGroup()

        titles = ("个人设置", "订单列表", "建议反馈", "联系客服")
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


class UserCenter(QWidget):
    def __init__(self, parent=None):
        super(UserCenter, self).__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("UserCenter")
        self.addComponents()
        self.addConnections()
        self.addStyle()

    def addComponents(self):
        self.left_bar = UserCenterLeftBar()

        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(self.left_bar)
        right_layout = QVBoxLayout()
        layout.addLayout(right_layout)

        self.stack = QStackedLayout()
        right_layout.addLayout(self.stack)

        self.stack.addWidget(AccountSetting())
        self.stack.addWidget(OrderTable())
        self.stack.addWidget(FeedBack())
        self.stack.addWidget(ContactUs())

    def addConnections(self):
        self.left_bar.button_groups.idClicked.connect(self.handle_switch)

    @Slot(int)
    def handle_switch(self, idx: int):
        self.stack.setCurrentIndex(idx)

    def addStyle(self):
        self.setStyleSheet("""
        #UserCenter {
            background-color: #fff;
            border-radius: 12px;
        }
        """)
