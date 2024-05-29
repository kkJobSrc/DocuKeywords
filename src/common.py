from datetime import datetime
from pdfminer.layout import LAParams # Class for parameters of text extractor

import json
import pathlib
import os


### Path
BASE_PATH =  pathlib.Path.cwd()
PDF_PATH = BASE_PATH/"origin_pdf"
SPLIT_RESULT_DIR=BASE_PATH/"split_pdf"
TXT_OUT_DIR = BASE_PATH/"text"
RESULT_OUT_DIR = BASE_PATH/"result"

def remove_files(dir):
    _files = dir.glob("*.pdf")
    for _f in _files: os.remove(_f)

def output_json_name_date(dir,base_name,data):
    _name = "{0}_{1}.json".format(base_name,datetime.now().strftime('%Y%m%d_%H%M%S'))
    _path = dir/_name
    
    if not(type(data) is dict) : return
    with open(_path, "w" ) as _j:
         json.dump(data, _j, indent=4, ensure_ascii=False)



### PDF size conf
IGNORE_HEIGHT_RATE = 0.05 #*100[%] header/footer
TITEL_HEIGHT_RATE  = 0.25 #*100[%] inucled title, authors and keyword
CENTER_RATE        = 0.50 #*100[%]

rate_pos =lambda h,r: h * r
offset_rate_pos=lambda h,r: h - (h * r)

def get_header_edge(h): return offset_rate_pos(h, IGNORE_HEIGHT_RATE)
def get_footer_edge(h): return rate_pos(h, IGNORE_HEIGHT_RATE)
def get_title_edge(h) : return offset_rate_pos(h, TITEL_HEIGHT_RATE)
def get_center_pos(w) : return rate_pos(w, CENTER_RATE)

###  PDFPageAggregator configulation
def get_options():
        la_params = LAParams()
        la_params.detect_vertical=True
        la_params.line_overlap=0.5 
        la_params.word_margin=0.1 
        la_params.char_margin=2.0 
        la_params.line_margin=0.2
        return la_params

