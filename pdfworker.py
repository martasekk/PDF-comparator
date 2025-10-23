import fitz
from comparemethods.myersdiff import MyersDiff
from comparemethods.deepdiffcompare import DeepDiffCompare
from comparemethods.sequencematchercompare import SequenceMatcherCompare
from comparemethods.hirschbergcompare import HirschbergCompare
from pdfdto import *

class PDFWorker:
    def __init__(self):
        self.left_pdf = None
        self.right_pdf = None
        
        self.added_diffs = []
        self.removed_diffs = []
        
        
        self._differences = []  # Stores differences between PDFs for later visualization
        self._selectedCompareMethod = None
        self._compareMethod1 = MyersDiff
        self._compareMethod2 = DeepDiffCompare
        self._compareMethod3 = SequenceMatcherCompare
        self._compareMethod4 = HirschbergCompare
        self._allCompareMethods = [self._compareMethod1, self._compareMethod2, self._compareMethod3, self._compareMethod4]

        self.pdfDTOLeft = PDFDTO()
        self.pdfDTORight = PDFDTO()

    def __LoadPDF(self, filePath, pdfDTO):
        pdf = fitz.open(filePath)
        words_pos = []
        words_txt = []
        
        for page_num in range(pdf.page_count):
            page1 = pdf.load_page(page_num)
            dict1 = page1.get_text("rawdict")
            page_words = self.chars_to_words(rawdict=dict1, page_num=page_num)
            words_pos.extend(page_words)
            words_txt.extend([w["text"] for w in page_words])
            
        pdfDTO.pdf_data = pdf
        pdfDTO.words_pos = words_pos
        pdfDTO.words_txt = words_txt
        
    def LoadPDF_Left(self, filePath):
        self.__LoadPDF(filePath, self.pdfDTOLeft)
        
    def LoadPDF_Right(self, filePath):
        self.__LoadPDF(filePath, self.pdfDTORight)
            
    def chars_to_words(self, rawdict, page_num=0, x_threshold=2.0):
        words = []

        for block in rawdict.get("blocks", []):
            if block.get("type") != 0:  # only text blocks
                continue

            for line in block.get("lines", []):
                current_word = ""
                word_bbox = None
                last_x1 = None

                for span in line.get("spans", []):
                    for ch in span.get("chars", []):
                        text = ch.get("c", "")
                        bbox = ch.get("bbox", None)
                        if not bbox:
                            continue

                        if not text.strip():  # skip spaces or invisible chars
                            if current_word:
                                words.append({
                                    "text": current_word,
                                    "bbox": word_bbox,
                                    "page_num": page_num
                                })
                                current_word = ""
                                word_bbox = None
                            last_x1 = None
                            continue

                        x0, y0, x1, y1 = bbox

                        # If too far from previous char → start new word
                        if last_x1 is not None and abs(x0 - last_x1) > x_threshold:
                            words.append({
                                "text": current_word,
                                "bbox": word_bbox,
                                "page_num": page_num
                            })
                            current_word = text
                            word_bbox = list(bbox)
                        else:
                            # Continue same word
                            current_word += text
                            if word_bbox:
                                word_bbox[2] = max(word_bbox[2], x1)
                                word_bbox[3] = max(word_bbox[3], y1)
                            else:
                                word_bbox = list(bbox)

                        last_x1 = x1

                # flush last word in line
                if current_word:
                    words.append({
                        "text": current_word,
                        "bbox": word_bbox,
                        "page_num": page_num
                    })

        return words
    
    def group_adjacent_words(self, diffs, words, distance_threshold=20.0, line_threshold=5.0):
        grouped = []
        current_group = None
        for idx, change_type in diffs:
            if idx < 0 or idx >= len(words):
                continue
            w = words[idx]
            text = w["text"]
            bbox = fitz.Rect(w["bbox"])
            page = w["page_num"]
            if current_group is None:
                current_group = {
                    "page": page,
                    "bbox": bbox,
                    "text": text,
                    "change_type": change_type,
                    "last_bbox": bbox
                }
                continue
            same_page = (page == current_group["page"])
            same_type = (change_type == current_group["change_type"])
            prev_bbox = current_group["last_bbox"]
            # Check if on same line or paragraph (vertical proximity)
            vertical_close = abs(bbox.y0 - prev_bbox.y0) < line_threshold or abs(bbox.y1 - prev_bbox.y1) < line_threshold
            horizontal_close = (bbox.x0 - prev_bbox.x1) < distance_threshold
            if same_page and same_type and (vertical_close or horizontal_close):
                # merge with current group
                current_group["text"] += " " + text
                current_group["bbox"] = fitz.Rect(
                    min(current_group["bbox"].x0, bbox.x0),
                    min(current_group["bbox"].y0, bbox.y0),
                    max(current_group["bbox"].x1, bbox.x1),
                    max(current_group["bbox"].y1, bbox.y1)
                )
                current_group["last_bbox"] = bbox
            else:
                grouped.append({
                    "page": current_group["page"],
                    "bbox": current_group["bbox"],
                    "text": current_group["text"],
                    "change_type": current_group["change_type"]
                })
                current_group = {
                    "page": page,
                    "bbox": bbox,
                    "text": text,
                    "change_type": change_type,
                    "last_bbox": bbox
                }
        if current_group:
            grouped.append({
                "page": current_group["page"],
                "bbox": current_group["bbox"],
                "text": current_group["text"],
                "change_type": current_group["change_type"]
            })
        return grouped

    def compare_pdf(self):
        selected_method = self._selectedCompareMethod or self._compareMethod1
        model = selected_method([w["text"] for w in self.pdfDTOLeft.words_pos],
                                    [w["text"] for w in self.pdfDTORight.words_pos])
        self.added_diffs, self.removed_diffs = model.get_diff_as_string()
                
        added_diffs = [(idx, "added") for idx, _ in self.added_diffs]
        removed_diffs = [(idx, "removed") for idx, _ in self.removed_diffs]
        all_diffs = added_diffs + removed_diffs

        # Group adjacent word changes
        grouped_diffs = (self.group_adjacent_words(removed_diffs, self.pdfDTOLeft.words_pos) 
                        + self.group_adjacent_words(added_diffs, self.pdfDTORight.words_pos))

        # Store for visualizing later
        self._differences = [
            (g["page"], g["bbox"], g["text"], g["change_type"])
            for g in grouped_diffs
        ]
