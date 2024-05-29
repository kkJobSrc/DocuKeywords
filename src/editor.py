from . import common
import pypdf
import numpy as np

class pdf_editor():
    def __init__(self, sec_num, header, footer, unuse) -> None:
        self.full_pdf=None

        self.split_page_num  = int(sec_num)
        self.header_page_num = int(header)
        self.footer_page_num = int(footer) #NONE
        if(len(unuse) != 0):
            self.unuse_page_list = [int(_n)-self.header_page_num-1 for _n in unuse.split(":")]
        else:
            self.unuse_page_list =[]
        self.input_base_dir = common.PDF_PATH
        self.split_out_dir = common.SPLIT_RESULT_DIR

    def remove_header_footer(self, target_pages):
        if(self.header_page_num != 0):
            target_pages = target_pages[self.header_page_num:]
        if(self.footer_page_num != 0):
            target_pages = target_pages[:-self.footer_page_num]
        if(self.unuse_page_list):
            target_pages = [target_pages[i] for i in range(len(target_pages))  if not( i in self.unuse_page_list)]

        return target_pages


    def remove_no_need_page(self, target_pages):
        _page_letter_nums=[]
        for _page in target_pages:
            _txt = _page.extract_text()
            _page_letter_nums.append(len(_txt))

        # calc. page letter number ave. and std.
        _data = np.array(_page_letter_nums)
        _lim = np.average(_data) + np.std(_data)
        print("lim:" ,_lim, _page_letter_nums)
        _target_pages = pypdf.PdfWriter()
        for _p ,_d in zip(target_pages, (_data < _lim)):
            if(_d):_target_pages.add_page(_p)
        
        return _target_pages.pages

    def split_pdf(self):
        common.remove_files(self.split_out_dir)

        # get target page
        _target_pages = self.full_pdf.pages
        _target_pages = self.remove_header_footer(_target_pages)
        #_target_pages = self.remove_no_need_page(_target_pages)

        # split pdf page
        _writer = pypdf.PdfWriter()
        for i, _pdf in enumerate(_target_pages):
            _writer.add_page(_pdf)
            if ((i+1)%self.split_page_num == 0):
                _file_name = "splitPdf_{0:03d}.pdf".format(i)
                _output_file_name = self.split_out_dir/_file_name
                _writer.write(_output_file_name)
                _writer = pypdf.PdfWriter()
                print("[out]: {:s}".format(_file_name))

    def read_pdf(self, file_name):
        _file_path = self.input_base_dir/file_name
        self.full_pdf = pypdf.PdfReader(_file_path)