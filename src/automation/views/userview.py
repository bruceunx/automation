from PySide6.QtCore import Slot
from PySide6.QtWidgets import QHBoxLayout, QWidget

from components.creatorswidget import CreatorsWidget
from components.leftmenu import AccountLeftMenu


class AccountView(QWidget):

    Style = """
    """

    def __init__(self, parent=None):
        super(AccountView, self).__init__(parent)
        self.addComponents()
        self.addStyle()

        self.addWorkers()
        self.addConnections()

        self.afterInit()

    def addComponents(self):
        self.setLayout(QHBoxLayout())

        self.left_menu = AccountLeftMenu()
        self.left_menu.setObjectName("left_menu")
        self.layout().addWidget(self.left_menu)

        self.creators_widgets = CreatorsWidget()
        self.creators_widgets.setObjectName("creators_widgets")
        self.layout().addWidget(self.creators_widgets)

        self.layout().setSpacing(5)

    def addStyle(self):
        self.setStyleSheet(self.Style)

    def addWorkers(self):
        pass

    def addConnections(self):
        self.left_menu.update_account.connect(self.handle_update_account)
        self.creators_widgets.webviews.close_all.connect(
            self.left_menu.handle_close_all)
        self.handle_update_account()

    @Slot()
    def handle_update_account(self):
        for button in self.left_menu.account_btns:
            button.creator_info.connect(
                self.creators_widgets.webviews.add_new_tab)
            self.creators_widgets.webviews.close_account.connect(
                button.handle_close_info)

    def afterInit(self):
        pass
