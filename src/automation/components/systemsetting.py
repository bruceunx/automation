from PySide6.QtCore import (
    QAbstractListModel,
    QAbstractTableModel,
    QEvent,
    QModelIndex,
    QSortFilterProxyModel,
    Qt,
    Signal,
    Slot,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QIcon,
    QStandardItem,
    QStandardItemModel,
)
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QMessageBox,
    QPushButton,
    QStackedLayout,
    QTableView,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from components.usergroup import CheckBoxHeader
from components.useritem import (
    CheckBoxDelegate,
)
from models.query import (
    Employee,
    Position,
    delete_employee_position,
    delete_position,
    get_all_employees,
    get_all_positions,
    insert_position,
    insert_positions_to_employee,
    update_employ,
    update_position,
)
from utils import PERMISSION, transform_permissions_to_str
from utils.constant import EmpployeeType


class PositionItem(QStandardItem):
    def __init__(self, position: Position):
        super(PositionItem, self).__init__(position.title)
        self.id = position.id


class EditEmployee(QDialog):
    def __init__(self, employee: Employee, parent=None):
        super(EditEmployee, self).__init__(parent)
        self.setWindowTitle("编辑用户")
        self.setWindowIcon(QIcon("assets/key.svg"))
        self.setFixedSize(500, 500)
        self.employee = employee

        self.position_ids = [position.id for position in employee.positions]

        positions = get_all_positions()
        for position in positions:
            if position.id in self.position_ids:
                position.check_state = Qt.CheckState.Checked  # type: ignore
            else:
                position.check_state = Qt.CheckState.Unchecked  # type: ignore

        self.postion_view = QListView()

        self.model = QStandardItemModel()
        for position in positions:
            root_item = PositionItem(position)
            root_item.setCheckable(True)
            root_item.setCheckState(position.check_state)  # type: ignore
            self.model.appendRow(root_item)

        self.postion_view.setModel(self.model)
        self.postion_view.setSelectionMode(QListView.SelectionMode.NoSelection)
        self.postion_view.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.employee_selector = QComboBox()
        for employee_type in EmpployeeType:
            self.employee_selector.addItem(employee_type.verbose)

        self.employee_selector.setCurrentText(employee.status.verbose)

        # name, phone number postions, status
        layout = QFormLayout()
        layout.addRow("用户名: ", QLabel(employee.name))
        layout.addRow("手机号: ", QLabel(str(employee.phone_number)))
        layout.addRow("当前职位: ", self.postion_view)
        layout.addRow("当前状态: ", self.employee_selector)

        self.button_box = QDialogButtonBox()
        self.confirm_button = QPushButton("确认")
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setObjectName("cancelButton")

        self.button_box.addButton(
            self.confirm_button, QDialogButtonBox.ButtonRole.AcceptRole
        )
        self.button_box.addButton(
            self.cancel_button, QDialogButtonBox.ButtonRole.RejectRole
        )

        self.confirm_button.clicked.connect(self.before_accept)
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

        self.setStyleSheet("""
        QListView {
            background-color: #f9f9f9;
            border: 1px solid #d3d3d3;
            border-radius: 5px;
            font-size: 14px;
            padding: 5px;
        }
        QListView::item {
            height: 25px;
        }
        QListView::item:hover {
            background-color: #e6f7ff;
        }
        QListView::indicator {
            width: 15px;
            height: 15px;
            border-radius: 5px;
            border: 1px solid #0078d4;
            background-color: white;
        }

        QListView::indicator:unchecked {
            border-color: #d3d3d3;
            background-color: white;
        }

        QListView::indicator:checked {
            border-color: #0078d4;
            background-color: #0078d4;
        }

        QListView::indicator:indeterminate {
            border-color: #0078d4;
            background-color: #b3d9ff;
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
        QPushButton {
            background-color: #0078d4;
            color: white;
            border-radius: 5px;
            padding: 5px 15px;
        }
        QPushButton:hover {
            background-color: #005a9e;
        }
        QPushButton:pressed {
            background-color: #003f6b;
        }
        QPushButton#cancelButton {
            background-color: #d9534f;
            color: white;
        }
        QPushButton#cancelButton:hover {
            background-color: #c9302c;
        }
        QPushButton#cancelButton:pressed {
            background-color: #ac2925;
        }
        """)

    def before_accept(self):
        position_ids = []
        for row_idx in range(self.model.rowCount()):
            item = self.model.item(row_idx)
            if item.checkState() == Qt.CheckState.Checked:
                position_ids.append(item.id)
        if self.position_ids == position_ids:
            self.reject()
        delete_ids = [id for id in self.position_ids if id not in position_ids]
        insert_ids = [id for id in position_ids if id not in self.position_ids]
        current_status = self.employee_selector.currentText()

        if current_status != self.employee.status.verbose:
            if not update_employ(
                self.employee.id, EmpployeeType.from_str(current_status).value
            ):
                self.reject()

        if len(delete_ids) != 0:
            if not delete_employee_position(self.employee.id, delete_ids):
                self.reject()
        if len(insert_ids) != 0:
            if not insert_positions_to_employee(self.employee.id, insert_ids):
                self.reject()
        self.accept()


class CheckableTreeModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def flags(self, index):
        return super().flags(index) | Qt.ItemFlag.ItemIsUserCheckable


class CreatePostion(QDialog):
    def __init__(self, parent=None):
        super(CreatePostion, self).__init__(parent)
        self.setWindowTitle("添加职位权限")
        self.setWindowIcon(QIcon("assets/key.svg"))
        self.setFixedSize(500, 500)

        layout = QFormLayout()

        self._data = PERMISSION

        self.postion_name = QLineEdit()
        self.postion_name.setPlaceholderText("输入职位名称")

        self.permission_view = QTreeView()

        self.permission_view.setSelectionMode(QListView.SelectionMode.NoSelection)
        self.permission_view.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.model = QStandardItemModel()

        self.permission_view.header().setVisible(False)

        for row in self._data:
            root = QStandardItem(row[0])
            root.setCheckable(True)
            root.setCheckState(Qt.CheckState.Unchecked)
            for subrow in row[1:]:
                child = QStandardItem(subrow)
                child.setCheckable(True)
                child.setCheckState(Qt.CheckState.Unchecked)
                root.appendRow(child)
            self.model.appendRow(root)

        self.permission_view.setModel(self.model)
        self.model.itemChanged.connect(self.on_item_changed)

        layout.addRow("职位名称: ", self.postion_name)
        layout.addRow("设置权限: ", self.permission_view)

        self.button_box = QDialogButtonBox()
        self.confirm_button = QPushButton("确认")
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setObjectName("cancelButton")

        self.button_box.addButton(
            self.confirm_button, QDialogButtonBox.ButtonRole.AcceptRole
        )
        self.button_box.addButton(
            self.cancel_button, QDialogButtonBox.ButtonRole.RejectRole
        )

        self.confirm_button.clicked.connect(self.before_accept)
        self.cancel_button.clicked.connect(self.reject)

        self.permission_view.expandAll()
        layout.addRow(self.button_box)

        self.setLayout(layout)

        self.addStyle()

    def on_item_changed(self, item):
        last_row_index = self.model.rowCount() - 1
        last_row_item = self.model.item(last_row_index)

        if item == last_row_item:
            last_row_state = item.checkState()
            for row_index in range(self.model.rowCount() - 1):
                current_item = self.model.item(row_index)
                current_item.setCheckState(last_row_state)
                self.update_child_check_state(current_item)
        else:
            self.update_child_check_state(item)

    def get_check_state_as_int(self, parent_item=None):
        start = 0
        if parent_item is None:
            parent_item = self.model.invisibleRootItem()
            row_num = parent_item.rowCount() - 1
        else:
            row_num = parent_item.rowCount()
        binary_states = []
        for row in range(start, row_num):
            child_item = parent_item.child(row)
            if child_item.rowCount() > 0:
                binary_states.append(self.get_check_state_as_int(child_item))
            else:
                if child_item.checkState() == Qt.Checked:
                    binary_states.append("1")
                elif child_item.checkState() == Qt.Unchecked:
                    binary_states.append("0")
        return "".join(binary_states)

    def update_child_check_state(self, parent_item):
        if parent_item is None:
            return

        parent_state = parent_item.checkState()

        for i in range(parent_item.rowCount()):
            child = parent_item.child(i)
            child.setCheckState(parent_state)
            self.update_child_check_state(child)

    def before_accept(self):
        postion = self.postion_name.text().strip()
        if len(postion) == 0:
            QMessageBox.warning(self, "缺少名称", "职位名称未填写!!")
            return

        permission = int(self.get_check_state_as_int(), 2)
        if insert_position(postion, permission):
            self.accept()
        QMessageBox.warning(self, "添加失败", "添加职位失败!!")

    def addStyle(self):
        self.setStyleSheet("""
        QTreeView, QLineEdit {
            background-color: #f9f9f9;
            border: 1px solid #d3d3d3;
            border-radius: 5px;
            font-size: 14px;
            padding: 5px;
        }
        QTreeView::item {
            height: 25px;
        }
        QTreeView::item:hover {
            background-color: #e6f7ff;
        }
        QTreeView::indicator {
            width: 15px;
            height: 15px;
            border-radius: 5px;
            border: 1px solid #0078d4;
            background-color: white;
        }

        QTreeView::indicator:unchecked {
            border-color: #d3d3d3;
            background-color: white;
        }

        QTreeView::indicator:checked {
            border-color: #0078d4;
            background-color: #0078d4;
        }

        QTreeView::indicator:indeterminate {
            border-color: #0078d4;
            background-color: #b3d9ff;
        }
        QScrollBar:vertical {
            background: #f0f0f0;
            width: 12px;
            border: 1px solid #d3d3d3;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:vertical {
            background: #0078d4;
            border-radius: 6px;
            min-height: 20px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            background: #f0f0f0;
            height: 0px;
            subcontrol-origin: margin;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: #f0f0f0;
        }
        QScrollBar::handle:vertical:hover {
            background: #005a9e;
        }
        QScrollBar::handle:vertical:pressed {
            background: #003f6b;
        }
        QPushButton {
            background-color: #0078d4;
            color: white;
            border-radius: 5px;
            padding: 5px 15px;
        }
        QPushButton:hover {
            background-color: #005a9e;
        }
        QPushButton:pressed {
            background-color: #003f6b;
        }
        QPushButton#cancelButton {
            background-color: #d9534f;
            color: white;
        }
        QPushButton#cancelButton:hover {
            background-color: #c9302c;
        }
        QPushButton#cancelButton:pressed {
            background-color: #ac2925;
        }
        """)


