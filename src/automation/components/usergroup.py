# import json

from PySide6.QtCore import QAbstractTableModel, QEvent, QModelIndex, QSize, Slot, Signal
from PySide6.QtGui import QBrush, QColor, QIcon, Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QTableView,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
# from PySide6.QtSvgWidgets import QSvgWidget

from components.addaccount import AddAccount, LoginandSave
from components.addtogroup import AddToGroup
from components.addusergroup import AddUserGroup, EditorUser, GroupsDelete
from components.useritem import (
    CustomWidgetDelegate,
    UserGroupNamesDelegate,
    CheckBoxDelegate,
)
from models.query import (
    add_users_to_group,
    delete_groups,
    get_all_groups,
    get_user_by_id,
    query_users_with_groups,
    remove_groups_from_user,
    update_user_state,
)


class CheckBoxHeader(QHeaderView):
    check_value = Signal(bool)

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.checkbox = QCheckBox(self)
        self.checkbox.stateChanged.connect(self.on_stateChanged)
        self.sectionResized.connect(self.update_checkbox_position)
        self.sectionCountChanged.connect(self.update_checkbox_position)

        self.setFixedHeight(50)

        self.setStyleSheet("""
            QHeaderView::section {
                background-color: #e0e0e0;
                border: none;
            }
            QCheckBox {
                background-color: #fff;
            }
        """)

    def on_stateChanged(self, state):
        print(f"Checkbox state changed to: {state}")
        self.check_value.emit(bool(state))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_checkbox_position()

    def update_checkbox_position(self):
        header_pos = self.sectionViewportPosition(0)
        header_width = self.sectionSize(0)
        header_height = self.height()
        checkbox_size = self.checkbox.sizeHint()

        checkbox_x = header_pos + (header_width - checkbox_size.width()) // 2
        checkbox_y = (header_height - checkbox_size.height()) // 2

        self.checkbox.setGeometry(
            checkbox_x, checkbox_y, checkbox_size.width(), checkbox_size.height()
        )


class UserGroupModel(QAbstractTableModel):
    selected_ids = Signal(list)

    def __init__(self):
        super().__init__()

        self.row_id = -1
        self._data = self.get_data()
        self._headers = [
            "",
            "序号",
            "账号",
            "分组",
            "登录状态",
            "操作",
        ]

    def get_data(self, usergroup_id: int = None):
        data = query_users_with_groups(usergroup_id)
        for row in data:
            row["select"] = False
        return data

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
            user = self._data[index.row()]
            column = index.column()

            if column == 0:
                return user["select"]
            elif column == 1:
                return user["user_id"]
            elif column == 2:
                return user["username"], user["icon_str"], user["platform"]
            elif column == 3:
                return user["groups"] if len(user["groups"]) else [(0, "未分组")]
            elif column == 4:
                return "登录正常" if user["is_active"] else "登录失效"
            else:
                return "编辑"

        elif role == Qt.EditRole:
            user = self._data[index.row()]
            column = index.column()
            if column == 0:
                return user["select"]

        elif role == Qt.ForegroundRole:
            user = self._data[index.row()]
            column = index.column()
            if column == 4:
                return QColor(0, 128, 0) if user["is_active"] else QColor(128, 0, 0)
            elif column == 5:
                return QColor(128, 0, 0)
            else:
                return QColor("#555")

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        elif role == Qt.BackgroundRole:
            if index.row() == self.row_id:
                return QBrush(QColor(240, 240, 240))
        return None

    def flags(self, index):
        return Qt.ItemIsEnabled

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        if role == Qt.EditRole:
            if index.column() == 0:
                self._data[index.row()]["select"] = value
            selected_ids = [
                row["user_id"] for row in self._data if row["select"] is True
            ]
            self.selected_ids.emit(selected_ids)
            return True
        return False

    def check_all(self, value):
        self.beginResetModel()
        for row in range(len(self._data)):
            self._data[row]["select"] = value
        self.endResetModel()

    @Slot(int)
    def change_group(self, group_id: int):
        self.beginResetModel()
        if group_id == 0:
            data = self.get_data()
        else:
            data = self.get_data(group_id)
        for row in data:
            row["select"] = False
        self._data = data
        self.endResetModel()

    def remove_groups_from_user(self, user_id, group_ids):
        self.beginResetModel()
        for row in self._data:
            if row["user_id"] == user_id:
                row["groups"] = [
                    item for item in row["groups"] if item[0] not in group_ids
                ]
        self.endResetModel()

    @Slot(int, int)
    def update_user_state(self, user_id, is_active):
        self.beginResetModel()
        for row in self._data:
            if row["user_id"] == user_id:
                row["is_active"] = is_active
        self.endResetModel()

    @Slot(int)
    def handle_hover_row(self, row_id: int):
        self.row_id = row_id
        self.modelReset.emit()


