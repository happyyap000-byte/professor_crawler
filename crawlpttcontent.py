import requests
from bs4 import BeautifulSoup
import time
import re
import os
import time
def crawlcontent(name):
    ptt = 'https://www.ptt.cc/bbs/NTUcourse/search?q=' + name
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0'
    }

    # -------------------------
    # 取得搜尋結果文章連結
    # -------------------------
    respond = requests.get(ptt, headers=header)
    soup = BeautifulSoup(respond.text, 'html.parser')
    articals = soup.find_all('div', class_='r-ent')

    alllink = []
    for a in articals:
        title = a.find("div", class_='title')
        if title and title.a:
            link = "https://www.ptt.cc" + title.a['href']
            alllink.append(link)

    # 建立資料夾
    if not os.path.exists("articles"):
        os.mkdir("articles")

    # -------------------------
    # 逐篇爬文章並輸出 txt
    # -------------------------
    for idx, url in enumerate(alllink):
        time.sleep(0.5)
        resp = requests.get(url, headers=header)
        soup = BeautifulSoup(resp.text, 'html.parser')

        # 讀 main-content
        main = soup.find('div', id='main-content')
        if not main:
            continue
        
        # ----------------------------------------------------
        # 移除了擷取文章標題的舊有邏輯，因為不再用於檔名
        # ----------------------------------------------------
        
        # 移除 PTT 作者、時間欄位
        for meta in main.find_all('div', class_='article-metaline'):
            meta.decompose()
        for meta in main.find_all('div', class_='article-metaline-right'):
            meta.decompose()

        # 移除留言
        content_div = main.find_all('div', class_='push')
        for push in content_div:
            push.decompose()
        
        # 取得文章純文字
        article_text = main.get_text().strip()
        
        # 寫入檔案
        if article_text:
            # ⭐ 關鍵修改：將檔名改為 教授名字_編號.txt
            # 使用 idx+1 從 1 開始編號，並使用 :02d 確保兩位數格式 (例如 01, 02)
            file_name = f"articles/{name}_{idx+1:02d}.txt"
            
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(article_text)