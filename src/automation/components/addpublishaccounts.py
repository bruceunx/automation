from PySide6.QtCore import QSize, Slot
from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QListView,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from components.addusergroup import CheckBoxDelegate, CheckableListModel
from models.query import (
    get_all_groups,
    get_users_in_group,
    get_users_in_platform,
)
from utils import LOGIN_METADATA, Platform
from utils.constant import PublishType

article_platforms = [
    Platform.XHS,
    Platform.ZH,
    Platform.WX,
    Platform.BiliBili,
    Platform.TT,
    Platform.DY,
    Platform.KS,
]

video_platforms = [
    Platform.XHS,
    Platform.ZH,
    Platform.XG,
    Platform.BiliBili,
    Platform.TT,
    Platform.DY,
    Platform.KS,
]


class GroupUsers(QWidget):
    def __init__(self, users, parent=None):
        super(GroupUsers, self).__init__(parent)

        for user in users:
            user["checked"] = Qt.Unchecked
            _, user["platform_title"] = Platform.from_value(user["platform"])
        self.setLayout(QHBoxLayout())

        self.list_view = QListView()

        self.model = CheckableListModel(users)
        delegate = CheckBoxDelegate()

        self.list_view.setModel(self.model)
        self.list_view.setItemDelegate(delegate)

        self.layout().addWidget(self.list_view)

        self.select_all = QCheckBox("全部")
        self.layout().addWidget(self.select_all, 0, Qt.AlignmentFlag.AlignTop)

        self.select_all.checkStateChanged.connect(self.model.handle_select_all)
        self.setStyleSheet("""
            QListView {
                padding: 10px;
                background-color: #fff;
                border:none;
                border-radius: 7px;
            }
        """)

        self.layout().setContentsMargins(0, 0, 0, 0)


class UseMemAccounts(QDialog):
    def __init__(self, users: list, parent=None):
        super(UseMemAccounts, self).__init__(parent)
        self.added_user_ids: set[int] = set()
        self.setWindowTitle("选择记忆用户")
        self.setWindowIcon(QIcon("assets/users-d.svg"))
        self.setLayout(QVBoxLayout())
        inner_widget = GroupUsers(users)

        inner_widget.model.user_ids.connect(self.handle_checked_user_ids)
        self.layout().addWidget(inner_widget)

        button_box = QDialogButtonBox()
        button_box.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.setText("确定")

        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        cancel_button.setText("取消")

        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: 1px solid #4CAF50;
                padding: 5px 15px;
                font-size: 14px;
                border-radius: 7px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        cancel_button.setStyleSheet("""
            QPushButton {
                border-radius: 7px;
                background-color: #f44336;
                color: white;
                border: 1px solid #f44336;
                padding: 5px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e53935;
            }
        """)

        button_box.accepted.connect(self.before_accept)
        button_box.rejected.connect(self.reject)

        self.layout().addWidget(button_box)

    @Slot(list, list)
    def handle_checked_user_ids(self, checked_ids, unchecked_ids):
        self.added_user_ids |= set(checked_ids)
        self.added_user_ids -= set(unchecked_ids)

    def before_accept(self):
        if len(self.added_user_ids) == 0:
            QMessageBox.warning(self, "未选择用户", "没有选择用户!")
            return
        self.accept()


class AddPublishAccounts(QDialog):
    Style = """
    #leftmenu {
        background-color: #fff;
    }
    QPushButton {
        text-align: left;
        padding: 7 10;
        border: none;
        background-color: #eee;
    }
    QPushButton:hover {
        background-color: #B6E0F7;
    }
    QPushButton:pressed,QPushButton:checked {
        background-color: #A3D8F5;
    }
    """

    def __init__(self, publish_type: PublishType, parent=None):
        super(AddPublishAccounts, self).__init__(parent)
        self._publish_type = publish_type
        self.added_user_ids: set[int] = set()
        self.setWindowTitle("添加发布用户")
        self.setWindowIcon(QIcon("assets/users-d.svg"))

        self.addComponents()
        self.addStyle()

    def addComponents(self):
        self.setLayout(QHBoxLayout())
        content = QFrame()
        content.setObjectName("content")
        content.setLayout(QHBoxLayout())
        self.layout().addWidget(content)

        leftmenu = QFrame()
        leftmenu.setObjectName("leftmenu")
        leftmenu.setLayout(QVBoxLayout())
        leftmenu.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        content.layout().addWidget(leftmenu)

        right_frame = QFrame()
        right_frame.setLayout(QVBoxLayout())
        content.layout().addWidget(right_frame)

        self.stack = QStackedWidget()
        right_frame.layout().addWidget(self.stack)

        button_box = QDialogButtonBox()
        button_box.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.setText("确定")

        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        cancel_button.setText("取消")

        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: 1px solid #4CAF50;
                padding: 5px 15px;
                font-size: 14px;
                border-radius: 7px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        cancel_button.setStyleSheet("""
            QPushButton {
                border-radius: 7px;
                background-color: #f44336;
                color: white;
                border: 1px solid #f44336;
                padding: 5px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e53935;
            }
        """)

        button_box.accepted.connect(self.before_accept)
        button_box.rejected.connect(self.reject)

        right_frame.layout().addWidget(button_box)
        right_frame.setMinimumWidth(400)

        self.btn_groups = QButtonGroup()

        if self._publish_type == PublishType.Article:
            platforms = article_platforms
        else:
            platforms = video_platforms

        for idx, platform in enumerate(platforms):
            meta_data = LOGIN_METADATA[platform]
            btn = QPushButton(meta_data["title"])
            btn.setIcon(QIcon(meta_data["icon"]))
            btn.setIconSize(QSize(20, 20))
            btn.setCheckable(True)
            self.btn_groups.addButton(btn, idx)
            leftmenu.layout().addWidget(btn)

            group_users_w = GroupUsers(get_users_in_platform(platform))
            group_users_w.model.user_ids.connect(self.handle_checked_user_ids)

            self.stack.addWidget(group_users_w)

        # add line

        for idx, group in enumerate(self.get_all_groups(), start=len(platforms)):
            btn = QPushButton(group["name"])
            btn.setCheckable(True)
            self.btn_groups.addButton(btn, idx)
            leftmenu.layout().addWidget(btn)
            group_users_w = GroupUsers(get_users_in_group(group["id"]))
            group_users_w.model.user_ids.connect(self.handle_checked_user_ids)

            self.stack.addWidget(group_users_w)

        for btn in self.btn_groups.buttons():
            btn.setChecked(True)
            break

        self.btn_groups.idClicked.connect(self.handle_group_switch)

        leftmenu.layout().setContentsMargins(5, 5, 5, 0)
        right_frame.layout().setContentsMargins(0, 0, 0, 0)
        content.layout().setContentsMargins(0, 0, 0, 0)
        leftmenu.layout().setSpacing(2)

    @Slot(int)
    def handle_group_switch(self, idx: int):
        self.stack.setCurrentIndex(idx)

    @Slot(list, list)
    def handle_checked_user_ids(self, checked_ids, unchecked_ids):
        self.added_user_ids |= set(checked_ids)
        self.added_user_ids -= set(unchecked_ids)

    def addStyle(self):
        self.setStyleSheet(self.Style)

    def get_all_groups(self):
        # groups [ {id, name}]
        groups = get_all_groups()
        return groups

    def before_accept(self):
        if len(self.added_user_ids) == 0:
            QMessageBox.warning(self, "未选择用户", "没有选择用户!")
            return
        self.accept()
