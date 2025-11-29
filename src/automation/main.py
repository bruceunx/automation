import asyncio
import sys

from PySide6.QtCore import QSharedMemory
from PySide6.QtWidgets import QApplication
from qasync import QEventLoop

from models.db import connect_to_database, create_table

# from utils.temp import add_all_users
# from .models.query import test_add_employees
from views.mainview import MainView


class SingleInstanceApp(QApplication):
    def __init__(self, *args, key):
        super().__init__(*args)
        self.shared_memory = QSharedMemory(key)

        if not self.shared_memory.create(1):
            print("Another instance is already running.")
            sys.exit()


async def _main():
    app = SingleInstanceApp(
        sys.argv, key="automation_74e70c5a-cf39-438d-9219-6fcdfb16322d"
    )
    app.setStyle("Fusion")  # type: ignore

    if not connect_to_database("test.db"):
        sys.exit(1)
    create_table()

    # add_all_users()
    # test_add_employees()
    #########################################
    # add login dialog

    # login_w = LoginDialog()
    # if login_w.exec() != QDialog.Accepted:
    #     sys.exit(1)

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainView()
    window.show()

    with loop:
        loop.run_forever()

    # sys.exit(app.exec())


def main():
    asyncio.run(_main())


if __name__ == "__main__":
    main()
