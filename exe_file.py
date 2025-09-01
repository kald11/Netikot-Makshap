import sys
import subprocess
import pkg_resources

# Install packages from requirements.txt
requirements_file = 'requirements.txt'


def install_requirements(requirements_file):
    try:
        with open(requirements_file) as f:
            required_packages = f.read().splitlines()
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', *required_packages])
    except FileNotFoundError:
        print(f"Requirements file '{requirements_file}' not found.")


install_requirements(requirements_file)

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit
from PyQt6.QtCore import Qt


class ScriptRunner(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_window()
        self.create_widgets()
        self.setup_layout()
        self.connect_signals()

    def setup_window(self):
        self.setWindowTitle("Script Runner")
        self.setGeometry(100, 100, 500, 300)

    def create_widgets(self):
        self.header = QLabel("קובץ הרצה עבור גדוד 372 וית״ד")
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("הזן מספר אתר בטבלה")
        self.run_first_btn = QPushButton("הרצה אתר בודד")
        self.run_second_btn = QPushButton("הרצת כל האתרים")

    def setup_layout(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 10)
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.run_first_btn)
        input_layout.addWidget(self.input_field)

        main_layout.addWidget(self.header)
        main_layout.addSpacing(10)
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.run_second_btn)

    def connect_signals(self):
        self.run_first_btn.clicked.connect(self.run_first_script)
        self.run_second_btn.clicked.connect(self.run_second_script)

    def run_first_script(self):
        index = self.input_field.text()
        subprocess.run(["python", "script1.py", index]) if index.isdigit() else self.header.setText("הזן מספר תקין!")

    def run_second_script(self):
        subprocess.run(["python", "main.py"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScriptRunner()
    window.show()
    sys.exit(app.exec())
