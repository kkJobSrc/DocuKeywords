import MeCab
import re

tagger = MeCab.Tagger('-d /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd')


def detect_person_name(sentence):
    def empty_dict():
        return {"name":"", "aff":""}
    node = tagger.parseToNode(''.join(sentence.split())).next
    _f=False

    _authors = []
    _author=empty_dict()

    _name=""
    _aff =""
    while node:
        #print(node.surface, node.feature)
        _features = node.feature.split(",")
        if ("組織" in _features):
            _aff=node.surface
        if ("人名" in _features):
            if( "姓" in _features):
                _author["name"] = node.surface
            if(("名" in _features and _author["name"]) ):#or ("一般" in _features)):
                _author["name"] += node.surface
                if _aff: _author["aff"] += _aff              
                _authors.append(_author)
                _author=empty_dict()

        elif("名詞" in _features and _author["name"] ):
            _name += node.surface
            if _aff: _author["aff"] = _aff              
            _authors.append(_author)
            _author=empty_dict()

        if ( "名詞" in _features):
            pass#print(_features, node.surface)

        node = node.next

    return _authors

def extract_word_with_pos(sentence):
    _node = tagger.parseToNode(''.join(sentence.split())).next
    _words=[]
    while _node:
        _features = _node.feature.split(",")
        if(("名詞" in _features) or ("形容詞" in _features)):
            _words.append(_node.surface)
        _node = _node.next
    
    return _words

def tokenize(sentence):
    def isEmpyt(m):
        return ((m.split("\t")[0] == "EOS") or (m.split("\t")[0] == ""))

    def anonymizePos(pos):
        return "a" if pos == "形容詞" else "n" if pos=="名詞" else "o"

    _tokens = [(morph.split("\t")[0], morph.split("\t")[1].split(",")[0])
                for morph in tagger.parse(sentence).split("\n") if not isEmpyt(morph)]
    
    #print(_tokens)
    _pos_tags = [ anonymizePos(_t[1]) for _t in _tokens]
    _ptn = r"a*n+"

    _itr = re.finditer(_ptn, "".join(_pos_tags))
    #print(_pos_tags)
    _phrases = filter(lambda x: len(x) <= 3, [[_t[0] for _t in _tokens[_m.start():_m.end()]] for _m in _itr])
    _phrases = ["_".join(_p) for _p in _phrases]

    return [ _t[0] for _t in _tokens if _t[1] in ["形容詞","名詞"]], _phrases