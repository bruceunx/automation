from PySide6.QtCore import QSize, Signal, Slot
from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import QButtonGroup, QFormLayout, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QRadioButton, QScrollArea, QStackedLayout, QVBoxLayout, QWidget

from components.addimage import AddImageCover
from utils import Platform

SettingStyle = """
    #scroll_area {
        border: none;
        background-color: transparent;
    }
    #scroll_area QFrame {
        background-color: transparent;
    }
    QScrollBar:vertical {
        background: transparent;
        width: 10px;
    }
    QScrollBar::handle:vertical {
        background: #ccc;
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

"""

XHSStyle = SettingStyle + """
    QRadioButton {
        font-size: 13px;
        color: #777;
    }
"""


class ArticlPlatformSetting(QWidget):

    def __init__(self, parent=None):
        super(ArticlPlatformSetting, self).__init__(parent)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("scroll_area")
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(scroll_area)
        self.content = QFrame()
        self.content.setLayout(QVBoxLayout())
        self.content.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_area.setWidget(self.content)

        self.content.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(SettingStyle)


class ArticleXHS(ArticlPlatformSetting):

    setting = Signal(dict)

    def __init__(self, parent=None):
        super(ArticleXHS, self).__init__(parent)

        self.content.layout().addWidget(QLabel("标签(选填)"))
        self.tags = QLineEdit()
        self.tags.setPlaceholderText("标签(以空格分开)")
        self.content.layout().addWidget(self.tags)

        self.content.layout().addWidget(QLabel("是否公开"))
        choose_layout = QHBoxLayout()
        pub_btn = QRadioButton("公开")
        nopub_btn = QRadioButton("仅我可见")
        choose_layout.addWidget(pub_btn)
        choose_layout.addWidget(nopub_btn)
        self.content.layout().addLayout(choose_layout)

        self.public_choose = QButtonGroup()
        self.public_choose.addButton(pub_btn, 0)
        self.public_choose.addButton(nopub_btn, 1)
        pub_btn.setChecked(True)

        self.setStyleSheet(XHSStyle)

        self.public_choose.idClicked.connect(self.handle_switch)
        self.tags.textEdited.connect(self.handle_tags)

    @Slot(int)
    def handle_switch(self, idx: int):
        is_public = 1 - idx
        self.setting.emit(dict(is_public=is_public, platform=Platform.XHS))

    @Slot(str)
    def handle_tags(self, text: str):
        self.setting.emit(dict(tags=text, platform=Platform.XHS))


class ArticleZH(ArticlPlatformSetting):

    setting = Signal(dict)

    def __init__(self, parent=None):
        super(ArticleZH, self).__init__(parent)

        self.content.layout().addWidget(QLabel("标题(选填)<100"))
        self.title = QLineEdit()
        self.title.setPlaceholderText("使用默认标题")
        self.content.layout().addWidget(self.title)

        self.title.textEdited.connect(self.handle_title)

    @Slot(str)
    def handle_title(self, text: str):
        self.setting.emit(dict(title=text, platform=Platform.ZH))


class ArticleWX(ArticlPlatformSetting):
    setting = Signal(dict)

    def __init__(self, parent=None):
        super(ArticleWX, self).__init__(parent)

        self.content.layout().addWidget(QLabel("作者"))
        self.author = QLineEdit()
        self.author.setPlaceholderText("默认admin")
        self.content.layout().addWidget(self.author)
        self.content.layout().addWidget(QLabel("标签"))
        self.tags = QLineEdit()
        self.tags.setPlaceholderText("标签(以空格分开)")
        self.content.layout().addWidget(self.tags)

        self.content.layout().addWidget(QLabel("是否公开"))
        choose_layout = QHBoxLayout()
        pub_btn = QRadioButton("公开")
        nopub_btn = QRadioButton("仅我可见")
        choose_layout.addWidget(pub_btn)
        choose_layout.addWidget(nopub_btn)
        self.content.layout().addLayout(choose_layout)

        self.public_choose = QButtonGroup()
        self.public_choose.addButton(pub_btn, 0)
        self.public_choose.addButton(nopub_btn, 1)
        pub_btn.setChecked(True)

        self.setStyleSheet(XHSStyle)

        self.public_choose.idClicked.connect(self.handle_switch)
        self.tags.textEdited.connect(self.handle_tags)
        self.author.textEdited.connect(self.handle_author)

    @Slot(int)
    def handle_switch(self, idx: int):
        is_public = 1 - idx
        self.setting.emit(dict(is_public=is_public, platform=Platform.WX))

    @Slot(str)
    def handle_tags(self, text: str):
        self.setting.emit(dict(tags=text, platform=Platform.WX))

    @Slot(str)
    def handle_author(self, text: str):
        self.setting.emit(dict(author=text, platform=Platform.WX))


