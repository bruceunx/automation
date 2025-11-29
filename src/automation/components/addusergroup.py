import base64

from PySide6.QtCore import (
    QAbstractListModel,
    QEvent,
    QModelIndex,
    QRect,
    QSize,
    Signal,
    Slot,
    Qt as QtCoreQt,
)
from PySide6.QtGui import QColor, QIcon, QImage, QPalette, QPixmap, Qt
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QMessageBox,
    QPushButton,
    QStyle,
    QStyleOptionButton,
    QStyledItemDelegate,
    QVBoxLayout,
)

from components.addaccount import LoginandSave
from models.query import (
    add_user_group,
    add_users_to_group,
    check_if_usergroup_exists,
    delete_user,
    get_all_groups,
    get_all_users,
)
from utils.constant import Platform

ImageDataRole = QtCoreQt.ItemDataRole.UserRole + 1
ActiveDataRole = QtCoreQt.ItemDataRole.UserRole + 2


class CheckBoxDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if not index.isValid():
            return

        checked = index.data(Qt.CheckStateRole) == Qt.Checked
        text = index.data(Qt.DisplayRole)
        image_str = index.data(ImageDataRole)
        is_active = index.data(ActiveDataRole)
        if is_active == 0:
            text += "  (登录失效)"

        check_box_style_option = QStyleOptionButton()
        check_box_style_option.state |= QStyle.State_Enabled
        check_box_style_option.state |= QStyle.State_Active
        if checked:
            check_box_style_option.state |= QStyle.State_On
            painter.setPen(QColor(0, 0, 180))
        else:
            check_box_style_option.state |= QStyle.State_Off
            painter.setPen(option.palette.color(QPalette.Text))
        check_box_style_option.rect = self.get_check_box_rect(option)

        QApplication.style().drawControl(
            QStyle.CE_CheckBox, check_box_style_option, painter
        )

        if image_str is not None:
            image = QImage.fromData(base64.b64decode(image_str))
            pixmap = QPixmap.fromImage(image).scaled(
                20,
                20,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            pixmap_rect = QRect(
                option.rect.left() + check_box_style_option.rect.width() + 5,
                option.rect.top(),
                pixmap.width(),
                pixmap.height(),
            )
            painter.drawPixmap(pixmap_rect, pixmap)

            text_rect = option.rect.adjusted(
                check_box_style_option.rect.width() + 10 + pixmap.width() + 5, 5, 0, 0
            )
        else:
            text_rect = option.rect.adjusted(
                check_box_style_option.rect.width() + 10, 5, 0, 0
            )
        painter.drawText(text_rect, text)

        # painter.drawText(
        #     option.rect.adjusted(check_box_style_option.rect.width() + 10, 5,
        #                          0, 0), text)

    def editorEvent(self, event, model, option, index):
        if not index.isValid():
            return False
        if event.type() == QEvent.MouseButtonPress:
            if self.get_check_box_rect(option).contains(event.pos()):
                current_state = index.data(Qt.CheckStateRole)
                new_state = (
                    Qt.Checked if current_state == Qt.Unchecked else Qt.Unchecked
                )
                model.setData(index, new_state, Qt.CheckStateRole)
                return True
        return False

    def get_check_box_rect(self, option):
        check_box_style_option = QStyleOptionButton()
        rect = QApplication.style().subElementRect(
            QStyle.SE_CheckBoxIndicator, check_box_style_option, None
        )
        return QRect(
            option.rect.left(),
            option.rect.center().y() - rect.height() // 2,
            rect.width(),
            rect.height(),
        )

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(size.height() + 10)
        return size


class CheckableListModel(QAbstractListModel):
    user_ids = Signal(list, list)

    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        self.items = items or []

    def data(self, index, role):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            row = self.items[index.row()]
            return f"{row['name']} - {row['platform_title']}"

        if role == Qt.CheckStateRole:
            return self.items[index.row()]["checked"]

        if role == ImageDataRole:
            return self.items[index.row()]["icon_raw"]

        if role == ActiveDataRole:
            return self.items[index.row()]["is_active"]

        return None

    def rowCount(self, parent=QModelIndex()):
        return len(self.items)

    def setData(self, index, value, role):
        if not index.isValid():
            return False

        if role == Qt.CheckStateRole:
            print(value)
            self.items[index.row()]["checked"] = value
            self.dataChanged.emit(index, index, [Qt.CheckStateRole])
            self.get_checked_users()
        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable

    def get_checked_users(self):
        checked_ids = []
        unchecked_ids = []
        for user in self.items:
            if user["checked"] == Qt.Checked:
                checked_ids.append(user["id"])
            else:
                unchecked_ids.append(user["id"])
        self.user_ids.emit(checked_ids, unchecked_ids)

    def handle_select_all(self, value):
        self.beginResetModel()
        for item in self.items:
            item["checked"] = value
        self.endResetModel()
        self.get_checked_users()


class GroupCheckableListModel(QAbstractListModel):
    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        self.items = items or []

    def data(self, index, role):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            row = self.items[index.row()]
            return f"{row['name']}"

        if role == Qt.CheckStateRole:
            return self.items[index.row()]["checked"]

        return None

    def rowCount(self, parent=QModelIndex()):
        return len(self.items)

    def setData(self, index, value, role):
        if not index.isValid():
            return False

        if role == Qt.CheckStateRole:
            self.items[index.row()]["checked"] = value
            self.dataChanged.emit(index, index, [Qt.CheckStateRole])

        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable

    def get_checked_groups(self):
        group_ids = []
        for group in self.items:
            if group["checked"] == Qt.Checked:
                group_ids.append(group["id"])
        return group_ids

    def get_checked_group_names(self):
        group_names = []
        for group in self.items:
            if group["checked"] == Qt.Checked:
                group_names.append(group["name"])
        return group_names

    def remove_groups(self, group_ids):
        self.beginResetModel()
        self.items = [item for item in self.items if item["id"] not in group_ids]
        self.endResetModel()


class UserListView(QDialog):
    def __init__(self, parent=None):
        super(UserListView, self).__init__(parent)
        self.setFixedSize(400, 500)
        self.setWindowTitle("选择用户")
        self.setWindowIcon(QIcon("assets/users-d.svg"))

        self.list_view = QListView()

        self.model = CheckableListModel(self.get_all_users())
        delegate = CheckBoxDelegate()

        self.list_view.setModel(self.model)
        self.list_view.setItemDelegate(delegate)

        layout = QVBoxLayout()
        layout.addWidget(self.list_view)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ok_button = button_box.button(QDialogButtonBox.Ok)
        if ok_button:
            ok_button.setText("添加用户")
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        if cancel_button:
            cancel_button.setText("取消")

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

        self.setLayout(layout)
        self.setStyleSheet("""
            QListView {
                padding: 10px;
                background-color: #fff;
                border-radius: 10px;
                border: 1 solid rgba(0, 0, 200, 100);
                font-size: 14px;
                color: #333333;
            }
        """)

    def get_all_users(self):
        users = get_all_users()
        for user in users:
            user["checked"] = Qt.Unchecked
            _, user["platform_title"] = Platform.from_value(user["platform"])
        return users


class AddUserGroup(QDialog):
    Style = """
    QLabel {
        font-size: 17px;
        font-weight: bold;
        color: #555;
    }
    #content QLabel {
        font-weight: normal;
        font-size: 15px;
    }
    #content QLineEdit {
        padding: 5px 10px;
        font-weight: normal;
        font-size: 15px;
        border-radius: 10px;
    }
    #content QPushButton {
        background-color: rgba(0, 180, 0, 200);
        border-radius: 30px;
    }
    #content QPushButton:hover,QPushButton:pressed {
        background-color: rgba(0, 100, 0, 200);
    }
    QMessageBox {
        background-color: #353535;
        color: #ffffff;
        font: 14pt "Arial";
    }

    QMessageBox QPushButton {
        background-color: #555555;
        color: #ffffff;
        border: 1px solid #888888;
        padding: 5px 10px;
        font: 12pt "Arial";
    }

    QMessageBox QPushButton:hover {
        background-color: #777777;
    }

    QMessageBox QPushButton:pressed {
        background-color: #aaaaaa;
    }
    """
    new_group = Signal(int, str)

    def __init__(self, parent=None):
        super(AddUserGroup, self).__init__(parent)
        self.setWindowTitle("添加用户组")
        self.setWindowIcon(QIcon("assets/grid.svg"))
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint)

        self.setFixedSize(600, 300)
        self.addComponents()
        self.addStyle()
        self.addConnections()

    def addComponents(self):
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        title = QLabel("添加用户组")

        self.layout().addWidget(title)

        content = QFrame()
        content.setObjectName("content")
        content.setLayout(QFormLayout())
        self.group_input = QLineEdit()
        self.add_users = QPushButton()
        self.add_users.setIcon(QIcon("assets/plus.svg"))
        self.add_users.setIconSize(QSize(30, 30))
        self.add_users.setFixedSize(60, 60)
        self.group_input.setPlaceholderText("请输入分组名称")
        content.layout().addRow("分组", self.group_input)
        content.layout().addRow("添加用户", self.add_users)

        self.layout().addWidget(content)

    def addStyle(self):
        self.setStyleSheet(self.Style)

    def addConnections(self):
        self.add_users.clicked.connect(self.handle_add_users)

    def handle_add_users(self):
        group_name = self.group_input.text().strip()
        if len(group_name) == 0:
            return
        if check_if_usergroup_exists(group_name):
            QMessageBox.warning(self, "用户组已存在", "用户组名已存在!")
            return
        userlist_dialog = UserListView()
        if userlist_dialog.exec() == QDialog.Accepted:
            group_id = add_user_group(group_name)
            user_ids = userlist_dialog.model.get_checked_users()
            add_users_to_group(user_ids, group_id)
            self.new_group.emit(group_id, group_name)
            self.close()


