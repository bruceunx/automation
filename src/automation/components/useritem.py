import base64

from PySide6.QtCore import QRect, QSize, Slot
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPixmap, Qt, QMouseEvent
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QGridLayout,
    QLabel,
    QLineEdit,
    QStyle,
    QStyleFactory,
    QStyleOptionButton,
    QStyledItemDelegate,
    QVBoxLayout,
    QWidget,
)

from utils.constant import Platform


class GroupsItem(QWidget):
    def __init__(self, groups: list[str], hover: bool = False, parent=None):
        super(GroupsItem, self).__init__(parent)
        self.hover = hover
        content = QFrame()
        content.setObjectName("content")
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(content)
        content.setLayout(QGridLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        if len(groups) > 6:
            self.groups = groups[:5]
            content.layout().addWidget(
                QLabel("其他"), 2, 3, Qt.AlignmentFlag.AlignCenter
            )  # type: ignore
        else:
            self.groups = groups

        for index, group in enumerate(self.groups):
            row, col = divmod(index, 3)
            content.layout().addWidget(
                QLabel(group[1]), row, col, Qt.AlignmentFlag.AlignCenter
            )  # type: ignore

        if hover:
            _style = """
                #content {
                    background-color: rbg(240, 240, 240);
                }
            """
        else:
            _style = """
                #content {
                    background-color: #fff;
                }
            """

        if len(groups) == 1 and groups[0][1] == "未分组":
            _style += """
                QLabel {
                    font-size: 12px;
                    border-radius: 5px;
                    color: #fff;
                    padding: 3px;
                    background-color: #ccc;
                }
            """
        else:
            _style += """
                QLabel {
                    font-size: 12px;
                    border-radius: 5px;
                    color: #fff;
                    padding: 3px;
                    background-color: #3DA5D9;
                }
            """
        self.setStyleSheet(_style)


class AccountItem(QWidget):
    def __init__(
        self,
        username: str,
        icon_str: str,
        platform: int | Platform,
        hover: bool = False,
        parent=None,
    ):
        super(AccountItem, self).__init__(parent)
        self._username = username
        self._platform = platform
        self.hover = hover

        icon_bytes = base64.b64decode(icon_str)
        pixmap = QPixmap()
        pixmap.loadFromData(icon_bytes)
        scaled_pixmap = pixmap.scaled(
            QSize(40, 40),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.scaled_pixmap = self.create_rounded_pixmap(scaled_pixmap)
        if isinstance(platform, int):
            _, self._title = Platform.from_value(platform)
        else:
            self._title = platform.display_name
        self.addComponents()
        self.addStyle()

    def addComponents(self):
        content = QFrame()
        content.setObjectName("content")
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(content)
        content.setLayout(QGridLayout())
        self.image_label = QLabel()
        self.image_label.setPixmap(self.scaled_pixmap)
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
            }
        """)

        content.layout().addWidget(account_type, 1, 1, Qt.AlignmentFlag.AlignLeft)
        content.layout().setColumnStretch(0, 1)
        content.layout().setColumnStretch(1, 2)

        self.layout().setContentsMargins(0, 0, 0, 0)

    def addStyle(self):
        if self.hover:
            self.setStyleSheet("""
            #content {
                background-color: rgb(240, 240, 240);
            }
            QLabel {
                color: #777;
                font-size: 12px;
            }
            """)
        else:
            self.setStyleSheet("""
            #content {
                background-color: #fff;
            }
            QLabel {
                color: #777;
                font-size: 12px;
            }
            """)

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


class UserGroupNamesDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(UserGroupNamesDelegate, self).__init__()
        self.row_idx = -1

    def paint(self, painter, option, index):
        groups = index.model().data(index, Qt.DisplayRole)
        widget = GroupsItem(groups, hover=self.row_idx == index.row())
        widget.resize(option.rect.size())
        pixmap = widget.grab()
        painter.drawPixmap(option.rect, pixmap)

    @Slot(int)
    def handle_row_id(self, row_id: int):
        self.row_idx = row_id


class CustomWidgetDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(CustomWidgetDelegate, self).__init__(parent)
        self.row_idx = -1

    def paint(self, painter, option, index):
        data = index.model().data(index, Qt.DisplayRole)

        widget = AccountItem(*data, hover=index.row() == self.row_idx)
        widget.resize(option.rect.size())
        pixmap = widget.grab()
        painter.drawPixmap(option.rect, pixmap)

    @Slot(int)
    def handle_row_id(self, row_id: int):
        self.row_idx = row_id


class LineEditDelegate(QStyledItemDelegate):
    def __init__(self, *args, **kwars):
        super(LineEditDelegate, self).__init__(*args, **kwars)
        self.row_idx = -1

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setStyleSheet("""
            QLineEdit {
                background-color: red;
            }
        """)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        editor.setText(value)

    def setModelData(self, editor, model, index):
        value = editor.text()
        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    @Slot(int)
    def handle_row_id(self, row_id: int):
        self.row_idx = row_id


class NoFocusDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        option.state &= ~QStyle.State_HasFocus
        super(NoFocusDelegate, self).paint(painter, option, index)


class CheckBoxDelegate(QStyledItemDelegate):
    def __init__(self, *args, **kwars):
        super(CheckBoxDelegate, self).__init__(*args, **kwars)
        self.style = QStyleFactory.create("Fusion")
        self.row_idx = -1

    def paint(self, painter, option, index):
        if index.data() is None:
            return super().paint(painter, option, index)
        if index.row() == self.row_idx:
            painter.fillRect(option.rect, QColor(240, 240, 240))
        else:
            painter.fillRect(option.rect, QColor("#fff"))
        checked = bool(index.data())
        check_box_style_option = QStyleOptionButton()

        if checked:
            check_box_style_option.state |= QStyle.State_On
        else:
            check_box_style_option.state |= QStyle.State_Off

        check_box_style_option.rect = self.getCheckBoxRect(option)
        self.style.drawControl(QStyle.CE_CheckBox, check_box_style_option, painter)

    def createEditor(self, parent, option, index):
        check_box = QCheckBox(parent)
        check_box.setStyle(QStyleFactory.create("Fusion"))
        check_box.setStyleSheet("""
            QCheckBox {
                background-color: #ffffff;
            }
        """)
        check_box.stateChanged.connect(self.commitAndCloseEditor)
        return check_box

    def setEditorData(self, editor, index):
        if bool(index.data()):
            editor.setCheckState(Qt.Checked)
        else:
            editor.setCheckState(Qt.Unchecked)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.checkState() == Qt.Checked)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def commitAndCloseEditor(self):
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor)

    def getCheckBoxRect(self, option):
        check_box_style_option = QStyleOptionButton()
        check_box_rect = self.style.subElementRect(
            QStyle.SE_CheckBoxIndicator, check_box_style_option, None
        )
        check_box_point = option.rect.center() - check_box_rect.center()
        return QRect(check_box_point, check_box_rect.size())

    def editorEvent(self, event, model, option, index):
        if event.type() == QMouseEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                if self.getCheckBoxRect(option).contains(event.pos()):
                    current_value = index.data()
                    new_value = not current_value
                    model.setData(index, new_value)
        return super().editorEvent(event, model, option, index)

    @Slot(int)
    def handle_row_id(self, row_id: int):
        self.row_idx = row_id
