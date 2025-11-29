import os
import subprocess
import tempfile
import json

from PySide6.QtCore import QFileInfo, QObject, QSize, Signal, Slot
from PySide6.QtGui import QIcon, QPixmap, Qt
from PySide6.QtWidgets import (
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
# from qasync import asyncSlot, asyncio

from components.addpublishaccounts import AddPublishAccounts, UseMemAccounts
from components.publishcontrol import PublishControl
from components.videosetting import VerticalVideoSetting, VideoSetting
from models.query import get_users_from_user_ids
from utils.constant import (
    LOGIN_METADATA,
    Platform,
    PublishType,
)


class FFmpegParse(QObject):
    result_status = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

    @Slot(str)
    def get_cover(self, command: str):
        process = subprocess.run(
            command,
            stdin=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        if process.returncode == 0:
            self.result_status.emit(True)
        else:
            self.result_status.emit(False)


class HorizonVideo(QWidget):
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
    #header_frame QLabel {
        color: #777;
        font-size: 13px;
    }
    #video_info_frame QPushButton {
        background-color: #C8E8F9;
        padding: 7 12;
        font-size: 12px;
        color: #2165bf;
        border: none;
        border-radius: 7px;
        text-align: center;
    }
    #video_info_frame QPushButton:hover {
        background-color: #7EC9F1;
    }
    #video_info_frame QLabel {
        color: #777;
    }
    #editor_frame QLineEdit {
        border: 1 solid #ccc;
        color: #777;
        padding: 5px;
        font-size: 13px;
        border-radius: 7px;
    } 
    #editor_frame QLabel {
        max-height: 30px;
        min-width: 50px;
        color: #777;
        font-size: 14px;
    } 
    #editor_frame QTextEdit {
        border: 1 solid #ccc;
        font-size: 13px;
        color: #777;
        padding: 5px;
        border-radius: 7px;
    } 
    #setting_frame {
        background-color: #fff;
    }
    """

    publish_data = Signal(list)
    ffmpeg_command = Signal(str)

    def __init__(self, vertical: bool = False, parent=None):
        super(HorizonVideo, self).__init__(parent)
        self._vertical = vertical
        self._last_user_ids = None
        self._selected_user_ids = None
        self._video_path = None
        self._file_name = None
        self.addComponents()
        self.addStyle()
        self.addWorkers()
        self.addConnections()
        self.afterInit()

        temp_handle, self.temp_file = tempfile.mkstemp(suffix=".jpg")
        os.close(temp_handle)

        self.video_info_frame.setVisible(False)

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

        if self._vertical:
            self.setting = VerticalVideoSetting()
        else:
            self.setting = VideoSetting()
        setting_frame.layout().addWidget(self.setting)

        header_frame = QFrame()
        header_frame.setLayout(QHBoxLayout())
        header_frame.setObjectName("header_frame")

        self.create_frame = QFrame()
        self.create_frame.setLayout(QHBoxLayout())
        self.create_frame.layout().setAlignment(Qt.AlignmentFlag.AlignLeft)
        header_frame.layout().addWidget(
            self.create_frame, 0, Qt.AlignmentFlag.AlignLeft
        )

        self.create_btn = QPushButton("添加视频")
        self.help_info = QLabel("支持mp4 mov mkv 格式")

        self.create_btn.setIcon(QIcon("assets/file-plus.svg"))
        self.create_btn.setIconSize(QSize(20, 20))

        self.create_frame.layout().addWidget(self.create_btn)
        self.create_frame.layout().addWidget(self.help_info)

        self.video_info_frame = QFrame()
        self.video_info_frame.setObjectName("video_info_frame")
        self.video_info_frame.setLayout(QVBoxLayout())
        self.video_info = QLabel("视频信息")
        self.video_info_frame.layout().addWidget(self.video_info)
        self.video_cover = QLabel()
        self.video_cover.setFixedSize(200, 100)
        self.video_info_frame.layout().addWidget(self.video_cover)

        reload_layout = QHBoxLayout()
        self.video_info_frame.layout().addLayout(reload_layout)
        self.reload_btn = QPushButton("重新添加")
        self.clear_btn = QPushButton("清空视频")
        reload_layout.addWidget(self.reload_btn)
        reload_layout.addStretch()
        reload_layout.addWidget(self.clear_btn)

        content_frame.layout().addWidget(header_frame)
        content_frame.layout().addWidget(self.video_info_frame)

        #############################################################
        # editor_frame
        editor_frame = QFrame()
        editor_frame.setLayout(QVBoxLayout())
        editor_frame.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        editor_frame.setObjectName("editor_frame")

        video_title_layout = QHBoxLayout()
        self.video_title = QLineEdit()
        self.video_title.setPlaceholderText("标题(5-30)")
        self.video_title_count = QLabel("0/30")
        video_title_layout.addWidget(self.video_title)
        video_title_layout.addWidget(self.video_title_count)

        video_introduction_layout = QHBoxLayout()
        self.video_introduction = QTextEdit()
        self.video_introduction.setMaximumHeight(100)
        self.video_introduction.setPlaceholderText(
            "填入视频简介，可以加入标签， 标签以#开头"
        )
        self.video_introduction_count = QLabel("0/200")
        video_introduction_layout.addWidget(self.video_introduction)
        video_introduction_layout.addWidget(self.video_introduction_count)

        editor_frame.layout().addWidget(QLabel("标题"))
        editor_frame.layout().addLayout(video_title_layout)
        editor_frame.layout().addWidget(QLabel("视频简介"))
        editor_frame.layout().addLayout(video_introduction_layout)

        video_title_layout.setContentsMargins(0, 0, 0, 0)
        video_introduction_layout.setContentsMargins(0, 0, 0, 0)
        content_frame.layout().addWidget(editor_frame)
        # content_frame.layout().addItem(
        #     QSpacerItem(10, 50, QSizePolicy.Fixed, QSizePolicy.Expanding))
        #############################################################
        self.publish_control = PublishControl()
        center_frame.layout().addWidget(self.publish_control)

        #############################################################
        # set margin and spacing
        self.video_info_frame.layout().setContentsMargins(0, 0, 0, 0)
        center_frame.layout().setContentsMargins(0, 0, 0, 0)
        setting_frame.layout().setContentsMargins(0, 0, 0, 0)
        editor_frame.layout().setContentsMargins(0, 0, 0, 0)
        self.create_frame.layout().setContentsMargins(0, 0, 0, 0)
        header_frame.layout().setContentsMargins(5, 10, 0, 10)
        header_frame.layout().setSpacing(20)
        content_frame.layout().setContentsMargins(10, 0, 10, 0)
        self.layout().setContentsMargins(10, 8, 10, 10)

    def addStyle(self):
        self.setStyleSheet(self.Style)

    def addWorkers(self):
        self.ffmpeg_parser = FFmpegParse()
        # self.ffmpeg_thread = QThread()
        # self.ffmpeg_parser.moveToThread(self.ffmpeg_thread)

    def addConnections(self):
        self.publish_control.publish_btn.clicked.connect(self.handle_publishing)

        self.publish_control.mem_btn.clicked.connect(self.handle_men_accounts)
        self.create_btn.clicked.connect(self.handle_import_video)
        self.reload_btn.clicked.connect(self.handle_import_video)
        self.clear_btn.clicked.connect(self.handle_clear)

        self.ffmpeg_command.connect(self.ffmpeg_parser.get_cover)
        self.ffmpeg_parser.result_status.connect(self.handle_video_cover)

        self.video_title.textEdited.connect(self.handle_video_title)
        self.video_introduction.textChanged.connect(self.handle_video_introduction)

    @Slot(str)
    def handle_video_title(self, text: str):
        self.video_title_count.setText(f"{len(text)}/30")

    @Slot()
    def handle_video_introduction(self):
        count = len(self.video_introduction.toPlainText())
        self.video_introduction_count.setText(f"{count}/200")

    @Slot()
    def handle_clear(self):
        self.video_info_frame.setVisible(False)
        self.create_frame.setVisible(True)
        self._video_path = None

    @Slot()
    def handle_video_cover(self):
        # handle the cover and
        self.video_info_frame.setVisible(True)
        self.create_frame.setVisible(False)

        pixmap = QPixmap(self.temp_file)
        scaled_pixmap = pixmap.scaled(
            self.video_cover.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.video_info.setText(self._file_name)
        self.video_cover.setPixmap(scaled_pixmap)

    @Slot()
    def handle_publishing(self):
        if self._video_path is None:
            QMessageBox.warning(self, "上传视频", "缺少视频!")
            return
        title = self.video_title.text().strip()
        if len(title) == 0:
            QMessageBox.warning(self, "缺少标题", "缺少标题!")
            return
        content = self.video_introduction.toPlainText()
        if len(content) == 0:
            QMessageBox.warning(self, "缺少文字内容", "缺少文字内容!")
            return

        image_cover = self.setting.image_cover.image_cover.get_image_cover()
        if image_cover is None:
            image_cover = self.temp_file

        if self._selected_user_ids is None:
            add_accounts = AddPublishAccounts(PublishType.HorizonVideo)
            if add_accounts.exec() == QDialog.Accepted:
                user_ids = add_accounts.added_user_ids
            else:
                return
        else:
            user_ids = self._selected_user_ids
        video_class = self.setting.article_class.text().strip()
        video_tags = self.setting.article_tag.text().strip()
        all_settings = self.setting.setting
        users = get_users_from_user_ids(user_ids)
        for user in users:
            user["video_path"] = self._video_path
            user["publish_type"] = PublishType.HorizonVideo
            user["image_cover"] = image_cover
            platform, _ = Platform.from_value(user["platform"])
            if "publish_url_video" in LOGIN_METADATA[platform]:
                user["publish_url"] = LOGIN_METADATA[platform]["publish_url_video"]

            user["platform"] = platform  # transform to Platform
            user["title"] = title
            user["content"] = content

            if platform in all_settings:
                user["setting"] = all_settings[platform]
            if len(video_class) == 0:
                user["video_class"] = video_class
            if len(video_tags) == 0:
                user["video_tags"] = video_tags
        process_users = [
            user for user in users if "publish_url" in user and user["is_active"] == 1
        ]

        self._last_user_ids = list(user_ids)
        self.save_last_user_ids()

        self.publish_data.emit(process_users)

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

    @Slot()
    def handle_import_video(self):
        video_formats = "Video Files (*.mp4 *.mkv *.mov)"
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Video File", "", video_formats
        )
        if file_path:
            self._file_name = os.path.basename(file_path)
            self._video_path = file_path
            command = f'.\\ffmpeg.exe  -i "{file_path}" -vframes 1 -f image2 -y "{self.temp_file}"'
            self.ffmpeg_command.emit(command)

    def afterInit(self):
        pass
        # self.ffmpeg_thread.start()

    # @asyncSlot()
    # async def close_thread(self):
    #     print("closing thread")
    #     self.ffmpeg_parser.deleteLater()
    #     self.ffmpeg_thread.quit()
    #     self.ffmpeg_thread.wait()
    #     self.ffmpeg_thread.deleteLater()
    #     print(self.ffmpeg_thread)
    # loop = asyncio.get_event_loop()
    # loop.call_soon(self._clean_up)

    def _clean_up(self):
        print("clean up")

    def save_last_user_ids(self):
        with open("last_users_h_video.json", "w") as file:
            json.dump(self._last_user_ids, file)

    def load_last_user_ids(self):
        file_path = "last_users_h_video.json"
        file_info = QFileInfo(file_path)
        if not file_info.exists():
            return
        with open(file_path, "r") as file:
            self._last_user_ids = json.load(file)