class EditPostion(CreatePostion):
    def __init__(self, position: Position, parent=None):
        super(EditPostion, self).__init__(parent)
        self.setWindowTitle("编辑职位权限")
        self.position = position
        self.postion_name.setText(self.position.title)
        self.postion_name.setDisabled(True)

        del_btn = QPushButton("删除")
        self.button_box.addButton(del_btn, QDialogButtonBox.DestructiveRole)  # type: ignore
        del_btn.clicked.connect(self.handle_delete)
        del_btn.setObjectName("del_btn")

        binary_string = bin(self.position.permission)[2:].zfill(9)
        # ? why set index = [0]
        self.set_check_state_from_binary(binary_string)

    @Slot()
    def handle_delete(self):
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定删除职位 {self.position.title} 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                if delete_position(self.position.id):
                    self.accept()
                else:
                    QMessageBox.warning(self, "删除错误", "删除职位时发生错误")
                    return
            except Exception as e:
                QMessageBox.warning(self, "删除错误", f"删除职位时发生错误: {e}")
                self.reject()

    def before_accept(self):
        permission = int(self.get_check_state_as_int(), 2)
        if update_position(self.position.id, permission):
            self.accept()
        else:
            QMessageBox.warning(self, "编辑失败", "编辑职位失败!!")

    def set_check_state_from_binary(
        self, binary_string, parent_item=None, index=0
    ) -> int:
        if parent_item is None:
            parent_item = self.model.invisibleRootItem()
            row_num = parent_item.rowCount() - 1
        else:
            row_num = parent_item.rowCount()
        for row in range(row_num):
            child_item = parent_item.child(row)
            if child_item.rowCount() > 0:
                index = self.set_check_state_from_binary(
                    binary_string, child_item, index
                )
            else:
                if index < len(binary_string):
                    state = (
                        Qt.CheckState.Checked
                        if binary_string[index] == "1"
                        else Qt.CheckState.Unchecked
                    )
                    child_item.setCheckState(state)
                    index += 1
        return index


