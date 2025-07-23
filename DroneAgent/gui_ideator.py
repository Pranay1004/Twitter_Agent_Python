"""
Drone Thread Ideator GUI
Allows users to generate and preview drone-related Twitter threads using ContentIdeator
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QLineEdit, QSpinBox, QScrollArea, QGroupBox
)
from PyQt5.QtCore import Qt
from DroneAgent.agent.ideator import ContentIdeator

class IdeatorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drone Thread Ideator")
        self.setGeometry(200, 200, 900, 700)
        self.ideator = ContentIdeator()
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Theme input
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Thread Theme:")
        self.theme_input = QLineEdit()
        self.theme_input.setPlaceholderText("e.g. The Art of Drone Cinematography: Pro Tips")
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_input)
        layout.addLayout(theme_layout)

        # Tweet count input
        count_layout = QHBoxLayout()
        count_label = QLabel("Number of Tweets:")
        self.count_input = QSpinBox()
        self.count_input.setRange(3, 20)
        self.count_input.setValue(10)
        count_layout.addWidget(count_label)
        count_layout.addWidget(self.count_input)
        layout.addLayout(count_layout)

        # Generate button
        self.generate_btn = QPushButton("Generate Thread")
        self.generate_btn.clicked.connect(self.generate_thread)
        layout.addWidget(self.generate_btn)

        # Thread preview area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.thread_widget = QWidget()
        self.thread_layout = QVBoxLayout(self.thread_widget)
        self.scroll_area.setWidget(self.thread_widget)
        layout.addWidget(self.scroll_area)

        self.setCentralWidget(central_widget)

    def generate_thread(self):
        theme = self.theme_input.text().strip()
        tweet_count = self.count_input.value()
        if not theme:
            self.show_status("Please enter a thread theme.")
            return
        thread_data = self.ideator.generate_thread_content(theme, tweet_count)
        self.display_thread(thread_data)

    def display_thread(self, thread_data):
        # Clear previous content
        for i in reversed(range(self.thread_layout.count())):
            widget = self.thread_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        # Show theme
        theme_label = QLabel(f"<b>Theme:</b> {thread_data.get('theme', '')}")
        theme_label.setStyleSheet("font-size: 16px; margin-bottom: 10px;")
        self.thread_layout.addWidget(theme_label)
        # Show each tweet
        for tweet in thread_data.get('tweets', []):
            group = QGroupBox(f"Tweet #{tweet['number']}")
            vbox = QVBoxLayout(group)
            tweet_text = QLabel(tweet['content'])
            tweet_text.setWordWrap(True)
            tweet_text.setStyleSheet("background-color: #f5f5f5; padding: 8px; border-radius: 4px;")
            vbox.addWidget(tweet_text)
            info = QLabel(f"Chars: {tweet['character_count']} | Needs Image: {tweet['needs_image']}")
            info.setStyleSheet("color: #888; font-size: 11px;")
            vbox.addWidget(info)
            self.thread_layout.addWidget(group)

    def show_status(self, message):
        status = QLabel(message)
        status.setStyleSheet("color: red; font-weight: bold; margin: 10px;")
        self.thread_layout.addWidget(status)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IdeatorGUI()
    window.show()
    sys.exit(app.exec_())
