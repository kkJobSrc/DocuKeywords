from src import editor
from src import papar
from src import position_rank

import argparse


if "__main__" == __name__:

    # python .\main.py -s 2 -t 6 -f -u 33:62 -e -p
    _parser = argparse.ArgumentParser()
    _parser.add_argument("-s", "--sp_num", default=2, help="abstract par page.")
    _parser.add_argument("-t", "--header", default=0, help="header number of page.")
    _parser.add_argument("-f", "--footer", default=0, help="footer number of page.")
    _parser.add_argument("-u", "--unuse", default="", help="ignore page.(delimiter = :) ")
    _parser.add_argument("-e", "--edit", action="store_true", help="flag for split full pdf")
    _parser.add_argument("-p", "--parse", action="store_true", help="flag for pars abstracts")
    _args = _parser.parse_args()

    if(_args.edit):
        print("=== start PDF split ===")
        _editor = editor.pdf_editor(_args.sp_num, _args.header, _args.footer, _args.unuse)
        _editor.read_pdf("jgs58_DS_20230711.pdf")
        _editor.split_pdf()
        print("=== end PDF split ===")

    if(_args.parse):
        print("=== start parse PDF ===")
        _papers = papar.parser()
        _papers.initalize()
        print("=== end parse PDF ===")


        print("=== start extract key words ===")
        for  i, _p in enumerate(_papers.papars):
            _extractor = position_rank.positon_rank(_p.title, _p.body)
            _papers.papars[i].keyword = _extractor.execute()
            print("\n",_p.file_name)
            print("Title: {:s}".format(_p.title))
            print("Authors: ", _p.authors)
            print("Keyword: ", _p.keyword)
        print("=== end extract key words ===")

        _papers.result_summary() # output json file