class GroupsDelete(QDialog):
    def __init__(self, parent=None):
        super(GroupsDelete, self).__init__(parent)
        self.setFixedSize(400, 500)
        self.setWindowTitle("删除分组")
        self.setWindowIcon(QIcon("assets/grid.svg"))

        self.list_view = QListView()

        self.model = GroupCheckableListModel(self.get_all_groups())
        delegate = CheckBoxDelegate()

        self.list_view.setModel(self.model)
        self.list_view.setItemDelegate(delegate)

        layout = QVBoxLayout()
        layout.addWidget(self.list_view)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ok_button = button_box.button(QDialogButtonBox.Ok)
        if ok_button:
            ok_button.setText("确认删除")
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        if cancel_button:
            cancel_button.setText("取消")

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

        self.setLayout(layout)
        self.setStyleSheet("""
            QListView {
                padding: 10px;
                background-color: #fff;
                border-radius: 10px;
                border: 1 solid rgba(0, 0, 200, 100);
                font-size: 14px;
                color: #333333;
            }
        """)

    def get_all_groups(self):
        groups = get_all_groups()
        for group in groups:
            group["checked"] = Qt.Unchecked
        return groups

    def get_checked_groups(self):
        return self.model.get_checked_groups()


"""
        users_with_groups[user_id] = {
            "user_id": user_id,
            "username": username,
            "platform": platform,
            "icon_str": icon_str,
            "is_active": is_active,
            "groups": []
        }

"""


