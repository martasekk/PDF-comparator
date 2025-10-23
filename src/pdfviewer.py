from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QFileDialog, QFrame, QSizePolicy
)
from PySide6.QtGui import QPixmap, QPainter, QColor, QImage
from PySide6.QtCore import Qt, QRect, Signal, QTimer, QPropertyAnimation, QEasingCurve
from ui.ui_mainwindow import Ui_MainWindow  # the generated file
import sys
import fitz
import comparemethods.myersdiff as myersdiff
from io import BytesIO
from PIL import Image

from collections import defaultdict

class ClickableFrame(QFrame):
    clicked = Signal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

class PDFPageLabel(QLabel):
    """Custom QLabel that scales its pixmap to the label width and draws highlights
       given in normalized coordinates (nx0, ny0, nx1, ny1) where ny uses PDF top origin (0..1)."""
    def __init__(self, pixmap=None, highlights=None):
        super().__init__()
        # keep a high-resolution original pixmap for high-quality scaling
        self._orig_pixmap = pixmap
        # highlights: list of (norm_bbox, color) where norm_bbox=(nx0, ny_top, nx1, ny_bottom)
        # color is (r,g,b) ints 0..255
        self.highlights = highlights or []
        if pixmap:
            # show scaled version immediately; do NOT permanently fix the height
            self.setPixmap(pixmap)
            # allow layout to compute sizes from sizeHint / updateGeometry
            self.setMinimumHeight(1)
        self.setScaledContents(False)
        # Expand horizontally, allow vertical size to adapt
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_scaled_pixmap()

    def _update_scaled_pixmap(self):
        if not self._orig_pixmap:
            return
        target_w = max(1, self.width())
        # scale from the high-res original so downscaling remains sharp
        scaled = self._orig_pixmap.scaledToWidth(target_w, Qt.SmoothTransformation)
        self.setPixmap(scaled)
        # update preferred/minimum/maximum so layouts can shrink/expand properly
        self.setMinimumHeight(scaled.height())
        self.setMaximumHeight(scaled.height())
        self.updateGeometry()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.highlights:
            return
        painter = QPainter(self)
        painter.setOpacity(0.3)
        pm = self.pixmap()
        if pm is None:
            painter.end()
            return
        sw = pm.width()
        sh = pm.height()
        # draw highlights: normalized coords multiplied by current pixmap size
        for norm_bbox, color in self.highlights:
            nx0, ny_top, nx1, ny_bottom = norm_bbox
            x = int(round(nx0 * sw))
            y = int(round(ny_top * sh))
            w = max(1, int(round((nx1 - nx0) * sw)))
            h = max(1, int(round((ny_bottom - ny_top) * sh)))
            painter.fillRect(QRect(x, y, w, h), QColor(*color))
        painter.end()
        