class UsersTableView(QTableView):
    test_user = Signal(dict)
    test_user_result = Signal(int)
    hover_row_id = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._current_hover_index = QModelIndex()

        self.clicked.connect(self.handle_clicked)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(70)

        self.header = CheckBoxHeader(Qt.Horizontal, self)
        self.setHorizontalHeader(self.header)
        self.setSelectionMode(QTableView.SelectionMode.NoSelection)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.setMouseTracking(True)
        self.viewport().installEventFilter(self)

        self.header.check_value.connect(self.handle_check_all)
        self.setShowGrid(False)

    def setModel(self, model):
        super().setModel(model)
        self.setColumnWidth(0, 200)

    @Slot(bool)
    def handle_check_all(self, value):
        self.model().check_all(value)

    @Slot()
    def check_state(self):
        button = self.sender()
        index = self.indexAt(button.pos())  # type: ignore
        if index.isValid():
            self.model()._data[index.row()][0] = button.isChecked()

    @Slot(QModelIndex)
    def handle_clicked(self, index: QModelIndex):
        if index.isValid():
            if index.column() == 5:
                user = self.model()._data[index.row()]  # type:ignore
                editor_dialog = EditorUser(user)
                editor_dialog.test_user.connect(self.handle_test_edit_account)
                editor_dialog.relogined.connect(self.handle_relogined)
                self.test_user_result.connect(editor_dialog.handle_test_result)
                if editor_dialog.exec() == QDialog.Accepted:  # type: ignore
                    remove_ids = editor_dialog.get_removed_group_ids()
                    remove_groups_from_user(user["user_id"], remove_ids)
                    self.model().remove_groups_from_user(  # type: ignore
                        user["user_id"], remove_ids
                    )

    @Slot(int)
    def handle_test_edit_account(self, user_id):
        user = get_user_by_id(user_id)
        self.test_user.emit(user)

    @Slot(int)
    def handle_relogined(self, user_id):
        self.model().update_user_state(user_id, 1)

    @Slot(int, int)
    def handle_test_account_result(self, user_id, is_active):
        if update_user_state(user_id, is_active):
            self.test_user_result.emit(is_active)
            self.model().update_user_state(user_id, is_active)

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

    def resizeEvent(self, event):
        super().resizeEvent(event)

        total_width = self.viewport().width()
        self.setColumnWidth(0, int(total_width * 0.1))
        self.setColumnWidth(1, int(total_width * 0.1))
        self.setColumnWidth(2, int(total_width * 0.3))
        self.setColumnWidth(3, int(total_width * 0.3))
        self.setColumnWidth(4, int(total_width * 0.1))
        self.setColumnWidth(5, int(total_width * 0.1))


