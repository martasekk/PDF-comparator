from tkinter import filedialog
from PIL import Image, ImageTk
import difflib
import fitz
import customtkinter as tk
import io
import re
import myersdiff

from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

def get_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs, return_dict=True)
    # Mean pooling
    embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings

def cosine_sim(a, b):
    return F.cosine_similarity(a, b).item()


class PDFComparatorApp(tk.CTk):
    def __init__(self, size):
        super().__init__()
        self.title("PDF Comparator")
        self.geometry("1200x600")
        self.resizable(True, True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Hlavní menu - otevřít soubor, vyčistit obsah plátna atd..
        top_frame = tk.CTkFrame(master=self, fg_color="#383838")
        
        top_frame.grid(row=0, column=0, sticky="ew")
        
        optionmenu_1 = tk.CTkOptionMenu(top_frame, values=["Load file", "Option 2", "Option 3"])
        optionmenu_1.grid(row=0, column=0, pady=2, padx=20, sticky="nsew")
        optionmenu_1.set("CTk Option Menu")
        
        compare = tk.CTkButton(top_frame, text= "Compare", command=self.compare_pdf)
        compare.grid(row=0, column=1, pady=2, padx=20, sticky="nsew")

        view_frame = tk.CTkFrame(master=self, fg_color="#383838")
        view_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        view_frame.grid_propagate(True)
        
        view_frame.grid_rowconfigure(0, weight=1)
        view_frame.grid_columnconfigure(0, weight=1)
        view_frame.grid_columnconfigure(1, weight=1)
        
        left_frame = tk.CTkFrame(master=view_frame)
        left_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=1)
        
        right_frame = tk.CTkFrame(master=view_frame)
        right_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew") 
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)
        
        diff_frame = tk.CTkFrame(master=view_frame)
        diff_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        diff_frame.grid_columnconfigure(0, weight=1)
        diff_frame.grid_rowconfigure(1, weight=1)
        
        # Spodní část - tlačítka pro porovnání PDF, vymazání obsahu atd.
        
        # - Levé okno
        # -- Menu pro levé okno
        # --- Tlačítko pro načtení souboru
        left_file_button = tk.CTkButton(left_frame, fg_color="gray", text="Load file", command=self.left_file_button_callback)
        left_file_button.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")

        # --- Tlačítko pro smazání obsahu
        left_delete_button = tk.CTkButton(left_frame, fg_color="gray", text="Delete", command=self.left_delete_button_callback)
        left_delete_button.grid(row=0, column=1, pady=5, padx=5, sticky="nsew")
        
        # -- Okno pro PDF
        self.first_window = PDFWindow(left_frame)
        
        # -- 

        # - Pravé okno
        # -- Menu pro pravé okno
        # --- Tlačítko pro načtení souboru
        right_file_button = tk.CTkButton(right_frame, fg_color="gray", text="Load file", command=self.right_file_button_callback)
        right_file_button.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")
        
        # --- Tlačítko pro smazání obsahu
        right_delete_button = tk.CTkButton(right_frame, fg_color="gray", text="Delete", command=self.right_delete_button_callback)
        right_delete_button.grid(row=0, column=1, pady=5, padx=5, sticky="nsew")
        
        # -- Okno pro PDF
        self.second_window = PDFWindow(right_frame)
        
        # - Zobrazení změn
               
    def left_file_button_callback(self):
        self.first_window.open_pdf()
        
    def left_delete_button_callback(self):
        self.first_window.clear_pdf_window()

    def right_file_button_callback(self):
        self.second_window.open_pdf()
           
    def right_delete_button_callback(self):
        self.second_window.clear_pdf_window()
        
    def extract_blocks(self, page):
        line_list = page.get_text("blocks")
        lines = [line[4] for line in line_list if line[6] == 0]
        return line_list, lines 
    
    def extract_pdf_blocks(self, pdf_path):
        pdf = fitz.open(pdf_path)
        line_list = []
        lines = []
        
        for page in pdf:
            lin, line = self.extract_words(page)
            line_list.extend(lin)
            lines.extend(line)
            
        print(f"Extracted {lines} lines from {pdf_path}")
        print(f"Extracted {line_list} blocks from {pdf_path}")
    
        pdf.close()
        return line_list, lines
        
    def extract_words(self, page):
        word_list = page.get_text("words")  # Get words with positions
        words = [word[4] for word in word_list]  # Extract only words
        
        return word_list, words

    def get_dict_with_page_num(self, page):
        dict = page.get_text("dict")
        for block in dict["blocks"]:
            block["page_num"] = page.number
        return dict

    def get_blocks(self, dict):
        return dict["blocks"]
    
    def get_block_info(self, block):
        """
        Convert a PyMuPDF block (from page.get_text("dict")) into a tuple:
        (x1, y1, x2, y2, text, None, None, page_num)
        """
        x0, y0, x1, y1 = block["bbox"]
        text = ""

        if block["type"] == 0:  # text block
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text += span["text"]
                text += "\n"
            text = text.strip()
        else:
            text = ""  # non-text blocks

        return (x0, y0, x1, y1, text, None, None, block["page_num"])
    
    def get_block_words_bbox(self, block):
        """
        Get the bounding box of all words in a block with their text"""
        words = []
        if block["type"] == 0:  # text block
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    words_in_span = span["text"].split()
                    for word in words_in_span:
                        words.append((span["bbox"][0], span["bbox"][1], span["bbox"][2], span["bbox"][3], word))
        return words

    def get_words_from_words_bbox(self, words_bbox):
        return [word[4] for word in words_bbox]

    def match_blocks(self, dict1, dict2, sim_thresh=0.8):
        matched_blocks = []
        used_blocks2 = set()
        
        blocks1 = self.get_blocks(dict1)
        blocks2 = self.get_blocks(dict2)
        
        # Precompute embeddings
        embeddings1 = [get_embedding(self.get_block_info(b)[4]) for b in blocks1] 
        embeddings2 = [get_embedding(self.get_block_info(b)[4]) for b in blocks2]

        for i, block1 in enumerate(blocks1):
            x1, y1, x2, y2, text1, _, _, page_num1 = self.get_block_info(block1)
            best_match = None
            best_score = sim_thresh
            best_j = -1
            operator = None

            for j, block2 in enumerate(blocks2):
                if j in used_blocks2:
                    continue
                x1b, y1b, x2b, y2b, text2, _, _, page_num2 = self.get_block_info(block2)

                if text1 == text2 and page_num1 == page_num2:
                    best_match = block2
                    operator = "text"
                    best_j = j
                    break
                
                sim = cosine_sim(embeddings1[i], embeddings2[j])
                if sim > best_score:
                    best_score = sim
                    best_match = block2
                    operator = f"check"
                    best_j = j

            # Record match or unmatched
            if best_match:
                matched_blocks.append([operator, block1, best_match])
                used_blocks2.add(best_j)
            else:
                matched_blocks.append(["-", block1, None])

        # Any remaining unmatched blocks in blocks2 are insertions
        for j, block2 in enumerate(blocks2):
            if j not in used_blocks2:
                matched_blocks.append(["+", None, block2])

        return matched_blocks
   
    def compare_pdf(self):
        pdf_path1 = self.first_window.pdf_path
        pdf_path2 = self.second_window.pdf_path
        pdf1 = fitz.open(pdf_path1)
        pdf2 = fitz.open(pdf_path2)
        
        output_pdf_left = fitz.open()
        output_pdf_right = fitz.open()

        dict1 = {"blocks": []}
        dict2 = {"blocks": []}
        
        for page_num in range(pdf1.page_count):
            
            print(f"Processing page {page_num}...")
            page1 = pdf1.load_page(page_num)
            page2 = pdf2.load_page(page_num)
            
            # add_page_num = lambda blocks, pn: [block + (pn,) for block in blocks]
              
            
            dict1["blocks"].extend(self.get_dict_with_page_num(page1)["blocks"])
            dict2["blocks"].extend(self.get_dict_with_page_num(page2)["blocks"])

            print(f"Extracted {len(dict1['blocks'])} blocks from PDF 1, page {page_num}")
            print(f"Extracted {len(dict2['blocks'])} blocks from PDF 2, page {page_num}")
            
            
        
            output_pdf_left.new_page(width=page1.rect.width, height=page1.rect.height)
            output_pdf_right.new_page(width=page2.rect.width, height=page2.rect.height)

            
        print("Starting block matching...")
        matched_blocks = self.match_blocks(dict1, dict2)
        print("Block matching completed.")
        
        for operator, block1, block2 in matched_blocks:
            
            if operator == "check":
                x1, y1, x2, y2, text1, _, _, page_num1 = self.get_block_info(block1)
                pad = 10
                highlight_rect = fitz.Rect(x1 - pad, y1 - pad, x2 + pad, y2 + pad)
                output_page_left = output_pdf_left[page_num1]
                output_page_right = output_pdf_right[page_num1]
                
                annot = output_page_left.add_rect_annot(highlight_rect)
                annot.set_border(width=1)
                annot.set_colors(stroke=(1, 0.3, 0))   
                annot.update()
                
                annot2 = output_page_right.add_rect_annot(highlight_rect)
                annot2.set_border(width=1)
                annot2.set_colors(stroke=(1, 0.3, 0))  
                annot2.update()
                
                block1_words = self.get_block_words_bbox(block1)
                block2_words = self.get_block_words_bbox(block2)
                
                myers = myersdiff.MyersDiff(self.get_words_from_words_bbox(block1_words), self.get_words_from_words_bbox(block2_words))
                added, removed = myers.get_diff_as_string()
                
                for idx, word in added:
                    
                    highlight_rect = fitz.Rect(block2_words[idx][0], block2_words[idx][1], block2_words[idx][2], block2_words[idx][3])
                    annot = output_page_right.add_highlight_annot(highlight_rect)
                    annot.set_colors(stroke=(0, 1, 0))
                    annot.set_opacity(0.3)
                    annot.update()
                    
                for idx, word in removed:
                    
                    highlight_rect = fitz.Rect(block1_words[idx][0], block1_words[idx][1], block1_words[idx][2], block1_words[idx][3])
                    annot = output_page_left.add_highlight_annot(highlight_rect)
                    annot.set_colors(stroke=(1, 0, 0))
                    annot.set_opacity(0.3)
                    annot.update()
                    
                
            elif operator == "-":
                x1, y1, x2, y2, text1, _, _, page_num1 = self.get_block_info(block1)
                pad = 10
                highlight_rect = fitz.Rect(x1 - pad, y1 - pad, x2 + pad, y2 + pad)
                output_page_left = output_pdf_left[page_num1]
                annot = output_page_left.add_highlight_annot(highlight_rect)
                annot.set_colors(stroke=(1, 0, 0))
                annot.set_opacity(0.3)
                annot.update()
                
            elif operator == "+":
                x1, y1, x2, y2, text1, _, _, page_num1 = self.get_block_info(block2)
                pad = 10
                highlight_rect = fitz.Rect(x1 - pad, y1 - pad, x2 + pad, y2 + pad)
                output_page_right = output_pdf_right[page_num1]
                annot = output_page_right.add_highlight_annot(highlight_rect)
                annot.set_colors(stroke=(0, 1, 0))
                annot.set_opacity(0.3)
                annot.update()
        
        
                
        for page_num in range(pdf1.page_count):
            output_pdf_left[page_num].show_pdf_page(page1.rect, pdf1, page_num)
            output_pdf_right[page_num].show_pdf_page(page2.rect, pdf2, page_num)
                
                
        output_pdf_left.save("output_left.pdf")
        self.first_window.display_pdf("output_left.pdf")
        output_pdf_right.save("output_right.pdf")
        self.second_window.display_pdf("output_right.pdf")
        output_pdf_left.close()
        output_pdf_right.close()
        
        
        
    def comparemethod1():
        # Placeholder for future comparison method
        pass
    