class PDFViewer(QWidget):
    """ScrollArea-based PDF viewer."""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.content_widget)
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)
        self.page_labels = []

    def load_pdf(self, path, highlights=None):
        pdf = fitz.open(path)
        # Clear old pages
        self.clear_pdf()

        self.draw_pdf(pdf, highlights)
            
    def draw_pdf(self, pdf, highlights=None):
        # Render pages at higher resolution for better quality when scaling.
        # Choose a render_scale: 1.0 = 72 DPI, 2.0 = ~144 DPI
        RENDER_SCALE = 2.4
        for page_num in range(pdf.page_count):
            page = pdf.load_page(page_num)
            mat = fitz.Matrix(RENDER_SCALE, RENDER_SCALE)
            pix = page.get_pixmap(matrix=mat)
             # Convert fitz Pixmap directly to QImage, then QPixmap
            if pix.alpha:
                fmt = QImage.Format_RGBA8888
            else:
                fmt = QImage.Format_RGB888
            qt_image = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
            qt_pixmap = QPixmap.fromImage(qt_image)

            # Prepare normalized highlights for this page
            raw_highlights = highlights.get(page_num, []) if highlights else []
            page_highlights = []
            pdf_rect = page.rect
            pdf_w = pdf_rect.width
            pdf_h = pdf_rect.height
            pm_w = qt_pixmap.width()
            pm_h = qt_pixmap.height()
            # compute mapping from PDF coords (x0,y0,x1,y1, origin bottom-left) to normalized coordinates
            for item in raw_highlights:
                # accept either (bbox, color) where bbox=(x0,y0,x1,y1) in PDF points
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    bbox, color = item[0], item[1]
                    if isinstance(bbox, (list, tuple)) and len(bbox) == 4 and pdf_w and pdf_h:
                        x0, y0, x1, y1 = bbox
                        nx0 = x0 / pdf_w
                        nx1 = x1 / pdf_w
                        # convert to normalized top-based coordinates for painting
                        ny_top = (pdf_h - y1) / pdf_h
                        ny_bottom = (pdf_h - y0) / pdf_h
                        page_highlights.append(((nx0, ny_top, nx1, ny_bottom), _normalize_qcolor(color)))
                        continue
                # if already normalized tuple (norm_bbox, color) accept it
                if isinstance(item, (list, tuple)) and len(item) == 2 and isinstance(item[0], (list, tuple)) and len(item[0]) == 4:
                    norm_bbox, color = item
                    page_highlights.append((tuple(norm_bbox), _normalize_qcolor(color)))
                    continue
                # unexpected format -> ignore

            label = PDFPageLabel(qt_pixmap, page_highlights)
            label.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(label)
            self.page_labels.append(label)
            
            
    def clear_pdf(self):
        for label in self.page_labels:
            self.scroll_layout.removeWidget(label)
            label.deleteLater()
        self.page_labels = []
            
    def smooth_scroll_to_bbox(self, page_index: int, bbox, duration: int = 400):
        """Smoothly scroll to a bounding box within a given page."""
        if not self.page_labels or page_index >= len(self.page_labels):
            return

        page_label = self.page_labels[page_index]

        # --- Compute Y offset inside scroll area ---
        # Each page_label is stacked vertically, so get its position
        base_y = page_label.pos().y()

        # Get pixmap and sizes
        pixmap = page_label.pixmap()
        pixmap_height = pixmap.height() if pixmap else page_label.height()
        page_height = page_label.height()

        x0, y0, x1, y1 = bbox

        target_y = int(base_y + (y1 + y0 - page_height)/2)

        scroll_bar = self.scroll_area.verticalScrollBar()
        current_value = scroll_bar.value()

        anim = QPropertyAnimation(scroll_bar, b"value", self)
        anim.setStartValue(current_value)
        anim.setDuration(duration)
        anim.setEndValue(target_y)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()

        # Prevent GC
        if not hasattr(self, "_scroll_anims"):
            self._scroll_anims = []
        self._scroll_anims.append(anim)
        
    def colorize_differences(self, diffs, pdfDTO, color=(1, 0, 0)):
        for idx, char in diffs:
            word = pdfDTO.words_pos[idx]
            bbox = word["bbox"]
            page_num = word["page_num"]

            highlight_rect = fitz.Rect(bbox)
            try: 
                output_page_right = pdfDTO.pdf_data[page_num]
                annot = output_page_right.add_rect_annot(highlight_rect)
                annot.set_colors(stroke=color,
                                fill=color)
                annot.set_opacity(0.2)
                annot.update()
                
            except Exception as e:
                print(f"Error adding annotation for added char '{char}' at index {idx} with bbox {bbox}: {e}")
        
    @staticmethod
    def pil_to_qpixmap(img):
        """Convert PIL image to QPixmap"""
        buf = BytesIO()
        img.save(buf, format="PNG")
        pixmap = QPixmap()
        pixmap.loadFromData(buf.getvalue(), "PNG")
        return pixmap

def _normalize_qcolor(color):
    """Return (r,g,b) ints 0..255 from float tuple (0..1) or int tuple."""
    if isinstance(color, (list, tuple)) and len(color) == 3:
        if all(isinstance(v, float) and 0.0 <= v <= 1.0 for v in color):
            return (int(color[0]*255), int(color[1]*255), int(color[2]*255))
        if all(isinstance(v, int) for v in color):
            return tuple(color)
    # fallback red
    return (255, 0, 0)