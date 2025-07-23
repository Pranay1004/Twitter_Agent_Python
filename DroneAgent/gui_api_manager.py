import os
from PyQt5 import QtWidgets, QtCore
from dotenv import load_dotenv

ENV_PATH = os.path.join(os.path.dirname(__file__), '..', '.env')



class ApiManager(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('API Key Manager')
        self.setGeometry(100, 100, 500, 400)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.info_label = QtWidgets.QLabel('Add or update API keys for your apps. Keys will be saved to .env.\nUse uppercase and underscores, ending with _API_KEY. Add a comment to describe the API (optional).')
        self.layout.addWidget(self.info_label)

        self.form_layout = QtWidgets.QFormLayout()
        self.key_name_input = QtWidgets.QLineEdit()
        self.key_name_input.setPlaceholderText('E.g. GEMINI_API_KEY, OPENROUTER_API_KEY')
        self.key_value_input = QtWidgets.QLineEdit()
        self.key_value_input.setPlaceholderText('Paste your API key here')
        self.comment_input = QtWidgets.QLineEdit()
        self.comment_input.setPlaceholderText('Optional: Describe what this API does')
        self.form_layout.addRow('API Key Name:', self.key_name_input)
        self.form_layout.addRow('API Key Value:', self.key_value_input)
        self.form_layout.addRow('Comment (optional):', self.comment_input)
        self.layout.addLayout(self.form_layout)

        self.save_button = QtWidgets.QPushButton('Save to .env')
        self.save_button.clicked.connect(self.save_key)
        self.layout.addWidget(self.save_button)

        self.status_label = QtWidgets.QLabel('')
        self.layout.addWidget(self.status_label)

        # API status section
        self.status_group = QtWidgets.QGroupBox('API Status')
        self.status_layout = QtWidgets.QVBoxLayout()
        self.status_group.setLayout(self.status_layout)
        self.layout.addWidget(self.status_group)
        self.update_api_status()

    def update_api_status(self):
        self.status_layout.setParent(None)
        self.status_layout = QtWidgets.QVBoxLayout()
        self.status_group.setLayout(self.status_layout)
        apis = [
            ('GEMINI_API_KEY', 'Gemini'),
            ('PERPLEXITY_API_KEY', 'Perplexity'),
            ('OPENROUTER_API_KEY', 'OpenRouter'),
            ('UNSPLASH_ACCESS_KEY', 'Unsplash'),
            ('PEXELS_API_KEY', 'Pexels'),
            ('BITLY_ACCESS_TOKEN', 'Bitly'),
            ('STABILITY_API_KEY', 'Stability AI'),
        ]
        if os.path.exists(ENV_PATH):
            with open(ENV_PATH, 'r') as f:
                env_lines = f.readlines()
            env_dict = {}
            for line in env_lines:
                if '=' in line and not line.strip().startswith('#'):
                    k, v = line.strip().split('=', 1)
                    env_dict[k] = v
        else:
            env_dict = {}
        for key, label in apis:
            status = '✅' if key in env_dict and env_dict[key] else '❌'
            self.status_layout.addWidget(QtWidgets.QLabel(f'{label}: {status}'))

    def save_key(self):
        key = self.key_name_input.text().strip().upper()
        value = self.key_value_input.text().strip()
        comment = self.comment_input.text().strip()
        if not key or not value:
            self.status_label.setText('Key name and value cannot be empty.')
            return
        if not key.endswith('_API_KEY') and 'TOKEN' not in key and 'SECRET' not in key:
            self.status_label.setText('Key name should end with _API_KEY, _TOKEN, or _SECRET.')
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
                if comment:
                    # Insert or update comment above key
                    if i > 0 and lines[i-1].startswith('#'):
                        lines[i-1] = f'# {comment}\n'
                    else:
                        lines.insert(i, f'# {comment}\n')
                lines[i] = f'{key}={value}\n'
                updated = True
                break
        if not updated:
            if comment:
                lines.append(f'# {comment}\n')
            lines.append(f'{key}={value}\n')
        with open(ENV_PATH, 'w') as f:
            f.writelines(lines)
        self.status_label.setText(f'Saved {key} to .env.')

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = ApiManager()
    win.show()
    app.exec_()
