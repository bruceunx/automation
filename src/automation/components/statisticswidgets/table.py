from PySide6.QtCore import (
    QAbstractTableModel,
    QDate,
    QDateTime,
    QEvent,
    QLocale,
    QModelIndex,
    QSortFilterProxyModel,
    Qt,
    Slot,
    Signal,
)
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)
import xlsxwriter

from models.query import get_all_groups, get_records_for_stats
from utils.constant import Platform, PublishType
from utils.delegates import RowHoverDelegation
from utils.struct import Record


class StatisticsModel(QAbstractTableModel):
    def __init__(self):
        super(StatisticsModel, self).__init__()

        self._data = []
        self._headers = [
            "账号",
            "总收益",
            "昨日收益",
            "总阅读量",
            "昨日阅读量",
            "总播放量",
            "昨日播放量",
            "粉丝数",
            "更新时间",
            "状态",
            "操作",
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


class StatisticsPlatformModel(QAbstractTableModel):
    def __init__(self):
        super(StatisticsPlatformModel, self).__init__()

        self._data = []
        self._headers = [
            "平台",
            "总收益",
            "昨日收益",
            "总阅读量",
            "昨日阅读量",
            "总播放量",
            "昨日播放量",
            "粉丝数",
            "更新时间",
            "状态",
            "操作",
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


class StatisticsContentModel(QAbstractTableModel):
    def __init__(self):
        super(StatisticsContentModel, self).__init__()

        self.row_id = -1
        self._data = []
        self._headers = [
            "账号",
            "标题",
            "类型",
            "平台",
            "发布时间",
            "发布状态",
            "操作",
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
            record = self._data[index.row()]
            column = index.column()
            match column:
                case 0:
                    return record.username
                case 1:
                    return record.title
                case 2:
                    return record.record_type.verbose
                case 3:
                    return record.platform.display_name
                case 4:
                    return QDateTime.fromSecsSinceEpoch(record.timestamp).toString(
                        "yyyy-MM-dd  hh:mm:ss"
                    )
                case 5:
                    return "发布成功" if record.status else "发布失败"
                case 6:
                    return "编辑"

            return None

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        elif role == Qt.BackgroundRole:
            if index.row() == self.row_id:
                return QBrush(QColor(240, 240, 240))

        elif role == Qt.ForegroundRole:
            if index.column() == 6:
                return QColor(0, 180, 0)

    def flags(self, index):
        return Qt.ItemIsEnabled

    def update_data(self, data: list[Record]):
        self.beginResetModel()
        self._data = data
        self.endResetModel()

    @Slot(int)
    def handle_hover_row(self, row_id: int):
        self.row_id = row_id
        self.modelReset.emit()


class StatisticsTableView(QTableView):
    hover_row_id = Signal(int)

    def __init__(self, parent=None):
        super(StatisticsTableView, self).__init__(parent)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(50)
        self.horizontalHeader().setMinimumHeight(50)
        self.setShowGrid(False)

        self.setSelectionMode(QTableView.SelectionMode.NoSelection)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.clicked.connect(self.handle_clicked)

        self.setMouseTracking(True)
        self.viewport().installEventFilter(self)

        self._current_hover_index = QModelIndex()

    @Slot(QModelIndex)
    def handle_clicked(self, index: QModelIndex):
        if not index.isValid():
            return

    def eventFilter(self, watched, event):
        if watched == self.viewport():
            if event.type() == QEvent.MouseMove:
                mouse_event = event
                index = self.indexAt(mouse_event.pos())
                if index != self._current_hover_index:
                    if index.isValid():
                        self._current_hover_index = index
                        self.hover_row_id.emit(index.row())
                    else:
                        self.hover_row_id.emit(-1)
        return super().eventFilter(watched, event)


class StatisticsContentTableView(StatisticsTableView):
    def __init__(self, parent=None):
        super(StatisticsContentTableView, self).__init__(parent)
        self.verticalHeader().setDefaultSectionSize(70)

    @Slot(QModelIndex)
    def handle_clicked(self, index: QModelIndex):
        if not index.isValid():
            return

    def resizeEvent(self, event):
        super().resizeEvent(event)

        total_width = self.viewport().width()
        self.setColumnWidth(0, int(total_width * 0.2))
        self.setColumnWidth(1, int(total_width * 0.25))
        self.setColumnWidth(2, int(total_width * 0.1))
        self.setColumnWidth(3, int(total_width * 0.1))
        self.setColumnWidth(4, int(total_width * 0.15))
        self.setColumnWidth(5, int(total_width * 0.1))
        self.setColumnWidth(6, int(total_width * 0.1))


class StatisticsTable(QWidget):
    def __init__(self, parent=None):
        super(StatisticsTable, self).__init__(parent)

        self.addComponents()
        self.addStyle()
        self.addConnections()
        self.afterInit()

    def addComponents(self):
        self.groups_selectors = QComboBox()
        self.platforms_selectors = QComboBox()
        self.refresh_btn = QPushButton("刷新数据")
        self.export_btn = QPushButton("导出数据")

        layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        top_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        top_layout.addWidget(self.groups_selectors)
        top_layout.addWidget(self.platforms_selectors)
        top_layout.addWidget(self.refresh_btn)
        top_layout.addStretch()
        top_layout.addWidget(self.export_btn)

        layout.addLayout(top_layout)

        total_layout = QGridLayout()
        layout.addLayout(total_layout)

        info_labels = (
            "账号总数",
            "累计收益",
            "昨天收益",
            "累计阅读量",
            "昨日阅读量",
            "累计播放量",
            "昨日播放量",
            "累计粉丝",
        )

        self.info_labels = []

        for idx, title in enumerate(info_labels):
            total_layout.addWidget(QLabel(title), 0, idx)
            label = QLabel("0")
            total_layout.addWidget(label, 1, idx)
            self.info_labels.append(label)

        self.table = StatisticsTableView()
        self._model = StatisticsModel()

        self.proxy_group = QSortFilterProxyModel()
        self.proxy_group.setSourceModel(self._model)
        self.proxy_group.setFilterKeyColumn(1)

        self.proxy_platform = QSortFilterProxyModel()
        self.proxy_platform.setSourceModel(self.proxy_group)
        self.proxy_platform.setFilterKeyColumn(2)

        self.table.setModel(self.proxy_platform)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def addConnections(self):
        self.groups_selectors.currentTextChanged.connect(
            lambda text: self.proxy_group.setFilterFixedString(
                "" if text == "全部分组" else text
            )
        )
        self.platforms_selectors.currentTextChanged.connect(
            lambda text: self.proxy_platform.setFilterFixedString(
                "" if text == "全部平台" else text
            )
        )

    def afterInit(self):
        # first get all the groups
        groups = get_all_groups()
        self.groups_selectors.addItem("全部分组")
        for group in groups:
            self.groups_selectors.addItem(group["name"])

        self.platforms_selectors.addItem("全部平台")
        for platform in Platform:
            self.platforms_selectors.addItem(platform.display_name)

        # add proxy for model

    @Slot(list)
    def update_info(self, data: list):
        pass

    def addStyle(self):
        self.setStyleSheet("""
        QLabel {
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
        """)


class PlatformStatistic(QWidget):
    def __init__(self, parent=None):
        super(PlatformStatistic, self).__init__(parent)

        self.addComponents()
        self.addStyle()
        self.afterInit()

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

        self.table = StatisticsTableView()
        self.model = StatisticsPlatformModel()
        self.table.setModel(self.model)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def afterInit(self):
        pass

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
        """)


class AccountStatistic(QWidget):
    def __init__(self, parent=None):
        super(AccountStatistic, self).__init__(parent)

        self.addComponents()
        self.addStyle()
        self.addConnections()
        self.afterInit()

    def addComponents(self):
        self.start_time = QDateEdit()
        self.end_time = QDateEdit()
        self.groups_selectors = QComboBox()
        self.platforms_selectors = QComboBox()
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
        top_layout.addWidget(self.groups_selectors)
        top_layout.addWidget(self.platforms_selectors)
        top_layout.addWidget(self.refresh_btn)
        top_layout.addStretch()
        top_layout.addWidget(self.export_btn)

        layout.addLayout(top_layout)

        total_layout = QGridLayout()
        layout.addLayout(total_layout)

        info_labels = (
            "账号总数",
            "累计收益",
            "昨天收益",
            "累计阅读量",
            "昨日阅读量",
            "累计播放量",
            "昨日播放量",
            "累计粉丝",
        )

        self.info_labels = []

        for idx, title in enumerate(info_labels):
            total_layout.addWidget(QLabel(title), 0, idx)
            label = QLabel("0")
            total_layout.addWidget(label, 1, idx)
            self.info_labels.append(label)

        self.table = StatisticsTableView()
        self._model = StatisticsModel()

        self.proxy_group = QSortFilterProxyModel()
        self.proxy_group.setSourceModel(self._model)
        self.proxy_group.setFilterKeyColumn(1)

        self.proxy_platform = QSortFilterProxyModel()
        self.proxy_platform.setSourceModel(self.proxy_group)
        self.proxy_platform.setFilterKeyColumn(2)

        self.table.setModel(self.proxy_platform)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def addConnections(self):
        self.groups_selectors.currentTextChanged.connect(
            lambda text: self.proxy_group.setFilterFixedString(
                "" if text == "全部分组" else text
            )
        )
        self.platforms_selectors.currentTextChanged.connect(
            lambda text: self.proxy_platform.setFilterFixedString(
                "" if text == "全部平台" else text
            )
        )

    def afterInit(self):
        groups = get_all_groups()
        self.groups_selectors.addItem("全部分组")
        for group in groups:
            self.groups_selectors.addItem(group["name"])

        self.platforms_selectors.addItem("全部平台")
        for platform in Platform:
            self.platforms_selectors.addItem(platform.display_name)

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

    @Slot(list)
    def update_info(self, data: list):
        pass


class ContentStatistic(QWidget):
    def __init__(self, parent=None):
        super(ContentStatistic, self).__init__(parent)

        self.addComponents()
        self.addStyle()
        self.addConnections()
        self.afterInit()

    def addComponents(self):
        self.start_time = QDateEdit()
        self.end_time = QDateEdit()
        self.publish_types = QComboBox()
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
        top_layout.addWidget(QLabel("筛选:"))
        top_layout.addWidget(self.publish_types)
        top_layout.addWidget(self.export_btn)

        layout.addLayout(top_layout)

        self.table = StatisticsContentTableView()

        self._model = StatisticsContentModel()

        self.proxy_type = QSortFilterProxyModel()
        self.proxy_type.setSourceModel(self._model)
        self.proxy_type.setFilterKeyColumn(2)
        self.table.setModel(self.proxy_type)

        self.row_hover_delegate = RowHoverDelegation()
        self.table.setItemDelegate(self.row_hover_delegate)

        layout.addWidget(self.table)

        self.setLayout(layout)

    def addConnections(self):
        self.publish_types.currentTextChanged.connect(
            lambda text: self.proxy_type.setFilterFixedString(
                "" if text == "全部类型" else text
            )
        )
        self.refresh_btn.clicked.connect(self.handle_get_data)
        self.table.hover_row_id.connect(self._model.handle_hover_row)
        self.export_btn.clicked.connect(self.handle_save_file)

    @Slot()
    def handle_save_file(self):
        filename, _ = QFileDialog.getSaveFileName(
            None, "导出数据", "", "Excel Files (*.xlsx);;All Files (*)"
        )
        if not filename:
            return
        if not filename.lower().endswith(".xlsx"):
            filename += ".xlsx"

        rows = self._model.rowCount()
        cols = self._model.columnCount()

        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()

        for col in range(cols):
            header = self._model.headerData(col, Qt.Horizontal)
            worksheet.write(0, col, header)

        for row in range(rows):
            for col in range(cols):
                index = self._model.index(row, col)
                cell_data = self._model.data(index)
                worksheet.write(row + 1, col, cell_data)

        workbook.close()

    @Slot()
    def handle_get_data(self):
        start_time = self.start_time.dateTime().toSecsSinceEpoch()
        end_time = self.end_time.dateTime().toSecsSinceEpoch()
        records = get_records_for_stats(start_time, end_time)
        self._model.update_data(records)

    def afterInit(self):
        self.publish_types.addItem("全部类型")
        for publish_type in PublishType:
            self.publish_types.addItem(publish_type.verbose)

    def addStyle(self):
        self.setStyleSheet("""
        QLabel {
            font-size: 10pt;
            color: #555;
            padding: 2px;
        }
        QTableView {
            border: none;
            font-size: 11pt;
            color: #777;
        }

        QTableView QHeaderView {
            border: none;
            background-color: #e0e0e0;
            color: #555;
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
