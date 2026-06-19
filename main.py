from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Signal Project")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("App is running"))
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())