#############################################################################################
#   Hlavní okno aplikace
#    


            
#############################################################################################
#   Okno pro PDF
#

class PDFWindow(tk.CTkFrame):    
    def __init__(self, parent):
        super().__init__(parent)
        self.pdf_pages = []
        self.pdf_path = None
        self.parent = parent
        self.labels = []
        self.separation = 2
        
        # Plátno pro vykreslení pdf souboru
        self.pdf_window = tk.CTkScrollableFrame(parent)
        self.pdf_window.grid(row= 1, column= 0, sticky="nsew", columnspan=3)

    def clear_pdf_window(self):
        for label in self.labels:
            label.destroy()
        self.pdf_pages.clear()
        self.labels.clear()

                
    def open_pdf(self):
        self.pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        print(f"Selected PDF: {self.pdf_path}")
        if self.pdf_path:
            self.display_pdf(self.pdf_path)

    def display_pdf(self, pdf_path):
        self.clear_pdf_window()
        self.pdf_path = pdf_path
        pdf = fitz.open(self.pdf_path)
        for page in pdf:
                page_data = page.get_pixmap()
                pix = fitz.Pixmap(page_data, 0) if page_data.alpha else page_data
                img = Image.open(io.BytesIO(pix.tobytes('ppm')))
                label_img = tk.CTkImage(img, size=(img.width, img.height))
                self.pdf_pages.append(label_img)
        pdf.close()
        self.redraw_pdf()
            
    def redraw_pdf(self):
        if self.pdf_path:
            num = 0
            for i in self.pdf_pages:
                label = tk.CTkLabel(self.pdf_window, image=i, text="")
                label.grid(row=num, column=0, padx=10, pady=10)
                self.labels.append(label)
                num += 1
        else:
            print("No PDF file loaded to redraw.")
        

