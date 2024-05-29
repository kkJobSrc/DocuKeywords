from . import common
from . import word_analyze

## https://qiita.com/f-suzuki/items/d861caf8ca9232c991fe
from pdfminer.pdfinterp import PDFResourceManager   #PDFのテキストや画像を管理するクラス
from pdfminer.converter import TextConverter        #PDFのテキストを抽出するためのクラス
from pdfminer.pdfpage import PDFPage                #PDFの1ページごとの情報を管理するクラス
from pdfminer.pdfinterp import PDFPageInterpreter   #PDFpageから必要な処理を行うクラス

from io import StringIO

## https://qiita.com/fumitrial8/items/f3d92fca0de409feaee9
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTContainer, LTTextBox, LTTextLine, LTChar

import unicodedata

class paper():
    def __init__(self, name, title, authors ,body):
        self.file_name = name
        self.title = title.replace("\n", "")
        self.authors = authors
        self.body = body
        self.keyword=[]


    def disp_menber(self):
        print("Title: ", self.title)
        print("Authors: ", self.authour)
        print("Body:\n", self.body)


    def formater(self): #JSON
        self.json={
            "title"  : self.title,
            "authors": self.authors,
            "keyword": self.keyword
            }


class parse_base():
    def __init__(self):
        self.baggage = []
        self.input_dir = common.SPLIT_RESULT_DIR
        self.files = self.input_dir.glob("*.pdf")
        common.remove_files(common.TXT_OUT_DIR)

    def get_file_path(self, file_name):
        return self.input_dir/file_name



class parser(parse_base):
    def __init__(self):
        super().__init__()
        self.papars =[]
        self.summary = {}

    def result_summary(self, isOutput=True):
        for _p in self.papars:
            _p.formater()
            self.summary[_p.file_name.name] = (_p.json)

        if(isOutput):
            common.output_json_name_date(common.RESULT_OUT_DIR, "paper", self.summary)


    def __del__( self ) :
        pass



    def find_layout(self, layout, lager_type=LTTextBox, samller_type=LTTextLine):
        if isinstance(layout, samller_type):
            return [layout]
        if isinstance(layout, lager_type):
            _ret = []
            for child in layout:
                _ret.extend(self.find_layout(child, lager_type, samller_type))
            return _ret
        return []

    def extract_above_eddge(self, lines,edge):
        _ret = ""
        for _l in lines:
            if (edge < _l.y0):
                _ret+=_l.get_text()
        return _ret

    def read(self,file_name):
        pdf_resource_manager = PDFResourceManager() #get PDFResourceManager object
        converter = PDFPageAggregator(pdf_resource_manager, laparams = common.get_options())
        pdf_iterpreter = PDFPageInterpreter(pdf_resource_manager, converter) # set manager and converter PDFPageInterpreter

        _page_counter = 1
        _authors=[]
        with open(self.get_file_path(file_name), "rb") as _file_bainry:
            print(file_name.name)

            _title = ""
            _body = ""
            _title_elements=[]

            for _page in PDFPage.get_pages(_file_bainry, maxpages = 3):
                pdf_iterpreter.process_page(_page)

                ## get page size
                _page_height = converter.get_result().height
                _page_width  = converter.get_result().width

                ## get region, position
                _center_pos = common.get_center_pos(_page_width) # center pos
                _title_boader = common.get_title_edge(_page_height) # title, authores
                _header_boder = common.get_header_edge(_page_height) # header
                _footer_boder = common.get_footer_edge(_page_height) # footer

                ## loop for text boxes
                _boxes=self.find_layout(converter.get_result(), LTContainer, LTTextBox)
                _boxes.sort(key=lambda b: (-b.y1, b.x0)) # sort with box position.
            
                ## initialized position buffer
                _pos_y_first_author = 0            # position of first authour (virtical)
                _pos_y_end_author = _page_height   # position of authour detecte latest(virtical)

                for _box in _boxes: #(x0 =left / y0=lower / x1=right / y1=upper)
                    _lines = self.find_layout(_box, LTTextBox, LTTextLine)
                    for _line in _lines:
                        if ( _footer_boder < _line.y1  and _line.y0 < _header_boder): # ignore header and header

                            ## read title information
                            if ( (_line.y0 > _title_boader) and (_page_counter == 1) ): 
                                _author = word_analyze.detect_person_name(_line.get_text()) # extract author
                                 
                                if _author:
                                    _authors.extend(_author)

                                    ## update author edge 
                                    if _pos_y_first_author==0:
                                        _pos_y_first_author = _line.y1
                                        _title = self.extract_above_eddge(_title_elements, _pos_y_first_author)
                                        
                                    if _pos_y_end_author > _line.y0:
                                        _pos_y_end_author = _line.y0
                                        _body=""
                                else:
                                    if _pos_y_first_author == 0:
                                        _title_elements.append(_line)#.get_text())

                                    if _pos_y_end_author > _line.y0:
                                        _body += _line.get_text().replace("\n","")
                            elif (_page_counter > 1):
                              _body += _line.get_text().replace("\n","")
                            else:
                                pass #do nothing
                    #_body += "\n"
                _page_counter += 1
            converter.close()
        
        if (_title):
            return paper(file_name, _title, _authors, _body)




    def initalize(self):
        txt=""
        ## parse PDF file
        for _file in sorted(self.files, key = lambda x: x.name):
            _papar = self.read(_file)

            if not(_papar is None):
                self.papars.append(_papar)
    
        ## output parse result
        _path=common.TXT_OUT_DIR/"resutl.txt"
        with open(_path, "w", encoding="utf-8") as _f:
            _f.write(txt)


