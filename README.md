# 論文のパーサー
## 引数
`python .\main.py -s 2 -t 6  -u 33:62 -e -p`
* -e : pdf を切り分ける処理をするか?
    * -s 2 : 何枚組の用紙か(2枚要旨なら)
    * -t 6 : ヘッダーのページ数(頭6ページを読み飛ばす)
    * -u 33:62 : 中間と無視するページ(:区切り=33と62ページを無視)
* -p : 論文パースをするか
 
## TODO
* 2段組みの判定
  * https://juu7g.hatenablog.com/entry/Python/PDF/program
* postion rank の前処理
  * 絞る(数字のみを避ける、図-1みたいのをいれない)
* 最初の情報の読み取り制度向上




## setup linux
```bash
# anaconda
wget https://repo.anaconda.com/archive/Anaconda3-2023.03-1-Linux-x86_64.sh
bash Anaconda3-2022.05-Linux-x86_64.sh
sudo reboot

# mecab
sudo apt install mecab mecab-ipadic-utf8 libmecab-dev swig
git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git

conda create -n dev python=3.10
conda activate dev
pip install mecab-python3 pdfminer pypdf pypdf

# mecab error: [ifs] no such file or directory: /usr/local/etc/mecabrc
#  sudo cp /etc/mecabrc /usr/local/etc/

```