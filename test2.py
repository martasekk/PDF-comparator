import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import fitz  # PyMuPDF

class PDFComparator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF Comparator")
        self.geometry("1000x800")
        
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Adding a scroll bar
        self.scroll_y = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll_y.set)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.pdf_images = []
        
        # Menu Bar
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=False)
        file_menu.add_command(label="Open", command=self.open_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        self.config(menu=menu_bar)
        
    def open_pdf(self):
        pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if pdf_path:
            self.display_pdf(pdf_path)

    def display_pdf(self, pdf_path):
        # Clear any previous images
        self.canvas.delete("all")
        self.pdf_images.clear()

        doc = fitz.open(pdf_path)
        for page_number in range(doc.page_count):
            page = doc.load_page(page_number)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scaling for better resolution
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_tk = ImageTk.PhotoImage(img)
            self.pdf_images.append(img_tk)  # Store reference to prevent garbage collection
            self.canvas.create_image(0, sum(image.height() for image in self.pdf_images[:-1]), anchor="nw", image=img_tk)
        
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def on_canvas_resize(self, event):
        # Adjust the canvas when the window is resized
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

# Create and run the application
if __name__ == "__main__":
    app = PDFComparator()
    app.mainloop()
