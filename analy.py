# 文件名稱：analy.py (已移除所有 print 語句)
from re import findall

import requests
from bs4 import BeautifulSoup
import json
import random
from html import unescape
import time
import random
from tabulate import tabulate 

def analy(name):
    goodword=['推','讚','愛']
    badword=['雷','不推','爛']
    comment=[];good=0;sweet=0;bad=0;NotSweet=0
    # 嘗試打開爬蟲輸出的評價.json
    try:
        with  open('評價.json','r',encoding='utf-8') as f:
                comment=json.load(f)
    except FileNotFoundError:
        return False

    if len(comment)==0:
        return False
    else:
        for i in comment:
            for j in goodword:
                if j in i:
                    good+=1
                    break
            if '甜' in i:
                    sweet+=1
            for k in badword:
                if k in i:
                    bad+=1
                    break
            if '不甜' in i:
                    sweet-=1
                    NotSweet+=1
        
        # 組裝所有分析結果，以 Tuple 形式回傳給 app.py (這是比較功能需要的數據)
        return (
            name,
            len(comment),
            good,
            good/len(comment), # 推比率
            sweet,
            sweet/len(comment), # 甜比率
            bad,
            bad/len(comment),
            NotSweet,
            NotSweet/len(comment)
        )