class UserGroupManagerHeader(QWidget):
    Style = """

    QToolButton{
        padding: 5 5;
        border-radius: 7;
        background-color: #0267C1;
        color: #fff;
        font-size: 10pt;
    }
    QToolButton:hover{
        background-color: #0075C4;
    }
    QToolButton:pressed{
        background-color: #0075C4;
    }

    QPushButton {
        background-color: #fff;
        color: #333;
        border-radius: 7;
        padding: 5 10;
        font-size: 10pt;
        border: 1px solid #ddd;
    }
    QPushButton:hover,QPushButton:pressed{
        color: #0267C1;
        border: 1px solid #0267C1;
    }
    QPushButton:disabled {
        background-color: #f0f0f0;
        color: #999;
        border-radius: 7;
        padding: 5 10;
        font-size: 10pt;
        border: 1px solid #ccc;
    }
    """

    new_group = Signal(int, str)
    update_signal = Signal()
    removed_group_ids = Signal(list)

    def __init__(self, parent=None):
        super(UserGroupManagerHeader, self).__init__()
        self._selected_ids = []
        self.addComponents()
        self.addStyle()
        self.addConnections()

    def addComponents(self):
        self.setLayout(QHBoxLayout())

        left_frame = QFrame()
        right_frame = QFrame()
        left_frame.setLayout(QHBoxLayout())
        right_frame.setLayout(QHBoxLayout())

        left_frame.layout().setAlignment(Qt.AlignmentFlag.AlignLeft)
        right_frame.layout().setAlignment(Qt.AlignmentFlag.AlignRight)

        self.add_account_btn = QToolButton()
        self.add_account_btn.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
        self.add_account_btn.setText("添加用户")
        self.add_account_btn.setIcon(QIcon("assets/plus.svg"))
        self.add_account_btn.setIconSize(QSize(20, 20))
        left_frame.layout().addWidget(self.add_account_btn)

        self.add_group_btn = QToolButton()
        self.add_group_btn.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
        self.add_group_btn.setText("添加分组")
        self.add_group_btn.setIcon(QIcon("assets/grid.svg"))
        self.add_group_btn.setIconSize(QSize(20, 20))
        left_frame.layout().addWidget(self.add_group_btn)

        self.test_accounts_state = QPushButton("一键检测登录状态")
        right_frame.layout().addWidget(self.test_accounts_state)
        self.batch_addto_group_btn = QPushButton("批量设置分组")
        right_frame.layout().addWidget(self.batch_addto_group_btn)
        self.user_group_btn = QPushButton("分组管理")
        right_frame.layout().addWidget(self.user_group_btn)

        self.layout().addWidget(left_frame)
        self.layout().addWidget(right_frame)

        left_frame.layout().setContentsMargins(0, 0, 0, 0)
        right_frame.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)

    def addStyle(self):
        self.setStyleSheet(self.Style)

    def addConnections(self):
        self.test_accounts_state.clicked.connect(self.handle_test_accounts)

        self.add_account_btn.clicked.connect(self.handle_add_account)
        self.add_group_btn.clicked.connect(self.handle_add_group)
        self.batch_addto_group_btn.clicked.connect(self.handle_batch_addto_group)

        self.user_group_btn.clicked.connect(self.handle_group_manage)

    @Slot()
    def handle_test_accounts(self):
        self.test_accounts_state.setEnabled(False)

    @Slot(float)
    def handle_test_progress(self, progress: float):
        if progress == 1:
            self.test_accounts_state.setEnabled(True)

    @Slot(int, str)
    def handle_new_group(self, group_id, group_name):
        self.new_group.emit(group_id, group_name)

    def handle_add_group(self):
        add_group_dialog = AddUserGroup()
        add_group_dialog.new_group.connect(self.handle_new_group)
        add_group_dialog.exec()

    def handle_batch_addto_group(self):
        if len(self._selected_ids) == 0:
            QMessageBox.warning(self, "未选择用户", "没有选择用户!")
            return
        chose_group = AddToGroup()
        if chose_group.exec() == QDialog.Accepted:
            group_id = chose_group.get_group_id()
            add_users_to_group(self._selected_ids, group_id)
            # update user group table
            self.update_signal.emit()

    @Slot(list)
    def update_selected_id(self, user_ids: list[int]):
        self._selected_ids = user_ids

    @Slot()
    def handle_group_manage(self):
        group_manager = GroupsDelete()
        if group_manager.exec() == QDialog.Accepted:
            group_ids = group_manager.get_checked_groups()
            if len(group_ids) > 0:
                delete_groups(group_ids)
                self.removed_group_ids.emit(group_ids)

    @Slot()
    def handle_add_account(self):
        account_dialog = AddAccount()
        if account_dialog.exec() == QDialog.Accepted:
            login_dialog = LoginandSave(account_dialog.choose_plafform)
            # login_dialog.new_account.connect(self.handle_new_account)
            # login_dialog.update_cookie.connect(self.handle_update_account)
            login_dialog.exec()
            self.update_signal.emit()


