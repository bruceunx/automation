from enum import Enum
from PySide6.QtCore import QDate, QSize, Qt, Slot
from PySide6.QtGui import QIcon, QTextDocument
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QRadioButton,
    QStyleOptionViewItem,
    QStyledItemDelegate,
    QVBoxLayout,
    QWidget,
)


class PaymentAgreementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("服务条款")
        self.addComponents()

    def addComponents(self):
        layout = QVBoxLayout()

        payment_label = QLabel("服务协议")
        payment_label.setStyleSheet("font-weight: bold; color: #333;")
        layout.addWidget(payment_label)

        agreement_text = QLabel(
            "我同意以下条款：\n"
            "1. 付款不可退还\n"
            "2. 我已查看所有细节\n"
            "3. 我理解服务条款"
        )
        agreement_text.setWordWrap(True)
        layout.addWidget(agreement_text)

        button_layout = QHBoxLayout()

        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)

        confirm_button = QPushButton("同意协议")
        confirm_button.clicked.connect(self.accept)

        button_layout.addWidget(cancel_button)
        button_layout.addWidget(confirm_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)


class PriceVersion(Enum):
    Month = 0
    Year = 1

    @property
    def verbose(self) -> str:
        return ("月付", "年付")[self.value]

    @property
    def days(self) -> int:
        return (30, 360)[self.value]


class PriceTagButton(QPushButton):
    def __init__(self, price_version: PriceVersion, price: int, parent=None):
        super(PriceTagButton, self).__init__(parent)
        self.setFixedSize(120, 90)
        layout = QVBoxLayout()
        title = QLabel(price_version.verbose)
        title.setObjectName("price_title")
        layout.addWidget(title, 0, Qt.AlignmentFlag.AlignHCenter)

        price_layout = QHBoxLayout()
        price_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        price_layout.setSpacing(0)
        layout.addLayout(price_layout)

        currency_tag = QLabel("¥")
        currency_tag.setObjectName("currency_tag")
        price_tag = QLabel(str(price))
        price_tag.setObjectName("price_tag")

        price_layout.addWidget(currency_tag, 0, Qt.AlignmentFlag.AlignBottom)
        price_layout.addWidget(price_tag)

        detail_layout = QHBoxLayout()
        detail_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addLayout(detail_layout)
        detail_label = QLabel(f"折合¥{price/price_version.days:.2f}/人/天")
        detail_label.setObjectName("detail_label")
        detail_layout.addWidget(detail_label)

        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)
        self.setStyleSheet("""
        #price_title {
            font-size: 14pt;
            font-weight: bold;
            color: #555;
        }
        #currency_tag {
            font-size: 7pt;
            font-weight: bold;
            text-align: center;
            color: red;
        }
        #price_tag {
            font-size: 16pt;
            font-weight: bold;
            text-align: center;
            color: red;
        }
        #detail_label {
            font-size: 6pt;
            text-align: center;
            color: #777;
        }
        """)


class HTMLDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        return None

    def paint(self, painter, option, index):
        options = option
        self.initStyleOption(options, index)

        options.text = index.data(Qt.DisplayRole)
        options.textElideMode = Qt.ElideNone
        options.features |= QStyleOptionViewItem.HasDisplay

        doc = QTextDocument()
        doc.setHtml(options.text)
        doc.setTextWidth(options.rect.width())

        painter.save()
        painter.translate(options.rect.topLeft())
        doc.drawContents(painter)
        painter.restore()


