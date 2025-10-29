from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QFileDialog, QFrame, QSizePolicy
)
from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtCore import Qt, QRect, Signal, QTimer, QPropertyAnimation, QEasingCurve

from ui.ui_mainwindow import Ui_MainWindow  # the generated file
from src.pdfworker import *  # your PDF comparison logic
from src.pdfviewer import *
from collections import defaultdict



class PDFComparator(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # load the UI from Qt Designer

        self.setWindowTitle("PDF Comparator")
        self.resize(1600, 900)
        
        
        self.left_pdf_viewer = PDFViewer()
        self.right_pdf_viewer = PDFViewer()
        
        self.pdfworker = PDFWorker()
        
        self.compared = False
        
        # Add them into the placeholders defined in your UI
        left_layout = QVBoxLayout(self.left_viewer)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(self.left_pdf_viewer)

        right_layout = QVBoxLayout(self.right_viewer)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(self.right_pdf_viewer)

        # =====================

        # Connect buttons (names must match your Qt Designer object names)
        self.left_load_file.clicked.connect(self.load_left_pdf)
        self.right_load_file.clicked.connect(self.load_right_pdf)
        self.pushButton_5.clicked.connect(self.compare_pdfs)

        # State
        self.left_pdf_path = None
        self.right_pdf_path = None
        
        self.prev_button.clicked.connect(self.prev_diff)
        self.next_button.clicked.connect(self.next_diff)      
        
        self.differences = []  # Will hold the differences after comparison  
        
        self.c_method_comboBox.currentIndexChanged.connect(self.change_compare_method)
        self.c_method_comboBox.clear()
        self.c_method_comboBox.addItems([
            "Myers Diff (Default)",
            "DeepDiff",
            "SequenceMatcher",
            "Hirschberg",
        ])
        self.c_method_comboBox.setCurrentIndex(0)
        self.c_method_comboBox.setToolTip("Select comparison method")
        
        # assuming rightScrollArea is your QScrollArea from .ui
        self.diff_scroll = self.changes_viewer  # rename for clarity if needed

        # 1️⃣ Create a QWidget to hold the layout
        self.diff_container = QWidget()
        self.diff_container.setObjectName("diff_container")

        # 2️⃣ Create the layout that will hold all diff cards
        self.diff_layout = QVBoxLayout(self.diff_container)
        self.diff_layout.setAlignment(Qt.AlignTop)
        self.diff_layout.setContentsMargins(10, 10, 10, 10)
        self.diff_layout.setSpacing(8)

        # 3️⃣ Attach the container to the scroll area
        self.diff_scroll.setWidget(self.diff_container)
        self.diff_scroll.setWidgetResizable(True)
        
    def change_compare_method(self, index):
        methods = self.pdfworker._allCompareMethods
        if 0 <= index < len(methods):
            self.pdfworker._selectedCompareMethod = methods[index]
        else:
            self.pdfworker._selectedCompareMethod = None

    def load_left_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Left PDF", "", "PDF Files (*.pdf)")
        if path:
            self.left_pdf_path = path
            self.left_pdf_viewer.load_pdf(path)
            self.pdfworker.LoadPDF_Left(path)
            self.compared = False

    def load_right_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Right PDF", "", "PDF Files (*.pdf)")
        if path:
            self.right_pdf_path = path
            self.right_pdf_viewer.load_pdf(path)
            self.pdfworker.LoadPDF_Right(path)
            self.compared = False
            
    def populate_diff_view(self):
        # Clear old items
        for i in reversed(range(self.diff_layout.count())):
            widget = self.diff_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if not getattr(self, "differences", None):
            return

        # Group by page number
        grouped = defaultdict(list)
        for page, bbox, text, change_type in self.differences:
            grouped[page].append((bbox, text, change_type))

        # Sort by page number
        for page in sorted(grouped.keys()):
            # --- Create page section ---
            page_frame = QFrame()
            page_frame.setFrameShape(QFrame.StyledPanel)
            page_frame.setStyleSheet("""
                QFrame {
                    background-color: #f7f7f7;
                    border: 1px solid #ccc;
                    border-radius: 1px;
                }
            """)
            
            page_frame.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)

            page_layout = QVBoxLayout(page_frame)
            page_layout.setContentsMargins(6, 6, 6, 6)
            page_layout.setSpacing(6)

            # --- Page title ---
            title = QLabel(f"<h4> Page {page + 1}</h4>")
            title.setAlignment(Qt.AlignLeft)
            page_layout.addWidget(title)

            # --- Each change for that page ---
            for bbox, text, change_type in grouped[page]:

                diff_frame = ClickableFrame()
                diff_frame.setFrameShape(QFrame.StyledPanel)
                # make the right diff window slightly smaller
                diff_frame.setFixedWidth(260)
                
                if change_type == "added":
                    diff_frame.setStyleSheet(f"""
                        QFrame {{
                            background-color: #e6ffe6;
                            border: 1px solid #00cc00;
                            border-radius: 5px; }}
                    """)
                else:
                    diff_frame.setStyleSheet(f"""
                        QFrame {{
                            background-color: #ffe6e6;
                            border: 1px solid #cc0000;
                            border-radius: 5px; }}
                    """)
                    
                diff_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

                if change_type == "added":
                    diff_frame.clicked.connect(lambda p=page, b=bbox: self.right_pdf_viewer.smooth_scroll_to_bbox(p, b))
                else:
                    diff_frame.clicked.connect(lambda p=page, b=bbox: self.left_pdf_viewer.smooth_scroll_to_bbox(p, b))
                    
                    
                diff_layout = QVBoxLayout(diff_frame)
                diff_layout.setContentsMargins(3, 2, 3, 2)
                diff_layout.setSpacing(2)


                title_label = QLabel(f"<b>{change_type.capitalize()}</b>")
                text_label = QLabel(text[:300] + ("..." if len(text) > 300 else ""))
                text_label.setWordWrap(True)
                text_label.setStyleSheet(f"""
                        QFrame {{
                            border: none;
                             }}
                    """)

                diff_layout.addWidget(title_label)
                diff_layout.addWidget(text_label)

                page_layout.addWidget(diff_frame)

            # Add some spacing between pages
            self.diff_layout.addWidget(page_frame)

        # Push everything to top
        self.diff_layout.addStretch()

    def flash_highlight(self, widget):
        """Quickly flash a yellow border to show focus."""
        original = widget.styleSheet()
        widget.setStyleSheet(original + "bg-color: #4499FF;")
        QTimer.singleShot(100, lambda: widget.setStyleSheet(original))

    def next_diff(self):
        row = self.changes_viewer.currentRow()
        if row < self.changes_viewer.count() - 1:
            self.changes_viewer.setCurrentRow(row + 1)
            self.scroll_to_diff(row + 1)

    def prev_diff(self):
        row = self.changes_viewer.currentRow()
        if row > 0:
            self.changes_viewer.setCurrentRow(row - 1)
            self.scroll_to_diff(row - 1)

    def scroll_to_diff(self, index):
        """Scroll to the given diff on the viewer."""
        page, bbox, text, change_type = self.differences[index]
        # optionally scroll PDF viewer to this page or highlight it
        print(f"Jumping to diff on page {page}: {text}")
    
    def compare_pdfs(self):
        if not self.left_pdf_path or not self.right_pdf_path:
            return
        if self.compared:
            return  # already compared
        self.compared = True
        self.pdfworker.compare_pdf()
        diffs_left, diffs_right = self.pdfworker.removed_diffs, self.pdfworker.added_diffs
        pdfDTOLeft, pdfDTORight = self.pdfworker.pdfDTOLeft, self.pdfworker.pdfDTORight
        self.differences = self.pdfworker._differences
        self.populate_diff_view()
        self.left_pdf_viewer.highlight_differences(diffs_left, pdfDTOLeft, color=(1, 0, 0))
        self.right_pdf_viewer.highlight_differences(diffs_right, pdfDTORight, color=(0, 1, 0))
        self.left_pdf_viewer.clear_pdf()
        self.right_pdf_viewer.clear_pdf()
        self.left_pdf_viewer.draw_pdf(pdfDTOLeft.pdf_data)
        self.right_pdf_viewer.draw_pdf(pdfDTORight.pdf_data)