class UserGroupLeftBar(QWidget):
    Style = """
    #content_frame {
        background-color: #eee;
        border-bottom-left-radius: 15px;
    }
    #all_btn{
        border: none;
        border-radius: none;
        background-color: #006ba6;
        padding: 10px;
        color: #fff;
    }
    #all_btn:hover{
        background-color: #0088cc;
    }
    #all_btn:pressed,#all_btn:checked {
        background-color: #005280;
    }
    QPushButton {
        border: none;
        border-radius: none;
        background-color: #ccc;
        padding: 5px;
        color: #555;
    }
    QPushButton:hover,QPushButton:pressed,QPushButton:checked {
        background-color: #aaa;
    }
    """
    current_group_id = Signal(int)

    def __init__(self, parent=None):
        super(UserGroupLeftBar, self).__init__()
        self.all_groups = self.get_all_groups()
        self.groups = {}
        self.addComponents()
        self.addStyle()
        self.addConnections()
        self.setFixedWidth(150)

    def addComponents(self):
        self.setLayout(QVBoxLayout())
        content_frame = QFrame()
        content_frame.setObjectName("content_frame")
        content_frame.setLayout(QVBoxLayout())
        content_frame.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

        self.all_btn = QPushButton("全部分组")
        self.all_btn.setObjectName("all_btn")

        content_frame.layout().addWidget(self.all_btn)
        self.all_groups_frame = QFrame()
        self.all_groups_frame.setLayout(QVBoxLayout())

        self.layout().addWidget(content_frame)

        content_frame.layout().addWidget(self.all_groups_frame)

        content_frame.layout().setSpacing(2)
        content_frame.layout().setContentsMargins(0, 0, 0, 0)
        self.all_groups_frame.layout().setContentsMargins(0, 5, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.btn_group = QButtonGroup()
        self.btn_group.addButton(self.all_btn, 0)

        self.all_btn.setCheckable(True)
        self.all_btn.setChecked(True)
        self.update_groups()

    def update_groups(self):
        for group in self.all_groups:
            btn = QPushButton(group["name"])
            btn.setCheckable(True)
            self.all_groups_frame.layout().addWidget(btn)
            self.groups[group["id"]] = btn
            self.btn_group.addButton(btn, group["id"])

    def addConnections(self):
        self.btn_group.buttonClicked.connect(self.handle_clicked)

    def handle_clicked(self, button):
        self.current_group_id.emit(self.btn_group.id(button))

    @Slot()
    def callback_update_group(self):
        checked_button = self.btn_group.checkedButton()
        self.current_group_id.emit(self.btn_group.id(checked_button))

    def addStyle(self):
        self.setStyleSheet(self.Style)

    def get_all_groups(self):
        return get_all_groups()

    @Slot(int, str)
    def add_new_group(self, group_id: int, group_name: str):
        btn = QPushButton(group_name)
        btn.setCheckable(True)
        self.all_groups_frame.layout().addWidget(btn)
        self.groups[group_id] = btn
        self.btn_group.addButton(btn, group_id)

    @Slot(list)
    def callback_remove_groups(self, group_ids: list[int]):
        checked_button = self.btn_group.checkedButton()
        current_id = self.btn_group.id(checked_button)

        for group_id in group_ids:
            btn = self.btn_group.button(group_id)
            if btn:
                self.all_groups_frame.layout().removeWidget(btn)
                self.btn_group.removeButton(btn)
                btn.deleteLater()
        if current_id in group_ids:
            self.current_group_id.emit(0)
        else:
            self.current_group_id.emit(current_id)


class UserGroupManager(QWidget):
    update_group_id = Signal(int)

    def __init__(self, parent=None):
        super(UserGroupManager, self).__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.addComponents()
        self.addStyle()
        self.addConnections()
        self.current_group_id = 0

    def addComponents(self):
        self.left_bar = UserGroupLeftBar()
        self.header_bar = UserGroupManagerHeader()
        self.user_table = UsersTableView()

        self.setObjectName("content")
        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(self.left_bar)

        right_frame = QFrame()
        right_frame.setLayout(QVBoxLayout())
        right_frame.setObjectName("right_frame")
        layout.addWidget(right_frame)

        right_frame.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        right_frame.layout().addWidget(self.header_bar)

        self.model = UserGroupModel()
        self.user_table.setModel(self.model)

        self.d0 = CheckBoxDelegate()
        self.d2 = CustomWidgetDelegate()
        self.d3 = UserGroupNamesDelegate()

        self.user_table.setItemDelegateForColumn(0, self.d0)
        self.user_table.setItemDelegateForColumn(2, self.d2)
        self.user_table.setItemDelegateForColumn(3, self.d3)

        right_frame.layout().addWidget(self.user_table)

    def addConnections(self):
        self.left_bar.current_group_id.connect(self.model.change_group)
        self.update_group_id.connect(self.model.change_group)
        self.left_bar.current_group_id.connect(self.handle_current_group_id)
        self.header_bar.new_group.connect(self.left_bar.add_new_group)

        self.model.selected_ids.connect(self.header_bar.update_selected_id)

        self.header_bar.update_signal.connect(self.left_bar.callback_update_group)

        self.header_bar.removed_group_ids.connect(self.left_bar.callback_remove_groups)

        self.header_bar.update_signal.connect(self.update_account)

        self.user_table.hover_row_id.connect(self.d0.handle_row_id)
        self.user_table.hover_row_id.connect(self.d2.handle_row_id)
        self.user_table.hover_row_id.connect(self.d3.handle_row_id)

        self.user_table.hover_row_id.connect(self.model.handle_hover_row)

    @Slot(int)
    def handle_current_group_id(self, group_id: int):
        self.current_group_id = group_id

    @Slot()
    def update_account(self):
        self.update_group_id.emit(self.current_group_id)

    def addStyle(self):
        self.setStyleSheet("""
        #content {
            background-color: #fff;
            border-radius: 10px;
        }
        #right_frame {
            background-color: #fff;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        }
        QTableView {
            background-color: #fff;
            border: none;
        }
        QTableView QHeaderView {
            border: none;
            background-color: #e0e0e0;
            color: #555;
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
        """)