class VersionType(Enum):
    FreeType = 0
    Personal = 1
    Group = 2
    Full = 3

    @property
    def verbose(self) -> str:
        return ("免费版", "个人版", "团队版", "全能版")[self.value]

    @property
    def subtitle(self) -> str:
        return ("", "适合个人使用", "适合2-100人团队使用", "适合100人以上公司使用")[
            self.value
        ]

    @property
    def background_color(self) -> str:
        return ("#fff", "#b4dee4", "#feefdd", "#201e1f")[self.value]

    @property
    def color(self) -> str:
        return ("#333", "#333", "#333", "#ffcc85")[self.value]

    @property
    def month_price(self) -> str:
        return ("0", "48", "88", "988")[self.value]

    @property
    def year_price(self) -> str:
        return ("0", "198", "498", "4988")[self.value]

    @property
    def btn_color(self) -> str:
        return ("#777", "#fff", "#feefdd", "#201e1f")[self.value]

    @property
    def btn_background_color(self) -> str:
        return ("#fff", "#668bb7", "#201e1f", "#feefdd")[self.value]

    @property
    def user_num(self) -> str:
        return ("1", "5", "100", "无限")[self.value]

    @property
    def support_stat(self) -> bool:
        return self != VersionType.FreeType

    @property
    def rights(self) -> tuple[str, ...]:
        return (
            ("", ""),
            ("成员席位数1-2人", "媒体账号支持管理>10", "数据统计"),
            ("成员席位数3-100人", "媒体账号支持管理>50", "数据统计"),
            ("成员席位数>100人", "媒体账号支持管理不限", "数据统计"),
        )[self.value]

    @property
    def support_num(self) -> tuple[int, ...]:
        return ((1, 1), (1, 2), (3, 5, 20, 100), (100, 200, 500))[self.value]

    @property
    def prices(self) -> tuple[int, ...]:
        return ((0, 0), (48, 198), (88, 498), (988, 4988))[self.value]