class ArticleBiliBili(ArticlPlatformSetting):

    setting = Signal(dict)

    def __init__(self, parent=None):
        super(ArticleBiliBili, self).__init__(parent)

        self.content.layout().addWidget(QLabel("标题(选填)<20"))
        self.title = QLineEdit()
        self.title.setPlaceholderText("使用默认标题截取前20")
        self.content.layout().addWidget(self.title)

        self.content.layout().addWidget(QLabel("标签"))
        self.tags = QLineEdit()
        self.tags.setPlaceholderText("标签(以空格分开)")
        self.content.layout().addWidget(self.tags)

        self.title.textEdited.connect(self.handle_title)
        self.tags.textEdited.connect(self.handle_tags)

    @Slot(str)
    def handle_title(self, text: str):
        self.setting.emit(dict(platform=Platform.BiliBili, title=text))

    @Slot(str)
    def handle_tags(self, text: str):
        self.setting.emit(dict(platform=Platform.BiliBili, tags=text))


class ArticleSetting(QWidget):

    def __init__(self, parent=None):
        super(ArticleSetting, self).__init__(parent)
        self.setting = {}
        self.addComponents()
        self.addStyle()
        self.addConnections()

        self.setFixedWidth(300)

    def addComponents(self):
        self.setLayout(QHBoxLayout())

        #############################################################
        # left frame
        self.platforms_frame = QFrame()
        self.platforms_frame.setLayout(QVBoxLayout())
        self.platforms_frame.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

        self.platforms_frame.layout().addWidget(QLabel("平台"), 0,
                                                Qt.AlignmentFlag.AlignHCenter)
        self.platforms_frame.setObjectName("platforms_frame")

        self.platforms_btns = QButtonGroup()
        xhs_btn = QPushButton()
        xhs_btn.setIcon(QIcon("assets/icons/xhs.svg"))
        self.platforms_btns.addButton(xhs_btn, 0)

        zh_btn = QPushButton()
        zh_btn.setIcon(QIcon("assets/icons/zh.svg"))
        self.platforms_btns.addButton(zh_btn, 1)

        wx_btn = QPushButton()
        wx_btn.setIcon(QIcon("assets/icons/wx.svg"))
        self.platforms_btns.addButton(wx_btn, 2)

        bilibili_btn = QPushButton()
        bilibili_btn.setIcon(QIcon("assets/icons/bilibili.svg"))
        self.platforms_btns.addButton(bilibili_btn, 3)

        tt_btn = QPushButton()
        tt_btn.setIcon(QIcon("assets/icons/tt.svg"))
        self.platforms_btns.addButton(tt_btn, 4)

        dy_btn = QPushButton()
        dy_btn.setIcon(QIcon("assets/icons/dy.svg"))
        self.platforms_btns.addButton(dy_btn, 5)

        ks_btn = QPushButton()
        ks_btn.setIcon(QIcon("assets/icons/ks.svg"))
        self.platforms_btns.addButton(ks_btn, 6)

        for button in self.platforms_btns.buttons():
            self.platforms_frame.layout().addWidget(button)
            button.setIconSize(QSize(25, 25))
            button.setCheckable(True)

        xhs_btn.setChecked(True)

        self.layout().addWidget(self.platforms_frame)

        vline = QFrame()
        vline.setObjectName("vline")
        vline.setFrameShape(QFrame.VLine)
        vline.setFrameShadow(QFrame.Sunken)
        self.layout().addWidget(vline)
        #############################################################
        # right frame
        content_frame = QFrame()
        content_frame.setLayout(QVBoxLayout())
        content_frame.setObjectName("content_frame")
        content_frame.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout().addWidget(content_frame)

        content_frame.layout().addWidget(QLabel("平台设置"))

        hline1 = QFrame()
        hline1.setObjectName("hline")
        hline1.setFrameShape(QFrame.HLine)
        hline1.setFrameShadow(QFrame.Sunken)
        content_frame.layout().addWidget(hline1)

        common_frame = QFrame()
        common_frame.setLayout(QFormLayout())
        content_frame.layout().addWidget(common_frame)

        self.image_cover = AddImageCover()
        self.article_class = QLineEdit()
        self.article_class.setPlaceholderText("请设置")
        self.article_tag = QLineEdit()
        self.article_tag.setPlaceholderText("请设置, 以空格分开")

        common_frame.layout().addRow("设置封面", self.image_cover)
        common_frame.layout().addRow("设置分类", self.article_class)
        common_frame.layout().addRow("设置标签", self.article_tag)

        hline = QFrame()
        hline.setObjectName("hline")
        hline.setFrameShape(QFrame.HLine)
        hline.setFrameShadow(QFrame.Sunken)
        content_frame.layout().addWidget(hline)

        self.platform_stacks = QStackedLayout()
        content_frame.layout().addLayout(self.platform_stacks)

        self.xhs_set = ArticleXHS()
        self.zh_set = ArticleZH()
        self.wx_set = ArticleWX()
        self.bilibili_set = ArticleBiliBili()
        self.platform_stacks.addWidget(self.xhs_set)
        self.platform_stacks.addWidget(self.zh_set)
        self.platform_stacks.addWidget(self.wx_set)
        self.platform_stacks.addWidget(self.bilibili_set)

        common_frame.layout().setContentsMargins(0, 0, 0, 0)
        self.platforms_frame.layout().setContentsMargins(0, 10, 0, 0)
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)

    def addConnections(self):
        self.platforms_btns.idClicked.connect(self.handle_platform_setting)
        self.xhs_set.setting.connect(self.handle_update_setting)
        self.zh_set.setting.connect(self.handle_update_setting)
        self.wx_set.setting.connect(self.handle_update_setting)
        self.bilibili_set.setting.connect(self.handle_update_setting)

    @Slot(dict)
    def handle_update_setting(self, setting_data: dict):
        if "platform" not in setting_data:
            return
        if setting_data["platform"] not in self.setting:
            self.setting[setting_data["platform"]] = setting_data
        else:
            self.setting[setting_data["platform"]].update(setting_data)

    @Slot(int)
    def handle_platform_setting(self, idx: int):
        self.platform_stacks.setCurrentIndex(idx)

    def addStyle(self):
        self.setStyleSheet("""
        QLabel {
            color: #777;
            font-size: 13px;
        }
        QLineEdit {
            padding: 5px;
            border-radius: 5px;
            border: 1 solid #ccc;
            font-size: 13px;
            color: #777;
        }
        #platforms_frame QPushButton {
            background-color: transparent;
            border: none;
            font-size: 14px;
            border-radius: 0;
            padding: 5px;
            color: #555;
            text-align: center;
        }
        #platforms_frame QPushButton:checked{
            background-color: #F7F4EA;
            color: rgba(0, 0, 200, 100);
            border-left: 2 solid #ED474A;
        }
        #platforms_frame QLabel {
            font-weight: bold;
        }
        QPushButton {
            padding: 5px;
        }
        #scroll_area {
            border: none;
            background-color: transparent;
        }

        #hline {
            background-color: #eeeeee;
            border: none;
            max-height: 1px;
        }
        #vline {
            background-color: #eeeeee;
            border: none;
            max-width: 5px;
        }
        #container {
            background-color: transparent;
        }
        #content_frame QLabel {
            font-weight: bold
        }
        """)


