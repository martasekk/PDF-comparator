import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import difflib
import fitz

class PDFComparatorApp(tk.Tk):
    def __init__(self, size):
        super().__init__()
        self.title("PDF Comparator")
        self.geometry(size)

        menu_bar = tk.Menu()
        self.config(menu=menu_bar)
        
        self.first_window = PDFWindow(self,0,0)
        self.second_window = PDFWindow(self,0,1)
        
        # Hlavní menu - otevřít soubor, vyčistit obsah plátna atd..
        file_menu = tk.Menu(menu_bar, tearoff= False)
        file_menu.add_command(label= "Open", command= self.first_window.open_pdf)
        file_menu.add_command(label= "Clear", command= self.first_window.clear_pdf_window)
        file_menu.add_separator()
        file_menu.add_command(label= "Exit", command= quit)
        menu_bar.add_cascade(label="File", menu= file_menu) 
        
        # Výběr možností porovnávání - todo
        compare_menu = tk.Menu(menu_bar, tearoff= False)
        compare_menu.add_command(label= "Open", command= self.second_window.open_pdf)
        compare_menu.add_command(label= "Compare PDFs", command=lambda:[self.compare_pdf(), self.first_window.display_pdf("output_left.pdf"), self.second_window.display_pdf("output_right.pdf")])
        menu_bar.add_cascade(label="Compare", menu= compare_menu)
        
    def extract_words_with_positions(self, page):
        word_list = page.get_text("words")  # Get words with positions
        words = [word[4] for word in word_list]  # Extract only words
        
        return word_list, words

    def compare_pdf(self):
        pdf_path1 = self.first_window.pdf_path
        pdf_path2 = self.second_window.pdf_path
        pdf1 = fitz.open(pdf_path1)
        pdf2 = fitz.open(pdf_path2)
        
        output_pdf_left = fitz.open()
        output_pdf_right = fitz.open()
        
        for page_num in range(pdf1.page_count):
            page1 = pdf1.load_page(page_num)
            page2 = pdf2.load_page(page_num)

            word_positions1, words1 = self.extract_words_with_positions(page1)
            word_positions2, words2 = self.extract_words_with_positions(page2)
            
            print(word_positions1)
            print(word_positions2)

            diff = list(difflib.ndiff(words1, words2))
            diff_output = []

            output_page_left = output_pdf_left.new_page(width=page1.rect.width, height=page1.rect.height)
            output_page_right = output_pdf_right.new_page(width=page2.rect.width, height=page2.rect.height)

            output_page_left.show_pdf_page(page1.rect, pdf1, page_num)
            output_page_right.show_pdf_page(page2.rect, pdf2, page_num)

            i = 0
            for word in diff:
                if word.startswith('+') or word == "? ^\n":
                    continue
                print(word, i)
                if word.startswith('-'):
                    diff_output.append(word)
                    word_position = word_positions1[i]
                    highlight_rect = fitz.Rect(word_position[:4])
                    annot = output_page_left.add_highlight_annot(highlight_rect)
                    annot.set_colors(stroke=(0, 1, 0))
                    annot.update()
                i += 1
                
            i = 0
            for word in diff:
                if word.startswith('-') or word == "? ^\n":
                    continue
                print(word, i)
                if word.startswith('+'):
                    diff_output.append(word)
                    word_position = word_positions2[i]
                    highlight_rect = fitz.Rect(word_position[:4])
                    annot = output_page_right.add_highlight_annot(highlight_rect)
                    annot.set_colors(stroke=(1, 0, 0))
                    annot.update()
                i += 1

        output_pdf_left.save("output_left.pdf")
        output_pdf_left.close()
        output_pdf_right.save("output_right.pdf")
        output_pdf_right.close()
        
        print(diff_output)
        
   
            
#############################################################################################
#   Okno pro PDF
#
class PDFWindow(tk.Frame):    
    def __init__(self, parent, row, column):
        super().__init__(parent)
        self.pdf_pages = []
        self.pdf_path = None
        
        # Hlavní frame
        self.main_frame = tk.Frame(parent, bg= "white", height= 1100, width= 800 )
        self.main_frame.grid(row= row, column= column)
        self.main_frame.grid_propagate(False)

        # Plátno pro vykreslení pdf souboru
        self.pdf_window = tk.Canvas(self.main_frame, bg= "gray", height= 800, width= 700)
        self.pdf_window.config(scrollregion=self.pdf_window.bbox(tk.ALL))
        self.pdf_window.grid(row= row, column= column)

        # Scrollbar
        self.scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.pdf_window.yview)
        self.scrollbar.grid(row= row, column= column+1, sticky=("N", "S"))

        self.pdf_window.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=self.pdf_window.yview)

        self.pdf_window.bind('<Enter>', self._bound_to_mousewheel)
        self.pdf_window.bind('<Leave>', self._unbound_to_mousewheel)

    
    def _bound_to_mousewheel(self, event):
        self.pdf_window.bind_all("<MouseWheel>", self._scroll_ev)

    def _unbound_to_mousewheel(self, event):
        self.pdf_window.unbind_all("<MouseWheel>")
    
    def clear_pdf_window(self):
        self.pdf_pages = []
        self.pdf_window.delete("all")
            
    def scroll_ev(self, event):
        if event.num == 5 or event.delta == -120:
            self.pdf_window.yview_scroll(1, "units")
        if event.num == 4 or event.delta == 120:
            self.pdf_window.yview_scroll(-1, "units")
                
    def open_pdf(self):
        self.pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        if self.pdf_path:
            self.display_pdf(self.pdf_path)

    def display_pdf(self, pdf_path):
        self.pdf_path = pdf_path
        pdf = fitz.open(self.pdf_path)
        self.clear_pdf_window()
        for page in pdf:
            pixmap = page.get_pixmap()
            page_image = ImageTk.PhotoImage(Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples))

            self.pdf_window.create_image(0, page.number * pixmap.height, anchor="nw", image=page_image)
            self.pdf_pages.append(page_image)

        self.pdf_window.configure(scrollregion= self.pdf_window.bbox(tk.ALL))
        pdf.close()
        

if __name__ == "__main__":
    app = PDFComparatorApp("1600x900")
    app.mainloop()
    