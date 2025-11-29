from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QLabel, QVBoxLayout

from models.query import get_all_groups


class AddToGroup(QDialog):

    def __init__(self, parent=None):
        super(AddToGroup, self).__init__(parent)
        self.setWindowTitle("设置分组")
        self.setWindowIcon(QIcon("assets/grid.svg"))
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("选择用户分组"))

        self.groups_list = QComboBox()
        self.groups_list.addItems(self.get_all_groups())

        button_box = QDialogButtonBox(QDialogButtonBox.Ok
                                      | QDialogButtonBox.Cancel)
        ok_button = button_box.button(QDialogButtonBox.Ok)
        if ok_button:
            ok_button.setText("确定")
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        if cancel_button:
            cancel_button.setText("取消")

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        self.layout().addWidget(self.groups_list)
        self.layout().addWidget(button_box)

    def get_group_id(self):
        return self._data[self.groups_list.currentText()]

    def get_all_groups(self):
        self._data = {}
        group_names = []
        groups = get_all_groups()
        for group in groups:
            self._data[group['name']] = group['id']
            group_names.append(group['name'])
        return group_names