class AuthModel(QAbstractTableModel):
    def __init__(self):
        super(AuthModel, self).__init__()
        self.row_id = -1
        self._data = self.get_data()
        self._headers = [
            "序号",
            "职位名",
            "权限",
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
            posotion = self._data[index.row()]
            column = index.column()
            match column:
                case 0:
                    return posotion.id
                case 1:
                    return posotion.title
                case 2:
                    return ",".join(transform_permissions_to_str(posotion.permission))
                case 3:
                    return "编辑"

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        elif role == Qt.ForegroundRole:
            if index.column() == 3:
                return QColor(0, 128, 0)
        elif role == Qt.BackgroundRole:
            if index.row() == self.row_id:
                return QBrush(QColor(240, 240, 240))

    def flags(self, index):
        return Qt.ItemIsEnabled

    def get_data(self):
        return get_all_positions()

    def update_data(self):
        self.beginResetModel()
        self._data = self.get_data()
        self.endResetModel()

    @Slot(int)
    def handle_edit(self, row_idx: int):
        edit_dialog = EditPostion(self._data[row_idx])  # type: ignore
        if edit_dialog.exec() == QDialog.Accepted:  # type: ignore
            self.update_data()

    @Slot(int)
    def handle_hover_row(self, row_id: int):
        self.row_id = row_id
        self.modelReset.emit()


class AuthTableView(QTableView):
    edit_row_id = Signal(int)

    hover_row_id = Signal(int)

    def __init__(self, parent=None):
        super(AuthTableView, self).__init__(parent)
        self._current_hover_index = QModelIndex()
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(80)
        self.horizontalHeader().setMinimumHeight(70)
        self.setShowGrid(False)

        self.setSelectionMode(QTableView.SelectionMode.NoSelection)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.clicked.connect(self.handle_clicked)

        self.setMouseTracking(True)
        self.viewport().installEventFilter(self)

    @Slot(QModelIndex)
    def handle_clicked(self, index: QModelIndex):
        if not index.isValid():
            return
        if index.column() == 3:
            self.edit_row_id.emit(index.row())

    def resizeEvent(self, event):
        super().resizeEvent(event)

        total_width = self.viewport().width()
        self.setColumnWidth(0, int(total_width * 0.1))
        self.setColumnWidth(1, int(total_width * 0.2))
        self.setColumnWidth(2, int(total_width * 0.6))
        self.setColumnWidth(3, int(total_width * 0.1))

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


class AuthManager(QWidget):
    def __init__(self, parent=None):
        super(AuthManager, self).__init__(parent)
        self.addComponents()
        self.addStyle()

    def addComponents(self):
        self.add_postions = QPushButton("添加新的职位")

        layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        top_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        top_layout.addWidget(self.add_postions)
        top_layout.addStretch(1)

        layout.addLayout(top_layout)

        self.table = AuthTableView()
        self.model = AuthModel()
        self.table.setModel(self.model)
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.add_postions.clicked.connect(self.handle_add_postion)
        self.table.edit_row_id.connect(self.model.handle_edit)

        self.table.hover_row_id.connect(self.model.handle_hover_row)

    @Slot()
    def handle_add_postion(self):
        add_postion = CreatePostion()
        if add_postion.exec() == QDialog.Accepted:
            self.model.update_data()

    def addStyle(self):
        self.setStyleSheet("""
        QTableView {
            background-color: #fff;
            border: none;
            color: #777;
        }
        QTableView QHeaderView {
            border: none;
            background-color: #e0e0e0;
            font-size: 15pt;
            color: #777;
        }
        QTableView QHeaderView:section {
            border: none;
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
        QPushButton {
            border: none;
            border-radius: 5px;
            background-color: #006ba6;
            padding: 7px;
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


class EmployeeModel(QAbstractTableModel):
    def __init__(self):
        super(EmployeeModel, self).__init__()

        self.row_id = -1
        self._data = self.get_data()
        self._headers = [
            "",
            "姓名",
            "职位",
            "员工状态",
            "账号数",
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
            employee = self._data[index.row()]
            column = index.column()
            match column:
                case 0:
                    return employee.check_state
                case 1:
                    return employee.name
                case 2:
                    return ", ".join(
                        [position.title for position in employee.positions]
                    )
                case 3:
                    return employee.status.verbose
                case 4:
                    return 0
                case 5:
                    return "操作"
            return None

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        elif role == Qt.ForegroundRole:
            if index.column() == 5:
                return QColor(0, 128, 0)

        elif role == Qt.BackgroundRole:
            if index.row() == self.row_id:
                return QBrush(QColor(240, 240, 240))

    def flags(self, index):
        return Qt.ItemIsEnabled

    @Slot(int)
    def handle_hover_row(self, row_id: int):
        self.row_id = row_id
        self.modelReset.emit()

    @Slot(bool)
    def check_all(self, value):
        self.beginResetModel()
        for row in range(len(self._data)):
            self._data[row].check_state = value
        self.endResetModel()

    def get_data(self):
        employees = get_all_employees()
        for employee in employees:
            employee.check_state = False
        return employees

    @Slot()
    def refresh_data(self):
        self.beginResetModel()
        self._data = self.get_data()
        self.endResetModel()

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        if role == Qt.EditRole:
            if index.column() == 0:
                self._data[index.row()].check_state = value
            return True
        return False

    @Slot(int)
    def handle_edit(self, row: int):
        employee = self._data[row]
        edit_employee = EditEmployee(employee)
        if edit_employee.exec() == QDialog.Accepted:  # type: ignore
            self.refresh_data()


class EmployeeTableView(QTableView):
    check_all = Signal(bool)
    edit_row = Signal(int)

    hover_row_id = Signal(int)

    def __init__(self, parent=None):
        super(EmployeeTableView, self).__init__(parent)
        self._current_hover_index = QModelIndex()
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(70)
        self.setShowGrid(False)

        self.header = CheckBoxHeader(Qt.Horizontal, self)
        self.header.setFixedHeight(50)
        self.setHorizontalHeader(self.header)
        self.header.check_value.connect(self.handle_check_all)
        self.clicked.connect(self.handle_clicked)

        self.setSelectionMode(QTableView.SelectionMode.NoSelection)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.setMouseTracking(True)
        self.viewport().installEventFilter(self)

    @Slot(QModelIndex)
    def handle_clicked(self, index: QModelIndex):
        if index.isValid():
            if index.column() == 5:
                self.edit_row.emit(index.row())

    @Slot(bool)
    def handle_check_all(self, value):
        self.check_all.emit(value)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        total_width = self.viewport().width()
        self.setColumnWidth(0, int(total_width * 0.1))
        self.setColumnWidth(1, int(total_width * 0.2))
        self.setColumnWidth(2, int(total_width * 0.3))
        self.setColumnWidth(3, int(total_width * 0.1))
        self.setColumnWidth(4, int(total_width * 0.1))
        self.setColumnWidth(5, int(total_width * 0.2))

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


class EmployeeTable(QWidget):
    def __init__(self, parent=None):
        super(EmployeeTable, self).__init__(parent)
        self.addComponents()
        self.addStyle()

    def addComponents(self):
        self.department_selector = QComboBox()
        self.employee_state_selector = QComboBox()
        self.employee_name = QLineEdit()
        self.refresh_btn = QPushButton("刷新数据")

        self.department_selector.addItem("全部职位")
        for position in get_all_positions():
            self.department_selector.addItem(position.title)

        self.employee_state_selector.addItem("全部状态")

        for employee_type in EmpployeeType:
            self.employee_state_selector.addItem(employee_type.verbose)

        self.employee_name.setPlaceholderText("关键词 筛选用户..")

        layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        top_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        top_layout.addWidget(self.department_selector)
        top_layout.addWidget(self.employee_state_selector)
        top_layout.addWidget(self.employee_name)
        top_layout.addWidget(self.refresh_btn)
        top_layout.addStretch(1)

        layout.addLayout(top_layout)

        self.table = EmployeeTableView()
        self._model = EmployeeModel()

        self.filter_name = QSortFilterProxyModel()
        self.filter_name.setSourceModel(self._model)
        self.filter_name.setFilterKeyColumn(1)

        self.filter_position = QSortFilterProxyModel()
        self.filter_position.setSourceModel(self.filter_name)
        self.filter_position.setFilterKeyColumn(2)

        self.filter_status = QSortFilterProxyModel()
        self.filter_status.setSourceModel(self.filter_position)
        self.filter_status.setFilterKeyColumn(3)

        self.table.setModel(self.filter_status)

        self.d0 = CheckBoxDelegate()
        self.table.setItemDelegateForColumn(0, self.d0)

        layout.addWidget(self.table)

        self.employee_name.textEdited.connect(
            lambda text: self.filter_name.setFilterFixedString(text)
        )

        self.department_selector.currentTextChanged.connect(
            lambda text: self.filter_position.setFilterFixedString(
                "" if text == "全部职位" else text
            )
        )

        self.employee_state_selector.currentTextChanged.connect(
            lambda text: self.filter_status.setFilterFixedString(
                "" if text == "全部状态" else text
            )
        )

        self.table.check_all.connect(lambda value: self._model.check_all(value))

        self.refresh_btn.clicked.connect(self._model.refresh_data)

        self.table.edit_row.connect(self._model.handle_edit)
        self.table.hover_row_id.connect(self._model.handle_hover_row)
        self.table.hover_row_id.connect(self.d0.handle_row_id)

        self.setLayout(layout)

    def addStyle(self):
        self.setStyleSheet("""
        QLabel {
            font-size: 10pt;
            color: #555;
            padding: 2px;
        }
        QTableView {
            background-color: #fff;
            color: #777;
            border: none;
        }

        QTableView QHeaderView {
            border: none;
            background-color: #e0e0e0;
            font-size: 15px;
            color: #777;
        }
        QTableView QHeaderView:section {
            border: none;
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

        QPushButton {
            border: none;
            border-radius: 5px;
            background-color: #006ba6;
            padding: 7px;
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
        QComboBox, QLineEdit {
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


class SystemSettingLeftBar(QWidget):
    def __init__(self, parent=None):
        super(SystemSettingLeftBar, self).__init__(parent)

        self.setFixedWidth(150)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.button_groups = QButtonGroup()

        titles = ("人员管理", "权限管理")
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


class SystemSetting(QWidget):
    def __init__(self, parent=None):
        super(SystemSetting, self).__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("SystemSetting")
        self.addComponents()
        self.addConnections()
        self.addStyle()

    def addComponents(self):
        self.left_bar = SystemSettingLeftBar()

        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(self.left_bar)
        right_layout = QVBoxLayout()
        layout.addLayout(right_layout)

        self.stack = QStackedLayout()
        right_layout.addLayout(self.stack)

        self.stack.addWidget(EmployeeTable())
        self.stack.addWidget(AuthManager())

    def addConnections(self):
        self.left_bar.button_groups.idClicked.connect(self.handle_switch)

    @Slot(int)
    def handle_switch(self, idx: int):
        self.stack.setCurrentIndex(idx)

    def addStyle(self):
        self.setStyleSheet("""
        #SystemSetting {
            background-color: #fff;
            border-radius: 12px;
        }
        """)