# buy dialog
class PurchaseDialog(QDialog):
    def __init__(self, version_type: VersionType, parent=None):
        super(PurchaseDialog, self).__init__(parent)
        self.setFixedSize(600, 500)
        self.setWindowTitle("购买会员")
        self.setWindowIcon(QIcon("assets/award.svg"))
        self.version_type = version_type
        self.addComponents()
        self.addStyle()
        self.addConnections()

    def addComponents(self):
        self.setLayout(QHBoxLayout())
        left_frame = QFrame()
        left_frame.setObjectName("left_frame")
        right_frame = QFrame()
        right_frame.setObjectName("right_frame")
        self.layout().addWidget(left_frame)
        self.layout().addWidget(right_frame)

        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        member_icon = QLabel()
        member_icon.setPixmap(QIcon("assets/award.svg").pixmap(27, 27))
        left_layout.addWidget(member_icon, 0, Qt.AlignmentFlag.AlignHCenter)

        title_layout = QHBoxLayout()
        title_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        left_layout.addLayout(title_layout)
        title_layout.addWidget(QLabel(self.version_type.verbose))
        title_layout.addWidget(QLabel("专属权益"))
        title_layout.setSpacing(2)
        title_layout.setContentsMargins(0, 5, 0, 30)

        list_widget = QListWidget()
        list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        delegate = HTMLDelegate(list_widget)
        list_widget.setItemDelegate(delegate)
        list_widget.setSpacing(10)
        for right in self.version_type.rights:
            item = QListWidgetItem(
                f"<div style='color: #777;'><span style='color: #F6E3A2;'>•</span> {right}</div>"
            )
            list_widget.addItem(item)

        left_layout.addWidget(list_widget)

        left_layout.setContentsMargins(0, 20, 0, 30)
        left_frame.setLayout(left_layout)
        left_frame.setFixedWidth(200)

        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        user_num_layout = QHBoxLayout()
        user_num_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        right_layout.addLayout(user_num_layout)
        user_num_layout.addWidget(QLabel("席位数: "))

        self.support_nums_btton_group = QButtonGroup()
        for num in self.version_type.support_num:
            btn = QPushButton(str(num))
            btn.setFixedWidth(30)
            user_num_layout.addWidget(btn)
            self.support_nums_btton_group.addButton(btn, num)
            btn.setCheckable(True)

        self.support_nums_btton_group.button(
            self.version_type.support_num[0]
        ).setChecked(True)

        supoort_account = QHBoxLayout()
        supoort_account.setAlignment(Qt.AlignmentFlag.AlignLeft)
        supoort_account.addWidget(QLabel("媒体账号: "))

        self.account_num_label = QLabel("10")
        supoort_account.addWidget(self.account_num_label)
        right_layout.addLayout(supoort_account)

        price_layout = QHBoxLayout()
        price_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        right_layout.addLayout(price_layout)

        self.priceversion_button_groups = QButtonGroup()
        _month_price, _year_price = self.version_type.prices
        self.month_price = PriceTagButton(PriceVersion.Month, _month_price)
        self.year_price = PriceTagButton(PriceVersion.Year, _year_price)
        price_layout.addWidget(self.month_price)
        price_layout.addWidget(self.year_price)
        price_layout.setContentsMargins(0, 20, 0, 20)
        price_layout.setSpacing(30)

        self.month_price.setCheckable(True)
        self.year_price.setCheckable(True)
        self.priceversion_button_groups.addButton(self.month_price, 0)
        self.priceversion_button_groups.addButton(self.year_price, 1)

        self.month_price.setChecked(True)

        expire_layout = QHBoxLayout()
        right_layout.addLayout(expire_layout)
        expire_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        expire_layout.addWidget(QLabel("购买后到期时间:"))

        self.expire_date = QLabel(
            QDate.currentDate().addMonths(1).toString("yyyy/MM/dd")
        )

        expire_layout.addWidget(self.expire_date)

        payment_layout = QHBoxLayout()
        right_layout.addLayout(payment_layout)
        payment_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        payment_layout.addWidget(QLabel("支付方式: "))
        self.alipay = QRadioButton()
        self.alipay.setIcon(QIcon("assets/icons/alipay.svg"))
        self.alipay.setIconSize(QSize(80, 50))

        self.weipay = QRadioButton()
        self.weipay.setIcon(QIcon("assets/icons/weipay.svg"))
        self.weipay.setIconSize(QSize(80, 20))

        payment_layout.addWidget(self.alipay)
        payment_layout.addWidget(self.weipay)

        self.alipay.setChecked(True)

        payment_price_layout = QHBoxLayout()
        right_layout.addLayout(payment_price_layout)
        payment_price_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        payment_price_layout.addWidget(QLabel("应付金额:   "))

        currency_tag = QLabel("¥")
        currency_tag.setObjectName("currency_tag")
        payment_price_layout.addWidget(currency_tag, 0, Qt.AlignmentFlag.AlignBottom)

        self.price_label = QLabel(str(_month_price))
        self.price_label.setObjectName("price_label")
        payment_price_layout.addWidget(
            self.price_label, 0, Qt.AlignmentFlag.AlignBottom
        )
        payment_price_layout.setSpacing(0)

        confirm_layout = QHBoxLayout()
        right_layout.addLayout(confirm_layout)
        confirm_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.confirm_check = QCheckBox("同意")

        confirm_layout.addWidget(self.confirm_check)

        self.policy_btn = QPushButton("<<购买服务协议>>")
        self.policy_btn.setObjectName("policy_btn")
        confirm_layout.addWidget(self.policy_btn)
        confirm_layout.addSpacing(10)
        self.confirm_btn = QPushButton("提交订单")
        self.confirm_btn.setObjectName("confirm_btn")

        confirm_layout.addWidget(self.confirm_btn)

        right_frame.setLayout(right_layout)
        right_layout.setSpacing(15)

    def addConnections(self):
        self.support_nums_btton_group.idClicked.connect(self.handle_spport_nums)
        self.priceversion_button_groups.idClicked.connect(self.handle_priceversion)
        self.policy_btn.clicked.connect(self.handle_policy)

    @Slot(int)
    def handle_priceversion(self, idx: int):
        price = self.version_type.prices[idx]
        self.price_label.setText(str(price))

    @Slot(int)
    def handle_spport_nums(self, num: int):
        pass

    @Slot()
    def handle_policy(self):
        policy_dialog = PaymentAgreementDialog()
        if policy_dialog.exec() == QDialog.Accepted:
            self.confirm_check.setChecked(True)
        else:
            self.confirm_check.setChecked(False)

    def addStyle(self):
        self.setStyleSheet("""
        QListWidget {
            background-color: transparent;
            border: none;
            padding: 5px;
        }
        #left_frame {
            background-color: #ddcede;
        }
        #right_frame {
            background-color: #fff;
        }
        #right_frame QPushButton {
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 5px;
        }
        #right_frame QPushButton:checked {
            border: 1px solid #9A6C9D;
        }
        #currency_tag {
            font-size: 9pt;
            font-weight: bold;
            text-align: center;
            color: red;
        }
        #price_label {
            font-size: 16pt;
            font-weight: bold;
            text-align: center;
            color: red;
        }
        #right_frame #policy_btn {
            background-color: none;
            border: none;
            color: #9A6C9D;
        }
        #right_frame #confirm_btn:hover {
            border: 1px solid #9A6C9D;
        }
        """)


