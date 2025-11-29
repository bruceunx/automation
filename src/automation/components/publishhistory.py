from PySide6.QtCore import QAbstractTableModel, QDateTime, QLocale, Slot
from PySide6.QtGui import QColor, Qt
from PySide6.QtWidgets import QDateTimeEdit, QFrame, QHBoxLayout, QHeaderView, QLabel, QPushButton, QTableView, QVBoxLayout, QWidget

from components.useritem import CustomWidgetDelegate
from models.query import get_records_from_time


class RecordModel(QAbstractTableModel):

    def __init__(self, data=None):
        super(RecordModel, self).__init__()
        self._data = data or []
        self._headers = ["序号", "用户", "标题", "发布时间", "发布状态"]

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            row = self._data[index.row()]
            if index.column() == 0:
                return row["record_id"]
            elif index.column() == 1:
                return row['username'], row['icon_raw'], row['platform']
            elif index.column() == 2:
                return row["title"]
            elif index.column() == 3:
                return QDateTime.fromSecsSinceEpoch(
                    row["timestamp"]).toString("yyyy-MM-dd  hh:mm:ss")
            elif index.column() == 4:
                return "发布成功" if row["status"] == 1 else "发布失败"

        elif role == Qt.ForegroundRole:
            row = self._data[index.row()]
            column = index.column()
            if column == 4:
                return QColor(0, 128, 0) if row["status"] else QColor(
                    128, 0, 0)

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]

        return None

    def flags(self, index):
        return Qt.ItemIsEnabled

    def update_data(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()


class PublishHistory(QWidget):

    Style = """
    #center_frame {
        background-color: #fff;
        border-top-left-radius: 20px;
        border-top-right-radius: 20px;
    }
    QLabel {
        color: #555;
        font-size: 13px;
    }
    QDateTimeEdit {
        background-color: #eee;
        color: #555;
        border: 1px solid #ccc;
        border-radius: 5px;
        padding: 5px;
        font-size: 13px;
    }
    QDateTimeEdit::drop-down {
        background-color: #e0e0e0;
        width: 20px;
        color: #333;
        border-left: 1px solid #5a5a5a;
    }
    QDateTimeEdit::down-arrow {
        image: url('assets/down.svg');
        width: 10px;
    }
    QTableView {
        border: none;
        color: #555;
        gridline-color: #e0e0e0;
        background-color: #fff;
    }
    QTableView::item {
        padding: 5px;
        border-bottom: 1px solid #e0e0e0;
    }
    QTableView::item:selected {
        color: white;
    }
    QHeaderView::section {
        background-color: #f0f0f0;
        padding: 5px;
        font-weight: bold;
        border: 1px solid #d0d0d0;
        color: #333;
    }
    QPushButton {
        background-color: #4CAF50;
        color: white;
        padding: 5px 10px;
        text-align: center;
        font-size: 16px;
        margin: 4px 2px;
        border-radius: 8px;
    }
    QPushButton:hover {
        background-color: #45a049;
    }
    QPushButton:pressed {
        background-color: #3e8e41; 
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
    """

    def __init__(self, parent=None):
        super(PublishHistory, self).__init__(parent)

        self.addComponents()
        self.addStyle()

    def addComponents(self):
        self.setLayout(QVBoxLayout())
        center_frame = QFrame()
        center_frame.setLayout(QVBoxLayout())
        center_frame.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        center_frame.setObjectName("center_frame")
        self.layout().addWidget(center_frame)

        head_layout = QHBoxLayout()
        head_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.start_time = QDateTimeEdit()
        self.end_time = QDateTimeEdit()

        self.start_time.setCalendarPopup(True)
        self.end_time.setCalendarPopup(True)
        self.start_time.setDateTime(QDateTime.currentDateTime().addDays(-1))
        self.end_time.setDateTime(QDateTime.currentDateTime())

        self.start_time.setLocale(QLocale.Language.Chinese)
        self.end_time.setLocale(QLocale.Language.Chinese)

        head_layout.addWidget(QLabel("开始时间"))
        head_layout.addWidget(self.start_time)
        head_layout.addWidget(QLabel("结束时间"))
        head_layout.addWidget(self.end_time)

        self.search_btn = QPushButton("查询")
        head_layout.addWidget(self.search_btn)

        center_frame.layout().addLayout(head_layout)

        self.table_view = QTableView()
        self.model = RecordModel()
        self.table_view.setModel(self.model)
        self.table_view.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        self.table_view.setShowGrid(False)

        self.table_view.verticalHeader().setVisible(False)
        center_frame.layout().addWidget(self.table_view)

        center_frame.layout().setContentsMargins(10, 10, 10, 10)
        center_frame.layout().setSpacing(20)

        self.search_btn.clicked.connect(self.handle_search)

        self.d1 = CustomWidgetDelegate()
        self.table_view.setItemDelegateForColumn(1, self.d1)

        self.model.modelReset.connect(self.handle_model_reset)

    @Slot()
    def handle_model_reset(self):
        row_height = 70
        for row in range(self.table_view.model().rowCount()):
            self.table_view.setRowHeight(row, row_height)

    def addStyle(self):
        self.setStyleSheet(self.Style)

    @Slot()
    def handle_search(self):
        start_time = self.start_time.dateTime().toSecsSinceEpoch()
        end_time = self.end_time.dateTime().toSecsSinceEpoch()
        records = get_records_from_time(start_time, end_time)
        self.model.update_data(records)
