from . import common
from . import word_analyze

from collections import Counter

import copy
import math as m
import numpy as np

# https://qiita.com/ymym3412/items/bc3d90e9e1b51959649a


class positon_rank():

    def __init__(self, title, body, alpha=0.85, window=6, extract_num=5):
        # text
        self.full_text= title + body
        self.window_size = window # length of search words
        self.phrase = [] 
        self.origin_words=[]
        self.unique_words = set()
        self.words_num = 0
        self.co_occ_dict = {}
        self.extract_num = extract_num

        # calculate parameters
        self.p = np.array([]) # teleport vector
        self.M = np.array([])
        self.s_vec = np.array([])
        self.alpha = alpha # dumping factor


    def search_words_within_window(self, idx, word):
        _range = m.ceil(self.window_size/2) + 1
        _list = self.co_occ_dict[word]
        for  i in range(1, _range):
            _pre_id  = idx - i
            _post_id = idx + i

            if 0 < _pre_id :
               _list.append(self.origin_words[_pre_id]) 
            if _post_id < len(self.origin_words):
                _list.append(self.origin_words[_post_id])

        self.co_occ_dict[word] = _list


    def split_words(self, lang="jp"):
        if lang == "jp":
            self.origin_words, self.phrase = word_analyze.tokenize(self.full_text)
        self.unique_words= set([w for w in self.origin_words])
        self.words_num = len(self.unique_words)
        self.words_to_index = {w:i for i, w in enumerate(self.unique_words)}
        self.co_occ_dict = {w: [] for w in self.unique_words}
        self.p = np.zeros(self.words_num)


    def set_calculation_factors(self):
        ## set teleport vector    
        _pVec = np.zeros(self.words_num)
        for i, _w in enumerate(self.origin_words):
            #print(i, _w)
            _pVec[self.words_to_index[_w]] += float(1 / (i+1))

            ## sarch co-occurrence words
            self.search_words_within_window(i, _w)

        ## set adjacency matrix
        _w2id = self.words_to_index
        _M_org = np.zeros((self.words_num, self.words_num))
        for _w, _list in self.co_occ_dict.items():
            _cnt = Counter(_list)
            for _word ,_frq in _cnt.most_common():
                _M_org[_w2id[_w]][_w2id[_word]] = _frq

        self.M = _M_org / _M_org.sum(axis=0)
        self.p = _pVec / _pVec.sum()
        self.s_vec = np.ones(self.words_num) / self.words_num

    
    def calculate(self):
        def total_weight(M, idx, s):
            return sum([(wij / M.sum(axis=0)[j]) * s[j] for j, wij in enumerate(M[idx]) if not wij == 0])

        _lamda = 1.0 # Threshold (inital value = 1.0)
        _cnt = 0

        ## Calculate word position rank
        while (_lamda > 0.001 or _cnt > 100): # end if previous setp diff below 0.001 
            _sVec_post = copy.deepcopy(self.s_vec)
            for i, (_p, _s) in enumerate(zip(self.p , self.s_vec)):
                _s_post = (1 - self.alpha) * _p + self.alpha * total_weight(self.M, i, self.s_vec)
                _sVec_post[i] = _s_post

            _lamda = np.linalg.norm(_sVec_post - self.s_vec)
            self.s_vec = _sVec_post
            _cnt+=1

        _word_with_score_list = [(word, self.s_vec[self.words_to_index[word]]) for word in self.origin_words]
        
        ## Calculate phrage score
        for _p in self.phrase:
            _total_score = sum([self.s_vec[self.words_to_index[word]] for word in _p.split("_")])
            _word_with_score_list.append((_p, _total_score))

        _sorted_list = np.argsort([t[1] for t in _word_with_score_list])
        _key_words = []
        
        # ステミングした結果が同じ単語の排除
        _stem_key_words = []
        for idx in reversed(_sorted_list):
            _key_word = _word_with_score_list[idx][0]
            _stem_key_word = " ".join([word for word in _key_word.split("_")])
            if not _stem_key_word in _stem_key_words:
                _key_words.append(_key_word)
                _stem_key_words.append(_stem_key_word)
            
            if len(_key_words) >= self.extract_num:
                break

        return _key_words
    
    def execute(self):
        self.split_words()
        self.set_calculation_factors()
        return self.calculate()