class PriceBoard(QWidget):
    def __init__(self, version_type: VersionType, parent=None):
        super(PriceBoard, self).__init__(parent)
        self.version_type = version_type
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("PriceBoard")
        self.setMinimumSize(220, 500)

        self.setLayout(QVBoxLayout())

        top_frame = QFrame()
        top_frame.setStyleSheet(f"""
        QFrame {{
            background-color: {version_type.background_color};
            border-top-left-radius: 20px;
            border-top-right-radius: 20px;
        }}
        #board_title{{
            font-size: 15pt;
            font-weight: bold;
            text-align: center;
            color: {version_type.color};
        }}
        #currency_tag {{
            font-size: 7pt;
            font-weight: bold;
            text-align: center;
            color: {version_type.color};
        }}
        #price_tag {{
            font-size: 15pt;
            font-weight: bold;
            text-align: center;
            color: {version_type.color};
        }}

        QPushButton {{
            border: none;
            border-radius: 10px;
            font-size: 10pt;
            width: 100px;
            padding: 5px;
            background-color: {version_type.btn_background_color};
            color: {version_type.btn_color};
        }}
        """)

        self.layout().addWidget(top_frame)

        layout = QVBoxLayout()
        top_frame.setLayout(layout)

        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        title = QLabel(version_type.verbose)
        title.setObjectName("board_title")
        layout.addWidget(title, 0, Qt.AlignmentFlag.AlignHCenter)

        subtitle = QLabel(version_type.subtitle)
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle, 0, Qt.AlignmentFlag.AlignHCenter)

        price_layout = QHBoxLayout()
        price_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addLayout(price_layout)

        currency_tag = QLabel("¥")
        currency_tag.setObjectName("currency_tag")
        price_layout.addWidget(currency_tag, 0, Qt.AlignmentFlag.AlignBottom)
        if version_type == VersionType.FreeType:
            price_tag = QLabel("0")
            price_tag.setObjectName("price_tag")
            price_layout.addWidget(price_tag)

            self.buy_btn = QPushButton("永久免费")
            self.buy_btn.setDisabled(True)
        else:
            month_price_tag = QLabel(version_type.month_price)
            month_price_tag.setObjectName("price_tag")
            price_layout.addWidget(month_price_tag)

            month_suffix = QLabel("/月  ")
            month_suffix.setObjectName("currency_tag")
            price_layout.addWidget(month_suffix, 0, Qt.AlignmentFlag.AlignBottom)

            year_currency_tag = QLabel("¥")
            year_currency_tag.setObjectName("currency_tag")
            price_layout.addWidget(year_currency_tag, 0, Qt.AlignmentFlag.AlignBottom)

            year_price_tag = QLabel(version_type.year_price)
            year_price_tag.setObjectName("price_tag")
            price_layout.addWidget(year_price_tag)

            year_suffix = QLabel("/年")
            year_suffix.setObjectName("currency_tag")
            price_layout.addWidget(year_suffix, 0, Qt.AlignmentFlag.AlignBottom)

            self.buy_btn = QPushButton("立即购买")

        price_layout.setSpacing(0)
        price_layout.setContentsMargins(0, 30, 0, 30)

        layout.addWidget(self.buy_btn)

        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        info_layout.setContentsMargins(20, 0, 20, 0)
        self.layout().addLayout(info_layout)  # type: ignore

        # add detail
        detail_layout1 = QHBoxLayout()
        info_layout.addLayout(detail_layout1)
        detail_layout1.addWidget(QLabel("支持用户数"), 0, Qt.AlignmentFlag.AlignLeft)
        detail_layout1.addWidget(
            QLabel(version_type.user_num), 0, Qt.AlignmentFlag.AlignRight
        )

        detail_layout2 = QHBoxLayout()
        info_layout.addLayout(detail_layout2)
        detail_layout2.addWidget(QLabel("数据统计"), 0, Qt.AlignmentFlag.AlignLeft)
        state_label = QLabel()
        if version_type.support_stat:
            state_label.setPixmap(QIcon("assets/check.svg").pixmap(10, 10))
        else:
            state_label.setPixmap(QIcon("assets/x-member.svg").pixmap(10, 10))

        detail_layout2.addWidget(state_label, 0, Qt.AlignmentFlag.AlignRight)

        detail_layout3 = QHBoxLayout()
        info_layout.addLayout(detail_layout3)
        detail_layout3.addWidget(QLabel("其他"), 0, Qt.AlignmentFlag.AlignLeft)
        state_label1 = QLabel()
        if version_type.support_stat:
            state_label1.setPixmap(QIcon("assets/check.svg").pixmap(10, 10))
        else:
            state_label1.setPixmap(QIcon("assets/x-member.svg").pixmap(10, 10))

        detail_layout3.addWidget(state_label1, 0, Qt.AlignmentFlag.AlignRight)

        layout.setContentsMargins(5, 20, 5, 5)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.addStyle()

        self.buy_btn.clicked.connect(self.handle_buy_membership)

    @Slot()
    def handle_buy_membership(self):
        purchase_dialog = PurchaseDialog(self.version_type)
        purchase_dialog.exec()

    def addStyle(self):
        self.setStyleSheet("""
        #PriceBoard {
            background-color: #fff;
            border-radius: 20px;
        }
        QLabel {
            font-size: 8pt;
            color: #777;
        }
        """)