class EditorUser(QDialog):
    Style = """
    QListView {
        padding: 10px;
        background-color: #f9f9f9;
        border-radius: 10px;
        border: 1px solid rgba(200, 200, 200, 80);
        font-size: 14px;
        color: #444;
    }
    #title {
        font-size: 18px;
        font-weight: bold;
        color: #333;
        margin-bottom: 15px;
    }
    QFrame#content {
        background-color: #fff;
        border-radius: 10px;
        padding: 15px;
    }
    QLabel {
        font-size: 14px;
        color: #444;
    }
    QPushButton {
        padding: 8px 10px;
        border-radius: 7px;
        border: 1px solid rgba(180, 180, 180, 100);
        background-color: #eee;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color: #ddd;
        color: #DA4167;
    }
    QPushButton:pressed {
        background-color: #ccc;
        color: #DA4167;
    }
    """
    test_user = Signal(int)

    relogined = Signal(int)

    def __init__(self, user_info: dict, parent=None):
        super(EditorUser, self).__init__(parent)
        self._user_info = user_info
        self.setFixedSize(400, 500)
        self.setWindowTitle("编辑用户")
        self.setWindowIcon(QIcon("assets/users-d.svg"))

        self.addComponents()
        self.addStyle()
        self.addConnections()
        self._removed_group_ids: list[int] = []

    def addComponents(self):
        self.setLayout(QHBoxLayout())
        left_frame = QFrame()
        left_frame.setLayout(QVBoxLayout())
        self.layout().addWidget(left_frame)

        left_frame.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        title = QLabel("编辑用户")
        title.setObjectName("title")

        left_frame.layout().addWidget(title)

        content = QFrame()
        content.setObjectName("content")
        content.setLayout(QFormLayout())
        content.layout().setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        left_frame.layout().addWidget(content)

        self._platform, platform_title = Platform.from_value(
            self._user_info["platform"]
        )

        self.current_state = QLabel(
            "登录成功" if self._user_info["is_active"] else "登录失效"
        )

        content.layout().addRow("用户名:", QLabel(self._user_info["username"]))
        content.layout().addRow("平台:", QLabel(platform_title))
        content.layout().addRow("登录状态:", self.current_state)

        groups = []
        for group in self._user_info["groups"]:
            groups.append(dict(id=group[0], name=group[1], checked=Qt.Unchecked))

        self.list_view = QListView()

        self.model = GroupCheckableListModel(groups)
        delegate = CheckBoxDelegate()

        self.list_view.setModel(self.model)
        self.list_view.setItemDelegate(delegate)
        content.layout().addRow("所在分组:", self.list_view)

        control_frame = QFrame()
        control_frame.setLayout(QVBoxLayout())
        control_frame.layout().setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.layout().addWidget(control_frame)

        self.test_state = QPushButton("检测状态")
        self.login_btn = QPushButton("重新登录")
        self.delete_groups = QPushButton("删除分组")
        self.delete_user = QPushButton("删除用户")
        self.ok_btn = QPushButton("确定")
        self.close_btn = QPushButton("取消")

        control_frame.layout().addWidget(self.test_state)
        control_frame.layout().addWidget(self.login_btn)
        control_frame.layout().addWidget(self.delete_groups)
        control_frame.layout().addWidget(self.delete_user)
        control_frame.layout().addWidget(self.ok_btn)
        control_frame.layout().addWidget(self.close_btn)

        control_frame.setFixedWidth(100)

        self.ok_btn.setStyleSheet("""
        QPushButton {
            padding: 8px 10px;
            border-radius: 7px;
            border: 1px solid rgba(180, 180, 180, 100);
            background-color: #eee;
            font-size: 14px;
            color: #368F8B;
        }
        QPushButton:hover {
            background-color: #ddd;
            color: #268f8b;
        }
        QPushButton:pressed {
            background-color: #ccc;
            color: #148f8b;
        }
        """)
        self.close_btn.setStyleSheet("""
        QPushButton {
            padding: 8px 10px;
            border-radius: 7px;
            border: 1px solid rgba(180, 180, 180, 100);
            background-color: #eee;
            font-size: 14px;
            color: #555;
        }
        QPushButton:hover {
            background-color: #ddd;
            color: #444;
        }
        QPushButton:pressed {
            background-color: #ccc;
            color: #333;
        }
        """)

    def addStyle(self):
        self.setStyleSheet(self.Style)

    def addConnections(self):
        self.delete_groups.clicked.connect(self.handle_delete_groups)
        self.delete_user.clicked.connect(self.handle_delete_user)
        self.close_btn.clicked.connect(self.reject)
        self.ok_btn.clicked.connect(self.accept)

        self.test_state.clicked.connect(
            lambda: self.test_user.emit(self._user_info["user_id"])
        )

        self.login_btn.clicked.connect(self.handle_relogin)

    def handle_delete_groups(self):
        group_ids = self.model.get_checked_groups()
        self._removed_group_ids.extend(group_ids)
        self.model.remove_groups(group_ids)

    def handle_relogin(self):
        login = LoginandSave(self._platform)
        if login.exec() == QDialog.Accepted:
            self.current_state.setText("登录成功")
            self.relogined.emit(self._user_info["user_id"])

    def handle_delete_user(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("删除用户")
        msg_box.setWindowIcon(QIcon("assets/user-d.svg"))
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText("删除用户")
        msg_box.setInformativeText("确认删除用户！")

        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg_box.setDefaultButton(QMessageBox.Cancel)

        msg_box.button(QMessageBox.Ok).setText("确认")
        msg_box.button(QMessageBox.Cancel).setText("取消")

        if msg_box.exec() == QMessageBox.Ok:
            delete_user(self._user_info["user_id"])
            self.reject()

    def get_removed_group_ids(self):
        return self._removed_group_ids

    @Slot(int)
    def handle_test_result(self, is_active):
        print(f"{is_active = }")
        self._user_info["is_active"] = is_active
        self.current_state.setText("登录成功" if is_active else "登录失效")
