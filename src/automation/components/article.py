import os
import json
import shutil
import re
import tempfile

from PySide6.QtCore import QFileInfo, QPoint, QSize, Signal, Slot
from PySide6.QtGui import QFont, QIcon, QImage, QTextCharFormat, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import pypandoc

from components.addpublishaccounts import (
    AddPublishAccounts,
    PublishType,
    UseMemAccounts,
)
from components.articlesetting import ArticleSetting
from components.publishcontrol import PublishControl
from models.query import get_users_from_user_ids
from utils.constant import LOGIN_METADATA, Platform


class HeadLine(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QHBoxLayout())
        self.head_input = QLineEdit()
        self.head_input.setPlaceholderText("请输入标题")
        self.head_label = QLabel("0/30")
        self.head_label.setFixedWidth(50)

        self.layout().addWidget(self.head_input)
        self.layout().addWidget(self.head_label)

        self.head_input.textChanged.connect(self.update_word_count)

        self.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: none;
                background-color: transparent;
                font-size: 20px;
                color: #555;
            }
            QLabel {
                background-color: transparent;
                color: #999;
                font-size: 13px;
            }
        """)

        self.layout().setContentsMargins(0, 0, 0, 0)

    def update_word_count(self):
        text = self.head_input.text()
        word_count = len(text)
        self.head_label.setText(f"{word_count}/30")
        if word_count > 30:
            self.head_label.setStyleSheet("""
             color: red;
            """)
        else:
            self.head_label.setStyleSheet("""
             color: #999;
            """)


class EditorWidget(QWidget):
    Style = """
    QPushButton {
        background-color: transparent;
        border: none;
    }
    QComboBox {
        color: #333;
    }
    QComboBox QAbstractItemView {
        background-color: #fff;
        color: #333;
        border: 1 solid #e0e0e0;
        selection-background-color: #e0e0e0;
        outline: 0;
        border-radius: 0;
        border-top: none;
    }
    """

    def __init__(self, parent=None):
        super(EditorWidget, self).__init__(parent)
        self.setLayout(QHBoxLayout())

        self.font_size_btn = QPushButton()
        self.font_bold_btn = QPushButton()
        self.underline_btn = QPushButton()
        self.italic_btn = QPushButton()
        self.image_btn = QPushButton()
        self.space_btn = QPushButton()

        self.font_size_btn.setIcon(QIcon("assets/heading.svg"))
        self.font_bold_btn.setIcon(QIcon("assets/bold.svg"))
        self.underline_btn.setIcon(QIcon("assets/underline.svg"))
        self.italic_btn.setIcon(QIcon("assets/italic.svg"))
        self.image_btn.setIcon(QIcon("assets/image.svg"))
        self.space_btn.setIcon(QIcon("assets/type.svg"))

        self.font_size_btn.setIconSize(QSize(20, 20))
        self.font_bold_btn.setIconSize(QSize(20, 20))
        self.underline_btn.setIconSize(QSize(20, 20))
        self.italic_btn.setIconSize(QSize(20, 20))
        self.image_btn.setIconSize(QSize(20, 20))
        self.space_btn.setIconSize(QSize(20, 20))

        self.layout().addWidget(self.font_size_btn)
        self.layout().addWidget(self.font_bold_btn)
        self.layout().addWidget(self.underline_btn)
        self.layout().addWidget(self.italic_btn)
        self.layout().addWidget(self.image_btn)
        self.layout().addWidget(self.space_btn)

        self.layout().setSpacing(2)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(self.Style)

        self.font_size_btn.clicked.connect(self.show_heading_menu)
        self.heading_combo = QComboBox(self)
        self.heading_combo.setVisible(False)
        self.heading_combo.addItems(["H1", "H2", "H3", "paragraph"])
        # self.heading_combo.currentIndexChanged.connect(self.set_heading)

    def show_heading_menu(self):
        pos = self.font_size_btn.mapToParent(QPoint(0, self.font_size_btn.height()))
        self.heading_combo.move(pos)
        self.heading_combo.showPopup()


class Article(QWidget):
    Style = """
    #content_frame {
        background-color: #fff;
        border-top-left-radius: 20px;
        border-top-right-radius: 20px;
    }
    #header_frame QPushButton {
        background-color: #2165bf;
        padding: 7 12;
        font-size: 14px;
        color: #fff;
        border: none;
        border-radius: 10px;
        text-align: center;
    }
    #header_frame QPushButton:hover {
        background-color: #1a4d8f;
    }
    #header_frame QPushButton:pressed {
        background-color: #143b6f;
    }
    #hline,#hline1 {
        background-color: #eeeeee;
        border: none;
        max-height: 1px;
    }
    QTextEdit {
        border: none;
        background-color: transparent;
        color: #555;
        border-bottom-left-radius: 10px;
        border-bottom-right-radius: 10px;
    }
    QTextEdit QScrollBar:vertical {
        border: none;
        background: white;
        width: 10px;
        margin: 0px 0px 0px 0px;
    }

    QTextEdit QScrollBar::handle:vertical {
        background: #ccc;
        border-radius: 3px;
        min-height: 20px;
    }

    QTextEdit QScrollBar::add-line:vertical, QTextEdit QScrollBar::sub-line:vertical {
        height: 0px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }

    QTextEdit QScrollBar::up-arrow:vertical, QTextEdit QScrollBar::down-arrow:vertical {
        height: 0px;
    }

    QTextEdit QScrollBar::add-page:vertical, QTextEdit QScrollBar::sub-page:vertical {
        background: none;
    }

    QTextEdit QScrollBar:horizontal {
        border: none;
        background: white;
        height: 10px;
        margin: 0px 0px 0px 0px;
    }

    QTextEdit QScrollBar::handle:horizontal {
        background: #ccc;
        border-radius: 3px;
        min-width: 20px;
    }

    QTextEdit QScrollBar::add-line:horizontal, QTextEdit QScrollBar::sub-line:horizontal {
        width: 0px;
        subcontrol-position: right;
        subcontrol-origin: margin;
    }

    QTextEdit QScrollBar::left-arrow:horizontal, QTextEdit QScrollBar::right-arrow:horizontal {
        width: 0px;
    }

    QTextEdit QScrollBar::add-page:horizontal, QTextEdit QScrollBar::sub-page:horizontal {
        background: none;
    }

    #setting_frame {
        background-color: #fff;
    }
    """
    image_count = Signal(int)
    publish_data = Signal(list)

    def __init__(self, parent=None):
        super(Article, self).__init__(parent)
        self._last_user_ids = None
        self._selected_user_ids = None
        self.images = []
        self.addComponents()
        self.addStyle()
        self.addConnections()

        self.load_last_user_ids()

    def addComponents(self):
        self.setLayout(QHBoxLayout())

        center_frame = QFrame()
        center_frame.setLayout(QVBoxLayout())
        self.layout().addWidget(center_frame)

        content_frame = QFrame()
        content_frame.setLayout(QVBoxLayout())
        content_frame.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        content_frame.setObjectName("content_frame")
        center_frame.layout().addWidget(content_frame)

        setting_frame = QFrame()
        setting_frame.setFixedWidth(300)
        setting_frame.setObjectName("setting_frame")
        setting_frame.setLayout(QVBoxLayout())
        self.layout().addWidget(setting_frame)

        self.setting = ArticleSetting()
        setting_frame.layout().addWidget(self.setting)

        header_frame = QFrame()
        header_frame.setLayout(QHBoxLayout())
        header_frame.setObjectName("header_frame")

        create_frame = QFrame()
        create_frame.setLayout(QHBoxLayout())
        create_frame.layout().setAlignment(Qt.AlignmentFlag.AlignLeft)
        header_frame.layout().addWidget(create_frame, 0, Qt.AlignmentFlag.AlignLeft)

        self.create_btn = QPushButton("新建图文")
        self.import_btn = QPushButton("导入word")

        self.create_btn.setIcon(QIcon("assets/file-plus.svg"))
        self.import_btn.setIcon(QIcon("assets/external-link.svg"))

        self.create_btn.setIconSize(QSize(20, 20))
        self.import_btn.setIconSize(QSize(20, 20))

        create_frame.layout().addWidget(self.create_btn)
        create_frame.layout().addWidget(self.import_btn)

        editor_frame = QFrame()
        editor_frame.setLayout(QHBoxLayout())
        header_frame.layout().addWidget(editor_frame)
        header_frame.layout().addWidget(QLabel())

        self.edit_widget = EditorWidget()
        editor_frame.layout().addWidget(
            self.edit_widget, 0, Qt.AlignmentFlag.AlignCenter
        )
        content_frame.layout().addWidget(header_frame)

        hline = QFrame()
        hline.setObjectName("hline")
        hline.setFrameShape(QFrame.HLine)
        hline.setFrameShadow(QFrame.Sunken)
        content_frame.layout().addWidget(hline)

        self.head_input = HeadLine()
        content_frame.layout().addWidget(self.head_input)

        hline1 = QFrame()
        hline1.setObjectName("hline1")
        hline1.setFrameShape(QFrame.HLine)
        hline1.setFrameShadow(QFrame.Sunken)
        content_frame.layout().addWidget(hline1)

        self.body_content = QTextEdit()
        content_frame.layout().addWidget(self.body_content)

        self.body_content.setPlaceholderText("编辑内容")

        self.publish_control = PublishControl()
        center_frame.layout().addWidget(self.publish_control)

        center_frame.layout().setContentsMargins(0, 0, 0, 0)
        setting_frame.layout().setContentsMargins(0, 0, 0, 0)
        editor_frame.layout().setContentsMargins(0, 0, 0, 0)
        create_frame.layout().setContentsMargins(0, 0, 0, 0)
        header_frame.layout().setContentsMargins(5, 10, 0, 10)
        header_frame.layout().setSpacing(20)
        content_frame.layout().setContentsMargins(10, 0, 10, 0)
        self.layout().setContentsMargins(10, 8, 10, 10)

    def addStyle(self):
        self.setStyleSheet(self.Style)

    def addConnections(self):
        self.edit_widget.heading_combo.currentIndexChanged.connect(self.set_heading)
        self.edit_widget.font_bold_btn.clicked.connect(self.toggle_bold)
        self.edit_widget.italic_btn.clicked.connect(self.toggle_italic)
        self.edit_widget.image_btn.clicked.connect(self.insert_image)
        self.edit_widget.underline_btn.clicked.connect(self.toggle_underline)

        self.create_btn.clicked.connect(self.new_article)
        self.import_btn.clicked.connect(self.handle_import_file)

        # self.body_content.textChanged.connect(self.handle_text_change)

        self.image_count.connect(
            self.setting.image_cover.handle_image_count_from_context
        )

        self.publish_control.publish_btn.clicked.connect(self.handle_publishing)

        self.publish_control.mem_btn.clicked.connect(self.handle_men_accounts)

    @Slot(int)
    def set_heading(self, index: int):
        cursor = self.body_content.textCursor()
        format = QTextCharFormat()
        font = QFont()
        if index == 3:
            font.setPointSize(12)
            font.setBold(False)
        elif index == 0:  # H1
            font.setPointSize(24)
            font.setBold(True)
        elif index == 1:  # H2
            font.setPointSize(18)
            font.setBold(True)
        elif index == 2:  # H3
            font.setPointSize(14)
            font.setBold(True)

        format.setFont(font)
        cursor.mergeCharFormat(format)

    def toggle_bold(self):
        if self.body_content.fontWeight() == QFont.Weight.Bold:
            self.body_content.setFontWeight(QFont.Weight.Normal)
        else:
            self.body_content.setFontWeight(QFont.Weight.Bold)

    def toggle_italic(self):
        self.body_content.setFontItalic(not self.body_content.fontItalic())

    def toggle_underline(self):
        self.body_content.setFontUnderline(not self.body_content.fontUnderline())

    def insert_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "Images (*.png *.xpm *.jpg *.bmp)"
        )
        if file_path:
            image = QImage(file_path)
            if not image.isNull():
                cursor = self.body_content.textCursor()
                cursor.insertImage(image)
            self.images.append(file_path)
            self.image_count.emit(len(self.images))

    def save_document(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存文档", "", " Files (*.docx)"
        )

        if file_path:
            if not file_path.endswith(".docx"):
                file_path += ".docx"

            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".rtf"
            ) as temp_rtf_file:
                self.body_content.document().save(temp_rtf_file.name, "RTF")

                pypandoc.convert_file(temp_rtf_file.name, "docx", outputfile=file_path)

    def new_article(self):
        # save old file?
        self.head_input.head_input.clear()
        self.body_content.clear()
        self.image_count.emit(0)
        self.images = []

    def handle_import_file(self):
        cache_dir = "cache_images"
        os.makedirs(cache_dir, exist_ok=True)
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文档", "", "docx (*.docx)"
        )
        if file_path:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".html"
            ) as temp_html_file:
                pypandoc.convert_file(
                    file_path,
                    "html",
                    outputfile=temp_html_file.name,
                    extra_args=[f"--extract-media={cache_dir}"],
                )

                with open(temp_html_file.name, "r", encoding="utf-8") as html_file:
                    html_content = html_file.read()

                html_content, images = self.adjust_image_paths(html_content, ".")
                self.body_content.setHtml(html_content)
                self.images = images
                self.image_count.emit(len(self.images))

    def adjust_image_paths(self, html_content, cache_dir):
        pattern = re.compile(r'<img src="(.*?)"')

        images = []

        def repl(match):
            relative_path = match.group(1)
            absolute_path = os.path.abspath(os.path.join(cache_dir, relative_path))
            images.append(absolute_path)
            return f'<img src="{absolute_path}"'

        return pattern.sub(repl, html_content), images

    def is_empty(self) -> bool:
        return (
            self.body_content.toPlainText().strip() == ""
            and "<img" not in self.body_content.toHtml().lower()
        )

    def save_to_docx(self):
        if self.is_empty:
            return
        html_content = self.body_content.toHtml()
        with tempfile.TemporaryDirectory() as temp_dir:
            html_content = self.adjust_image_paths_from_html(html_content, temp_dir)
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".html", dir=temp_dir
            ) as temp_html:
                temp_html.write(html_content.encode("utf-8"))
                temp_html_path = temp_html.name

                temp_docx = tempfile.NamedTemporaryFile(
                    delete=False, suffix=".docx", dir=temp_dir
                )
                temp_docx_path = temp_docx.name
                temp_docx.close()

                pypandoc.convert_file(
                    temp_html_path, "docx", format="html", outputfile=temp_docx_path
                )
        return temp_docx_path

    def adjust_image_paths_from_html(self, html_content, temp_dir):
        pattern = re.compile(r'<img src="(.*?)"')

        def repl(match):
            relative_path = match.group(1)
            if relative_path.startswith("file://"):
                file_path = relative_path[7:]
                file_name = os.path.basename(file_path)
                temp_image_path = os.path.join(temp_dir, file_name)
                shutil.copy(file_path, temp_image_path)
                return f'<img src="{temp_image_path}"'
            return match.group(0)

        return pattern.sub(repl, html_content)

    @Slot()
    def handle_publishing(self):
        # check content
        title = self.head_input.head_input.text().strip()
        if len(title) == 0:
            QMessageBox.warning(self, "缺少标题", "缺少标题!")
            return
        if self.is_empty():
            QMessageBox.warning(self, "缺少内容", "缺少内容!")
            return
        content = self.body_content.toPlainText()
        if len(content) == 0:
            QMessageBox.warning(self, "缺少文字内容", "缺少文字内容!")
            return
        image_cover = self.setting.image_cover.image_cover.get_image_cover()
        if image_cover is None:
            if len(self.images) == 0:
                QMessageBox.warning(self, "缺少图片", "缺少图片!")
                return
            else:
                image_cover = self.images[0]
        if self._selected_user_ids is None:
            add_accounts = AddPublishAccounts(PublishType.Article)
            if add_accounts.exec() == QDialog.Accepted:
                user_ids = add_accounts.added_user_ids
            else:
                return
        else:
            user_ids = self._selected_user_ids
        docx_path = self.save_to_docx()
        # check image cover
        image_class = self.setting.article_class.text().strip()
        image_tags = self.setting.article_tag.text().strip()
        all_settings = self.setting.setting
        users = get_users_from_user_ids(user_ids)
        for user in users:
            user["publish_type"] = PublishType.Article
            user["image_cover"] = image_cover
            platform, _ = Platform.from_value(user["platform"])
            if "publish_url_image" in LOGIN_METADATA[platform]:
                user["publish_url"] = LOGIN_METADATA[platform]["publish_url_image"]
            user["platform"] = platform  # transform to Platform
            user["title"] = title
            user["content"] = content
            if len(self.images) > 1 and platform == Platform.XHS:
                user["images"] = self.images
            if docx_path is not None and platform == Platform.WX:
                user["docx_path"] = docx_path
            if platform in all_settings:
                user["setting"] = all_settings[platform]
            if len(image_class) == 0:
                user["image_class"] = image_class
            if len(image_tags) == 0:
                user["image_tags"] = image_tags

        process_users = [
            user for user in users if "publish_url" in user and user["is_active"] == 1
        ]

        self._last_user_ids = list(user_ids)
        self.save_last_user_ids()
        # image_cover, title, content, image_class, image_tags, setting, user_ids
        # return
        self.publish_data.emit(process_users)

    def save_last_user_ids(self):
        with open("last_users_article.json", "w") as file:
            json.dump(self._last_user_ids, file)

    def load_last_user_ids(self):
        file_path = "last_users_article.json"
        file_info = QFileInfo(file_path)
        if not file_info.exists():
            return
        with open(file_path, "r") as file:
            self._last_user_ids = json.load(file)

    @Slot()
    def handle_men_accounts(self):
        if self._last_user_ids is None:
            QMessageBox.warning(self, "没有记忆", "没有记忆数据!")
            return

        # check all users from user_ids
        users = get_users_from_user_ids(self._last_user_ids)
        group_users_w = UseMemAccounts(users)
        if group_users_w.exec_() == QDialog.Accepted:
            self._selected_user_ids = group_users_w.added_user_ids

    @Slot()
    def handle_clear_men(self):
        self._selected_user_ids = None
