import sys
from PyQt5.QtWidgets import QApplication
from gui_ideator import IdeatorWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IdeatorWindow()
    window.show()
    sys.exit(app.exec_())
