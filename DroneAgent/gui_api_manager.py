import os
from PyQt5 import QtWidgets, QtCore
from dotenv import load_dotenv

ENV_PATH = os.path.join(os.path.dirname(__file__), '..', '.env')

class ApiManager(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('API Key Manager')
        self.setGeometry(100, 100, 400, 300)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.info_label = QtWidgets.QLabel('Add or update API keys for your apps. Keys will be saved to .env.')
        self.layout.addWidget(self.info_label)

        self.form_layout = QtWidgets.QFormLayout()
        self.key_name_input = QtWidgets.QLineEdit()
        self.key_value_input = QtWidgets.QLineEdit()
        self.form_layout.addRow('API Key Name:', self.key_name_input)
        self.form_layout.addRow('API Key Value:', self.key_value_input)
        self.layout.addLayout(self.form_layout)

        self.save_button = QtWidgets.QPushButton('Save to .env')
        self.save_button.clicked.connect(self.save_key)
        self.layout.addWidget(self.save_button)

        self.status_label = QtWidgets.QLabel('')
        self.layout.addWidget(self.status_label)

    def save_key(self):
        key = self.key_name_input.text().strip()
        value = self.key_value_input.text().strip()
        if not key or not value:
            self.status_label.setText('Key name and value cannot be empty.')
            return
        # Read existing .env
        if os.path.exists(ENV_PATH):
            with open(ENV_PATH, 'r') as f:
                lines = f.readlines()
        else:
            lines = []
        # Update or add key
        updated = False
        for i, line in enumerate(lines):
            if line.startswith(f'{key}='):
                lines[i] = f'{key}={value}\n'
                updated = True
                break
        if not updated:
            lines.append(f'{key}={value}\n')
        with open(ENV_PATH, 'w') as f:
            f.writelines(lines)
        self.status_label.setText(f'Saved {key} to .env.')

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = ApiManager()
    win.show()
    app.exec_()
