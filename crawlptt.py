from re import findall
import re
import requests
from bs4 import BeautifulSoup
import json
import random
from html import unescape
import time

def crawl(name):
    ptt='https://www.ptt.cc/bbs/NTUcourse/search?q='+name
    header={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0'}
    
    # -------------------------
    # 取得搜尋結果文章連結
    # -------------------------
    respond=requests.get(ptt,headers=header)
    with open('output.html','w',encoding='utf-8') as f:
        f.write(respond.text)
        
    soup=BeautifulSoup(respond.text,'html.parser')
    articals= soup.find_all('div',class_='r-ent')
    alllink=[]
    for a in articals: 
        title=a.find("div",class_='title') 
        if title and title.a:
            title= title.a
            link = "https://www.ptt.cc" + title['href']
            alllink.append(link)
            
    with open('ptt_ntu.json','w',encoding='utf-8') as file:
        json.dump(alllink,file,ensure_ascii=False,indent=4)
        
    with open('ptt_ntu.json','r',encoding='utf-8') as file:
        http=json.load(file) # http 就是 alllink
        
    content2=[] # 存放所有推文/留言
    
    # -------------------------
    # 逐篇爬取推文/留言
    # -------------------------
    for i in range (len(http)):
        time.sleep(0.5)
        ptt=http[i]
        header={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0'}
        respond=requests.get(ptt,headers=header)
        
        # 由於我們只取推文，這裡不需要寫入 '評價x.html'，但如果您的流程需要，您可以保留
        # with open('評價'+str(i)+'.html','w',encoding='utf-8') as f:
        #     f.write(respond.text)
            
        soup=BeautifulSoup(respond.text,'html.parser')
        
        # ⭐ 關鍵：只找 div class="push" (推文區塊)
        content=soup.find_all('div',class_='push')
        
        for push in content:
            # 獲取推文標籤 (例如：'推', '噓', '→')
            tag=push.find('span', class_='push-tag')
            tag=unescape(tag.get_text()) if tag else ''
            
            # 獲取推文內容
            content1_tag = push.find('span', class_='f3 push-content')
            
            if content1_tag:
                # 清除推文內容前的冒號與空白
                content1 = content1_tag.get_text().lstrip(': ').strip()
            else:
                continue

            # 沿用您的原始邏輯：將連續的 '→' 合併到上一則評論
            if tag.strip() == '→' and content2:
                content2[-1] += content1
            elif content1:
                content2.append(content1)
                
    # 輸出並回傳
    with open('評價.json','w',encoding='utf-8') as file:
        json.dump(content2,file,ensure_ascii=False,indent=4)
        
    return content2 # 確保回傳給 app.py 使用