class ShortNoteSetting(QWidget):

    def __init__(self, parent=None):
        super(ShortNoteSetting, self).__init__(parent)
        self.addComponents()
        self.addStyle()
        self.addConnections()

        self.setFixedWidth(300)

    def addComponents(self):
        self.setLayout(QHBoxLayout())

        #############################################################
        # left frame
        self.platforms_frame = QFrame()
        self.platforms_frame.setLayout(QVBoxLayout())
        self.platforms_frame.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

        self.platforms_frame.layout().addWidget(QLabel("平台"), 0,
                                                Qt.AlignmentFlag.AlignHCenter)
        self.platforms_frame.setObjectName("platforms_frame")
        self.platforms_frame.setMinimumWidth(30)

        self.platforms_btns = QButtonGroup()
        # xhs_btn = QPushButton()
        # xhs_btn.setIcon(QIcon("assets/icons/xhs.svg"))
        # self.platforms_btns.addButton(xhs_btn, 0)

        for button in self.platforms_btns.buttons():
            self.platforms_frame.layout().addWidget(button)
            button.setIconSize(QSize(25, 25))
            button.setCheckable(True)

        # xhs_btn.setChecked(True)

        self.layout().addWidget(self.platforms_frame)

        vline = QFrame()
        vline.setObjectName("vline")
        vline.setFrameShape(QFrame.VLine)
        vline.setFrameShadow(QFrame.Sunken)
        self.layout().addWidget(vline)
        #############################################################
        # right frame
        content_frame = QFrame()
        content_frame.setLayout(QVBoxLayout())
        content_frame.setObjectName("content_frame")
        content_frame.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout().addWidget(content_frame)

        content_frame.layout().addWidget(QLabel("平台设置"))

        hline1 = QFrame()
        hline1.setObjectName("hline")
        hline1.setFrameShape(QFrame.HLine)
        hline1.setFrameShadow(QFrame.Sunken)
        content_frame.layout().addWidget(hline1)

        common_frame = QFrame()
        common_frame.setLayout(QFormLayout())
        content_frame.layout().addWidget(common_frame)

        self.image_cover = AddImageCover()
        self.article_class = QLineEdit()
        self.article_class.setPlaceholderText("请设置")
        self.article_tag = QLineEdit()
        self.article_tag.setPlaceholderText("请设置")

        common_frame.layout().addRow("设置封面", self.image_cover)
        common_frame.layout().addRow("设置分类", self.article_class)
        common_frame.layout().addRow("设置标签", self.article_tag)

        hline = QFrame()
        hline.setObjectName("hline")
        hline.setFrameShape(QFrame.HLine)
        hline.setFrameShadow(QFrame.Sunken)
        content_frame.layout().addWidget(hline)

        self.platform_stacks = QStackedLayout()
        content_frame.layout().addLayout(self.platform_stacks)

        # self.platform_stacks.addWidget(ArticleXHS())

        common_frame.layout().setContentsMargins(0, 0, 0, 0)
        self.platforms_frame.layout().setContentsMargins(0, 10, 0, 0)
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)

    def addConnections(self):
        self.platforms_btns.idClicked.connect(self.handle_platform_setting)

    @Slot(int)
    def handle_platform_setting(self, idx: int):
        self.platform_stacks.setCurrentIndex(idx)

    def addStyle(self):
        self.setStyleSheet("""
        QLabel {
            color: #777;
            font-size: 13px;
        }
        QLineEdit {
            padding: 5px;
            border-radius: 5px;
            border: 1 solid #ccc;
            font-size: 13px;
            color: #777;
        }
        #platforms_frame QPushButton {
            background-color: transparent;
            border: none;
            font-size: 14px;
            border-radius: 0;
            padding: 5px;
            color: #555;
            text-align: center;
        }
        #platforms_frame QPushButton:checked{
            background-color: #F7F4EA;
            color: rgba(0, 0, 200, 100);
            border-left: 2 solid #ED474A;
        }
        #platforms_frame QLabel {
            font-weight: bold;
        }
        QPushButton {
            padding: 5px;
        }
        #scroll_area {
            border: none;
            background-color: transparent;
        }

        #hline {
            background-color: #eeeeee;
            border: none;
            max-height: 1px;
        }
        #vline {
            background-color: #eeeeee;
            border: none;
            max-width: 5px;
        }
        #container {
            background-color: transparent;
        }
        #content_frame QLabel {
            font-weight: bold
        }
        """)
