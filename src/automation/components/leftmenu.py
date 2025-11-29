import base64
import json

from PySide6.QtCore import QSize, Signal, Slot
from PySide6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QCursor,
    QIcon,
    QImage,
    QPainter,
    QPainterPath,
    QPixmap,
    Qt,
)
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QGridLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from models.query import (
    get_all_groups,
    get_all_users,
    get_user_by_id,
    get_users_in_group,
    search_users_by_name,
)
from utils import Platform
from components.addaccount import AddAccount, LoginandSave


class Account(QWidget):
    Style = """
        QLabel {
            color: #777;
            font-size: 12px;
        }
    """

    creator_info = Signal(str, list, Platform)

    def __init__(self, account: dict, parent=None):
        super(Account, self).__init__(parent)
        self._username = account["name"]
        self._platform, self._title = Platform.from_value(account["platform"])
        self._icon_bytes = base64.b64decode(account["icon_raw"])

        self._state = False

        self._is_active = account["is_active"]

        self._cookies = json.loads(account["cookies"])
        self._id = account["id"]

        self.addComponents()
        self.addStyle()

    def update_cookies(self, cookies):
        self._cookies = cookies
        self._is_active = True

    def addComponents(self):
        content = QFrame()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(content)
        content.setLayout(QGridLayout())
        self.image_label = QLabel()
        self.image_label.setFixedSize(40, 40)
        content.layout().addWidget(self.image_label, 0, 0, 2, 1)

        content.layout().addWidget(QLabel(self._username), 0, 1)

        account_type = QLabel(self._title)
        account_type.setFixedHeight(20)
        account_type.setStyleSheet("""
            QLabel {
                font-size: 10px;
                border-radius: 10px;
                color: #777;
                padding-left: 3px;
                padding-right: 3px;
                background-color: #e0e0e0;
            }
        """)

        content.layout().addWidget(account_type, 1, 1, Qt.AlignmentFlag.AlignLeft)
        content.layout().setColumnStretch(0, 1)
        content.layout().setColumnStretch(1, 2)

        pixmap = QPixmap()
        pixmap.loadFromData(self._icon_bytes)
        scaled_pixmap = pixmap.scaled(
            QSize(40, 40), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        self.active_image = self.create_rounded_pixmap(scaled_pixmap)
        self.inactive_image = self.create_rounded_pixmap(
            self.convert_to_grayscale(scaled_pixmap)
        )

        if self._is_active == 0:
            self.image_label.setPixmap(self.inactive_image)
        else:
            self.image_label.setPixmap(self.active_image)

        self.layout().setContentsMargins(0, 0, 0, 0)

    def addStyle(self):
        self.setStyleSheet(self.Style)

    @Slot(bool)
    def update_active(self, value):
        if self.active_image is None:
            return
        if value:
            self.image_label.setPixmap(self.active_image)
        else:
            self.image_label.setPixmap(self.inactive_image)

    def create_rounded_pixmap(self, pixmap):
        radius = 20
        rounded = QPixmap(pixmap.size())
        rounded.fill(Qt.transparent)

        path = QPainterPath()
        path.addRoundedRect(0, 0, pixmap.width(), pixmap.height(), radius, radius)

        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return rounded

    def convert_to_grayscale(self, pixmap):
        image = pixmap.toImage()
        grayscale_image = image.convertToFormat(QImage.Format_Grayscale8)
        grayscale_pixmap = QPixmap.fromImage(grayscale_image)
        return grayscale_pixmap

    def enterEvent(self, event) -> None:
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        return super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self.unsetCursor()
        return super().leaveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            if not self._state:
                self.creator_info.emit(self._username, self._cookies, self._platform)
                self._state = True
                self.update()

    @Slot(str, Platform)
    def handle_close_info(self, username, platform_type):
        if self._username == username and self._platform == platform_type:
            self._state = False
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._state:
            painter = QPainter(self)
            transparent_red = QColor(224, 224, 224, 200)
            painter.setBrush(QBrush(transparent_red))
            painter.drawRect(self.rect())
            painter.end()

    def update_close(self):
        self._state = False
        self.update()


class AccountLeftMenu(QWidget):
    Style = """
    QLineEdit {
        padding-right: 10px;
        padding-top:5px;
        padding-bottom:5px;
        padding-left:5px;
        border-radius: 7px;
        border: 1px solid #ccc;
        background-color: #fff;
        color: #6c757d;
        font-size: 12px;
    }
    QToolButton{
        border-radius: 5;
        background-color: transparent;
        font-size: 12px;
        color: #6c757d;
        border: 1px solid #ccc;
        padding: 2px 3px;
    }
    QToolButton:hover{
        border: 1px solid #6e7f80;
    }
    QToolButton:pressed{
        border: 1px solid #6e7f80;
    }
    QPushButton {
        border: 1px solid #ccc;
        background-color: #fff;
        font-size:12pt;
        padding: 5px;
        border-radius: 10px;
    }
    QPushButton::hover {
        border: 1px solid #6e7f80;
    }

    QPushButton::pressed {
        border: 1px solid #6e7f80;
    }
    QComboBox {
        border: 1px solid #ccc;
        background-color: #fff;
        border-radius: 5px;
        padding: 5px;
        color: #555;
        font-size: 12px;
    }
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        background-color: #fff;
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
    #account_frame {
        background-color: #fff;
    }
    """

    update_account = Signal()

    def __init__(self, parent=None):
        super(AccountLeftMenu, self).__init__(parent)
        self.setFixedWidth(200)
        self.addComponents()
        self.addStyle()

        self.addWorkers()
        self.addConnections()

        self.afterInit()

    def addComponents(self):
        self.search_input = QLineEdit()
        self.account_add_btn = QToolButton()
        self.group_combo = QComboBox()
        self.refresh_btn = QToolButton()

        #############################################################
        content = QFrame()
        content.setLayout(QVBoxLayout())
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(content)
        content.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

        control_frame = QFrame()
        control_frame.setLayout(QGridLayout())
        content.layout().addWidget(control_frame)

        self.search_input.setPlaceholderText("搜索账号")

        self.search_action = QAction(QIcon("assets/search.svg"), "", self.search_input)
        self.search_input.addAction(
            self.search_action, QLineEdit.ActionPosition.TrailingPosition
        )

        self.account_add_btn.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
        self.account_add_btn.setText("账户")
        self.account_add_btn.setIcon(QIcon("assets/plus-square.svg"))
        self.account_add_btn.setIconSize(QSize(25, 25))

        self.group_combo.addItems(["全部分组"])

        self.refresh_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.refresh_btn.setText("刷新")
        self.refresh_btn.setIcon(QIcon("assets/refresh-ccw.svg"))
        self.refresh_btn.setIconSize(QSize(25, 25))

        control_frame.layout().addWidget(self.search_input, 0, 0)
        control_frame.layout().addWidget(self.account_add_btn, 0, 1)
        control_frame.layout().addWidget(self.group_combo, 1, 0)
        control_frame.layout().addWidget(self.refresh_btn, 1, 1)

        account_area = QScrollArea()
        account_area.setWidgetResizable(True)

        account_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        account_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content.layout().addWidget(account_area)
        self.account_frame = QFrame()
        self.account_frame.setLayout(QVBoxLayout())
        self.account_frame.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        self.account_frame.setObjectName("account_frame")
        account_area.setWidget(self.account_frame)

        self.account_btns = []
        for account in self.get_accounts():
            button = Account(account)
            self.account_btns.append(button)
            self.account_frame.layout().addWidget(button)

        self.account_frame.layout().setContentsMargins(0, 0, 0, 0)
        control_frame.layout().setContentsMargins(0, 0, 0, 0)
        content.layout().setContentsMargins(0, 0, 0, 0)
        content.layout().setSpacing(3)
        self.layout().setContentsMargins(0, 0, 0, 0)

    def addStyle(self):
        self.setStyleSheet(self.Style)

    def addWorkers(self):
        pass

    def addConnections(self):
        self.search_action.triggered.connect(self.on_search_icon_clicked)
        self.account_add_btn.clicked.connect(self.on_add_account)
        self.group_combo.currentTextChanged.connect(self.handle_group_change)
        self.refresh_btn.clicked.connect(self.handle_refresh_account)

    @Slot(str)
    def handle_group_change(self, group_name: str):
        if group_name != "全部分组":
            group_id = self._groups[group_name]
            users = get_users_in_group(group_id)
        else:
            users = get_all_users()
        self.update_account_widgets(users)

    def update_account_widgets(self, users):
        layout = self.account_frame.layout()
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
            self.account_btns.clear()

        for account in users:
            button = Account(account)
            self.account_btns.append(button)
            self.account_frame.layout().addWidget(button)
        self.update_account.emit()

    @Slot()
    def handle_refresh_account(self):
        group_name = self.group_combo.currentText()
        self.handle_group_change(group_name)

    def afterInit(self):
        # check user group and add groups
        self._groups = self.get_all_groups()
        self.group_combo.addItems(self._groups.keys())

    def on_search_icon_clicked(self):
        account_name = self.search_input.text().strip()
        if len(account_name) != 0:
            users = search_users_by_name(account_name)
            self.update_account_widgets(users)
        else:
            self.update_account_widgets(get_all_users())

    def on_add_account(self):
        account_dialog = AddAccount()
        if account_dialog.exec() == QDialog.Accepted:
            login_dialog = LoginandSave(account_dialog.choose_plafform)
            login_dialog.new_account.connect(self.handle_new_account)
            login_dialog.update_cookie.connect(self.handle_update_account)
            login_dialog.exec()

    def get_accounts(self):
        return get_all_users()

    @Slot(int)
    def handle_new_account(self, idx: int):
        new_account = get_user_by_id(idx)
        if new_account is not None:
            btn = Account(new_account)
            self.account_btns.append(btn)
            self.account_frame.layout().addWidget(btn)
            self.update_account.emit()

    @Slot(int, list)
    def handle_update_account(self, idx: int, cookies: list):
        for btn in self.account_btns:
            if btn._id == idx:
                btn.update_cookies(cookies)

    @Slot(int, int)
    def handle_update_account_active(self, idx: int, is_active: int):
        for btn in self.account_btns:
            if btn._id == idx:
                btn.update_active(bool(is_active))

    @Slot()
    def handle_close_all(self):
        for btn in self.account_btns:
            btn.update_close()

    def get_all_groups(self):
        groups = get_all_groups()
        return {group["name"]: group["id"] for group in groups}

    def filter_social_type(self, social_type: str) -> Platform:
        return Platform.from_str(social_type)
