from PySide6.QtCore import Slot
from PySide6.QtWidgets import QListView, QVBoxLayout, QWidget

from components.addusergroup import CheckBoxDelegate, CheckableListModel
from utils.accounttype import PublishAccountType


class PublishAccountList(QWidget):

    def __init__(self, publish_account: PublishAccountType, parent=None):
        super(PublishAccountList, self).__init__(parent)

        self._publish_account = publish_account
        self.list_view = QListView()

        self.model = CheckableListModel()
        delegate = CheckBoxDelegate()

        self.list_view.setModel(self.model)
        self.list_view.setItemDelegate(delegate)

        layout = QVBoxLayout()
        layout.addWidget(self.list_view)

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

    @Slot(list)
    def update_accounts(self, accounts):
        for account in accounts:
            # check if the account is belonged to
            print(account)

    # def get_all_users(self):
    #     users = get_all_users()
    #     for user in users:
    #         user["checked"] = Qt.Unchecked
    #         _, user["platform_title"] = transform_value_to_platform(
    #             user["platform"])
    #     return users
