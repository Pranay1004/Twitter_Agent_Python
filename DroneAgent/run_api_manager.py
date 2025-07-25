import sys
from PyQt5.QtWidgets import QApplication
from gui_api_manager import APIManagerWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = APIManagerWindow()
    window.show()
    sys.exit(app.exec_())
