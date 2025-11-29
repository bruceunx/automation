import sys
from PySide6.QtWidgets import QApplication, QStyledItemDelegate, QTableView, QWidget, QVBoxLayout, QLineEdit
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex


class CustomWidgetDelegate(QStyledItemDelegate):

    def createEditor(self, parent, option, index):
        # Create the custom widget (e.g., QLineEdit)
        editor = QLineEdit(parent)
        editor.setStyleSheet("""
            QLineEdit {
                background-color: red;
                border: 2 solid red;
            }
        """)
        return editor

    def setEditorData(self, editor, index):
        # Set the data from the model into the editor
        value = index.model().data(index, Qt.EditRole)
        editor.setText(value)

    def setModelData(self, editor, model, index):
        # Get the data from the editor and set it in the model
        value = editor.text()
        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        # Set the editor's size and location based on the view options
        editor.setGeometry(option.rect)


class CustomTableModel(QAbstractTableModel):

    def __init__(self, data, headers, parent=None):
        super().__init__(parent)
        self._data = data
        self._headers = headers

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self._data[index.row()][index.column()]
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [role])
            return True
        return False

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable


class TableViewWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.tableView = QTableView(self)
        self.layout.addWidget(self.tableView)

        # Sample data and headers
        data = [
            ['Item 1-1', 'Item 1-2'],
            ['Item 2-1', 'Item 2-2'],
            ['Item 3-1', 'Item 3-2'],
            ['Item 4-1', 'Item 4-2'],
            ['Item 5-1', 'Item 5-2'],
        ]
        headers = ['Column 1', 'Column 2']

        # Create custom table model
        self.model = CustomTableModel(data, headers)
        self.tableView.setModel(self.model)

        # Set custom delegate for the first column
        self.tableView.setItemDelegateForColumn(
            0, CustomWidgetDelegate(self.tableView))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    table_view_widget = TableViewWidget()
    table_view_widget.show()

    sys.exit(app.exec())
