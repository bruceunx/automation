from PySide6.QtCore import Slot
from PySide6.QtWidgets import QHBoxLayout, QMessageBox, QStackedWidget, QWidget

from components.horizonvideo import HorizonVideo
from components.leftbar import LeftBar, LeftBarType
from components.publishhistory import PublishHistory
from components.article import Article
from components.shortnote import ShortNote
from models.query import insert_records
from workers.publishworker import PublishWorker


class PublisView(QWidget):
    def __init__(self, parent=None):
        super(PublisView, self).__init__(parent)
        self.addComponents()
        self.addStyle()
        self.addWorkers()
        self.addConnections()

    def addComponents(self):
        self.setLayout(QHBoxLayout())
        self.menu_bar = LeftBar.create_leftbar(LeftBarType.PublishLeftBar)
        self.layout().addWidget(self.menu_bar)

        self.stack = QStackedWidget()
        self.layout().addWidget(self.stack)

        self.article = Article()
        self.horizontal_video = HorizonVideo()
        self.stack.addWidget(self.article)
        self.stack.addWidget(self.horizontal_video)
        self.stack.addWidget(HorizonVideo(vertical=True))
        self.stack.addWidget(ShortNote())
        self.stack.addWidget(PublishHistory())
        self.stack.setCurrentIndex(0)

        self.layout().setSpacing(0)
        self.layout().setContentsMargins(10, 10, 5, 10)

    def addWorkers(self):
        self.publish_worker = PublishWorker()

    def addConnections(self):
        self.menu_bar.btn_groups.idClicked.connect(self.handle_stach_change)

        self.article.publish_data.connect(self.publish_worker.handle_publish)
        self.horizontal_video.publish_data.connect(self.publish_worker.handle_publish)

        self.publish_worker.task_completed.connect(self.handle_results)

    @Slot(int)
    def handle_stach_change(self, idx: int):
        self.stack.setCurrentIndex(idx)

    def addStyle(self):
        self.setStyleSheet("""
            QLabel {
                color: #333;
            }
        """)

    @Slot(list)
    def handle_results(self, results: list):
        insert_records(results)
        total = len(results)
        success = 0
        failed = 0
        for result in results:
            if result["status"] == 1:
                success += 1
            else:
                failed += 1
        QMessageBox.information(
            self, "上传结束", f"{success}/{total}成功\n{failed}/{total}失败"
        )

    def closeEvent(self, event):
        event.accept()
