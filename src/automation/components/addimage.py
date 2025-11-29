from PySide6.QtCore import QSize, Slot
from PySide6.QtGui import QIcon, QPixmap, Qt
from PySide6.QtWidgets import QButtonGroup, QFileDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QRadioButton, QVBoxLayout, QWidget


class ImageWidget(QWidget):

    def __init__(self, parent=None):
        super(ImageWidget, self).__init__(parent)

        self._image_path = None

        self.setLayout(QVBoxLayout())
        self.image_label = QLabel()
        self.image_label.setFixedSize(180, 100)
        self.layout().addWidget(self.image_label)

        control_frame = QFrame()
        control_frame.setLayout(QHBoxLayout())
        control_frame.layout().setAlignment(Qt.AlignmentFlag.AlignHCenter)
        control_frame.setObjectName("control_frame")
        self.layout().addWidget(control_frame)

        self.setimage_btn = QPushButton()
        self.removeimage_btn = QPushButton()

        self.setimage_btn.setIcon(QIcon("assets/image.svg"))
        self.removeimage_btn.setIcon(QIcon("assets/trash.svg"))

        self.setimage_btn.setIconSize(QSize(20, 20))
        self.removeimage_btn.setIconSize(QSize(20, 20))

        control_frame.layout().addWidget(self.setimage_btn)
        control_frame.layout().addWidget(self.removeimage_btn)

        self.setimage_btn.clicked.connect(self.handle_set_image)
        self.removeimage_btn.clicked.connect(self.handle_remove_image)

        control_frame.layout().setContentsMargins(0, 2, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        self.setStyleSheet("""
            QPushButton {
                padding: 2px;
                border: none;
                background-color: transparent;
                text-align: center;
            }
            QLabel {
                border: 1 solid #ccc;
                border-radius: 5px;
            }
        """)

    def handle_set_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "Images (*.png *.xpm *.jpg *.bmp)")
        if file_path:
            self._image_path = file_path
            pixmap = QPixmap(file_path)
            self.image_label.setPixmap(
                pixmap.scaled(150, 80,
                              Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                              Qt.TransformationMode.SmoothTransformation))

    def handle_remove_image(self):
        self._image_path = None
        self.image_label.clear()

    def get_image_cover(self):
        return self._image_path


class AddImageCover(QWidget):

    Style = """
    QRadioButton {
        color: #777;
        font-size: 13px;
    }
    """

    def __init__(self, parent=None):
        super(AddImageCover, self).__init__(parent)

        self.setLayout(QVBoxLayout())

        select_frame = QFrame()
        content_frame = QFrame()
        select_frame.setLayout(QHBoxLayout())
        content_frame.setLayout(QHBoxLayout())

        self.layout().addWidget(select_frame)
        self.layout().addWidget(content_frame)

        self.auto_radio = QRadioButton("自动")
        self.image_radio = QRadioButton("图片")

        self.switch_btns = QButtonGroup()
        self.switch_btns.addButton(self.auto_radio, 0)
        self.switch_btns.addButton(self.image_radio, 1)

        select_frame.layout().addWidget(self.auto_radio)
        select_frame.layout().addWidget(self.image_radio)

        self.auto_radio.setChecked(True)

        self.label = QLabel("确保编辑中有图片")
        content_frame.layout().addWidget(self.label, 0,
                                         Qt.AlignmentFlag.AlignVCenter)
        self.image_cover = ImageWidget()
        self.image_cover.setVisible(False)
        content_frame.layout().addWidget(self.image_cover, 0,
                                         Qt.AlignmentFlag.AlignVCenter)

        self.switch_btns.idClicked.connect(self.handle_switch)

        select_frame.layout().setContentsMargins(0, 0, 0, 0)
        content_frame.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setContentsMargins(0, 5, 0, 0)

        self.setStyleSheet(self.Style)

    @Slot(int)
    def handle_switch(self, idx):
        if idx == 0:
            self.label.setVisible(True)
            self.image_cover.setVisible(False)
        else:
            self.label.setVisible(False)
            self.image_cover.setVisible(True)

    @Slot(int)
    def handle_image_count_from_context(self, image_count: int):
        if image_count > 0:
            self.label.setText(f"编辑器中有{image_count}张图片")
        else:
            self.label.setText("确保编辑中有图片")