class MemeberCenter(QWidget):
    def __init__(self, parent=None):
        super(MemeberCenter, self).__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("Content")

        layout = QVBoxLayout()

        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        title = QLabel("引流平台")
        title.setObjectName("title")
        subtitle = QLabel("助力效率运营")
        subtitle.setObjectName("subtitle")
        layout.addWidget(title, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(subtitle, 0, Qt.AlignmentFlag.AlignHCenter)

        content_layout = QHBoxLayout()
        layout.addLayout(content_layout)

        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        content_layout.addWidget(PriceBoard(VersionType.FreeType))
        content_layout.addWidget(PriceBoard(VersionType.Personal))
        content_layout.addWidget(PriceBoard(VersionType.Group))
        content_layout.addWidget(PriceBoard(VersionType.Full))

        content_layout.setSpacing(40)
        self.setLayout(layout)
        self.addStyle()

    def addStyle(self):
        self.setStyleSheet("""
            #Content {
                border-radius: 12px;
                background-color: qlineargradient( x1:0, y1:0, x2:0, y2:1, stop:0 #ccc, stop:0.2 #eee, stop:0.4 #fff, stop:1 #fff);
            }
            #title {
                font-size: 27pt;
                font-weight: bold;
                font-style: italic;
                text-align: center;
                color: #333;
            }
            #subtitle {
                font-size: 8pt;
                font-weight: bold;
                color: #777;
                text-align: center;
            }
        """)