if __name__ == "__main__":
    app = PDFComparatorApp("1600x900")
    app.mainloop()
    
    
    # def compare_pdf(self):
    #     pdf_path1 = self.first_window.pdf_path
    #     pdf_path2 = self.second_window.pdf_path
    #     pdf1 = fitz.open(pdf_path1)
    #     pdf2 = fitz.open(pdf_path2)
        
    #     output_pdf_left = fitz.open()
    #     output_pdf_right = fitz.open()
        
    #     blocks1 = []
    #     blocks2 = []
        
    #     for page_num in range(pdf1.page_count):
    #         page1 = pdf1.load_page(page_num)
    #         page2 = pdf2.load_page(page_num)
            
    #         blocks1 = page1.get_text("blocks")
    #         blocks2 = page2.get_text("blocks")

    #         # tabs1 = page1.find_tables()
    #         # if tabs1.tables:
    #         #     print(tabs1[0].extract())
    #         #     page1.add_redact_annot(tabs1[0].bbox)
    #         #     page1.apply_redactions()
    #         #     print("printing bbox", tabs1[0].bbox)
            

            
    #         # tabs2 = page2.find_tables()
    #         # if tabs2.tables:
    #         #     print(tabs2[0].extract())
    #         #     page2.add_redact_annot(tabs2[0].bbox)
    #         #     page2.apply_redactions()
    #         #     print("printing bbox", tabs2[0].bbox)
            
    #         # word_positions1, words1 = self.extract_clean_text(page1)
    #         # word_positions2, words2 = self.extract_clean_text(page2)

    #         # diff = list(difflib.ndiff(words1, words2))
    #         # diff_output = []
    #         # print("Differences found:", diff)
    #         # output_page_left = output_pdf_left.new_page(width=page1.rect.width, height=page1.rect.height)
    #         # output_page_right = output_pdf_right.new_page(width=page2.rect.width, height=page2.rect.height)

    #         # output_page_left.show_pdf_page(page1.rect, pdf1, page_num)
    #         # output_page_right.show_pdf_page(page2.rect, pdf2, page_num)
            
    #         # # Highlight differences in the left PDF
    #         # for word in diff:

    #         #     if word == "? ^\n":
    #         #         continue
                
    #         #     if word.startswith('+'):
    #         #         diff_output.append(word)
    #         #         print(word)
    #         #         word_position = word_positions2[word_positions2[4].index(word[2:])]
    #         #         highlight_rect = fitz.Rect(word_position[:4])
    #         #         annot = output_page_right.add_highlight_annot(highlight_rect)
    #         #         annot.set_colors(stroke=(0, 1, 0))
    #         #         annot.set_opacity(0.3)
    #         #         annot.update()
                    
    #         #     if word.startswith('-'):
    #         #         diff_output.append(word)
    #         #         word_position = word_positions1[word_positions1[4].index(word[2:])]
    #         #         highlight_rect = fitz.Rect(word_position[:4])
    #         #         annot = output_page_left.add_highlight_annot(highlight_rect)
    #         #         annot.set_colors(stroke=(1, 0, 0))
    #         #         annot.set_opacity(0.3)
    #         #         annot.update()
            
        
    #     output_pdf_left.save("output_left.pdf")
    #     output_pdf_left.close()
    #     output_pdf_right.save("output_right.pdf")
    #     output_pdf_right.close()
        
    #     self.first_window.display_pdf("output_left.pdf")
    #     self.second_window.display_pdf("output_right.pdf")
        