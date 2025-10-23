from PySide6.QtWidgets import QApplication
from src.pdfcomparator import *
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFComparator()
    window.show()
    sys.exit(app.exec())
    # End of main.py
