from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel

app = QApplication([])

main_widget = QWidget()

# Create the main vertical layout
main_layout = QVBoxLayout()

# Add a QLabel to the main layout
main_layout.addWidget(QLabel("Main Layout Label"))

# Create and add a horizontal layout (nested_layout 1) with buttons to the main layout
nested_layout1 = QHBoxLayout()
nested_layout1.addWidget(QPushButton("Button 1"))
nested_layout1.addWidget(QPushButton("Button 2"))
main_layout.addLayout(nested_layout1)

# Add another QPushButton to the main layout
main_layout.addWidget(QPushButton("Main Layout Button"))

# Add another QLabel to the main layout
main_layout.addWidget(QLabel("Second Label Below Button"))

# Create another horizontal layout (nested_layout 2)
nested_layout2 = QHBoxLayout()
nested_layout2.addWidget(QPushButton("Button A"))
nested_layout2.addWidget(QPushButton("Button B"))

# Add the second horizontal layout to the main layout
main_layout.addLayout(nested_layout2)

# Set the main layout to the main widget
main_widget.setLayout(main_layout)
main_widget.show()

app.exec()
