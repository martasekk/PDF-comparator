
class CM_Name(Enum):
    CM_1 = "compareMethod_1"
    CM_2 = "compareMethod_2"

class CompareMethod_1:
	Name = CM_Name.CM_1
	def Compare(self, text1, text2):
        return text1, text2

class CompareMethod_2:
	Name = CM_Name.CM_2
	def Compare(self, text1, text2):
        return text1, text2

class PDFWorker:
	_selectedCompareMethod = None
	_compareMethod1 = CompareMethod_1()
	_compareMethod2 = CompareMethod_2()
	_allCompareMethods = [_compareMethod1, _compareMethod2]

    _pdfDataLeft = None
    _pdfDataRight = None
    _txtLeft = ""
    _txtRight = ""
    
	def LoadPDF(self, filePath):
        pass
    
    def ExtractTxt(self, pdfData):
        pass
    
    def LoadPDF_Left(filePath):
        self._pdfDataLeft = LoadPDF(filePath)
        self._txtLeft = ExtractTxt(pdf)
    
    def LoadPDF_Right(filePath):
        self._pdfDataRight = LoadPDF(filePath)
        self._txtRight = ExtractTxt(pdf)
     
	def SetCompareMethod(self, methodName)
        for method in self._allCompareMethods:
            if method.Name == methodName:
                self._selectedCompareMethod = method
                break
            
	def GetDiffs(self):
        _selectedCompareMethod.Compare(_txtLeft, _txtRight)
 

class Window:
	PDFWorker()
	
	OpenPDF1+2()
		LoadPDF
  
	ComboBox()
		SetCompare1() -> PDFWorker.SetCompareMethod(CM_Name.CM_1)
		SetCompare2() -> PDFWorker.SetCompareMethod(CM_Name.CM_2)

	Compare() 
		PDFWorker.GetDiffs()
