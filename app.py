# 文件名稱：app.py (包含單一查詢和比較功能)
import streamlit as st
import crawlptt       # 爬蟲程式
import analy          # PTT 評論分析程式
import excel_tool     # Excel 成績查詢程式
import crawlpttcontent # 匯入文章內容爬蟲
import time 
import requests 
import pandas as pd
import numpy as np
import random

# 網站標題與設定
st.set_page_config(layout="centered")
st.title("🎓 台大教授評價與成績彙整生成器")

st.markdown("##### 請輸入教授姓名，系統將為您彙整評價與成績數據。")

# 設置兩個輸入框 (主查詢和比較對象)
col_main, col_compare = st.columns(2)
with col_main:
    professor_input = st.text_input("輸入第一個教授名字 (主查詢):", key="prof1")
with col_compare:
    professor_compare_input = st.text_input("輸入第二個教授名字 (比較對象，可選):", key="prof2")


# 文件名稱：app.py (get_professor_review 函數內部)
# 文件名稱：app.py (get_professor_review 函數內部)
import random # <--- ⭐ 確保 app.py 頂部有此行

def get_professor_review(professor_name):
    """
    執行爬蟲、分析、和 Excel 查詢，回傳顯示用的 dict 和原始數據 tuple。
    同時加入了安全取樣邏輯，用於顯示隨機評論範例。
    """
    if not professor_name:
        return None, None
    
    ptt_result_tuple = None
    
    # --- 1. 執行 PTT 爬蟲與分析 ---
    try:
        # 爬蟲現在必須回傳所有評論列表 (all_comments)
        all_comments = crawlptt.crawl(professor_name) 
        
        # 爬取文章內容並儲存為 TXT
        crawlpttcontent.crawlcontent(professor_name) 

        # 分析數據 (回傳統計結果的 Tuple)
        ptt_result_tuple = analy.analy(professor_name)
        
        # 檢查是否有分析結果 (例如：查無評論)
        if ptt_result_tuple is False:
            # 即使分析無果，我們仍可以嘗試回傳成績數據（如果成績找到了的話）
            # 但為了保持數據完整性，這裡依舊回傳 None/False 讓單一查詢顯示錯誤訊息
            return None, False

        # ------------------------------------------------
        # ⭐ 關鍵：安全取樣邏輯
        # ------------------------------------------------
        if not all_comments:
            sample_comments = [] # 評論為空，回傳空列表
        else:
            # 隨機選取 5 則評論作為範例 (如果評論數不足 5 則，則全部選取)
            # 這是防止 random.sample 在評論數少於 k 時報錯的關鍵
            sample_comments = random.sample(all_comments, min(20, len(all_comments)))
        
        # --- 2. 執行 Excel 成績查詢 ---
        grade_msg = excel_tool.search_grade(professor_name)
        
        # --- 3. 整理數據 ---
        data_dict = {
            "name": ptt_result_tuple[0],
            "total_count": ptt_result_tuple[1],
            "good_count": ptt_result_tuple[2],
            "good_ratio": f"{ptt_result_tuple[3]*100:.1f}%",
            "sweet_count": ptt_result_tuple[4],
            "sweet_ratio": f"{ptt_result_tuple[5]*100:.1f}%",
            "bad_count": ptt_result_tuple[6],
            "bad_ratio": f"{ptt_result_tuple[7]*100:.1f}%",
            "notsweet_count": ptt_result_tuple[8],
            "notsweet_ratio": f"{ptt_result_tuple[9]*100:.1f}%",
            "grade_msg": grade_msg,
            "sample_comments": sample_comments # ⭐ 新增：傳遞隨機選取的評論
        }
        
        return data_dict, ptt_result_tuple
        
    except Exception as e:
        # 在開發階段，可以將 st.error 改為 st.exception 來顯示完整的錯誤堆棧
        # st.error(f"查詢過程中發生錯誤: {e}")
        return None, None

def display_single_review(review_data):
    """
    在 Streamlit 介面上顯示單一教授的詳細分析結果。
    新增了部分評論範例顯示。
    """
    if not review_data:
        st.error("❌ 查無相關資訊，請確認輸入是否正確，或爬蟲程式執行失敗。")
        return

    st.subheader(f"📊 『{review_data['name']}』教授評價彙整")
    
    # 顯示核心數據
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(label="總評價數", value=review_data['total_count'])
    with col2:
        st.metric(label="推 次數", value=review_data['good_count'], delta=review_data['good_ratio'])
    with col3:
        st.metric(label="甜 次數", value=review_data['sweet_count'], delta=review_data['sweet_ratio'])
    with col4:
        st.metric(label="不推 次數", value=review_data['bad_count'], delta=review_data['bad_ratio'], delta_color="inverse")
    with col5:
        st.metric(label="不甜 次數", value=review_data['notsweet_count'], delta=review_data['notsweet_ratio'], delta_color="inverse")
        
    st.markdown("---")
    
    # ⭐ 新增：顯示部分評論
    if review_data.get('sample_comments'): # 使用 .get() 確保安全取值
        st.subheader("💬 部分評論範例 (前 20 則)")
        # 遍歷前 5 則評論
        for i, comment in enumerate(review_data['sample_comments'][:20]): 
            # 確保評論非空
            if comment.strip(): 
                # 使用 Markdown 引用格式顯示評論
                # 只顯示前 100 個字，避免單則評論過長佔據太多空間
                st.markdown(f"> **{i+1}.** {comment[:100]}...") 
    else:
        st.info("查無 PTT 評論內容。")
        
    st.markdown("---")
    
    # 顯示成績數據
    st.subheader("📝 歷史課程 A+ 比例成績")
    st.text(review_data['grade_msg'])
    
    st.markdown("---")
    st.caption("🌐 資訊來源：PTT NTUcourse 板爬蟲 & 自行上傳之 Excel 成績單")
    st.success("📝 **文章原始內容已儲存**至應用程式根目錄下的 `articles/` 資料夾中。")


def display_comparison(prof1_raw, prof2_raw):
    """
    生成兩個教授的比較表格。
    """
    labels = ["名稱", "總評價數", "推 次數", "推 比率", "甜 次數", "甜 比率", "不推 次數", "不推 比率", "不甜 次數", "不甜 比率"]
    
    # 整理數據以便顯示 (將比率從浮點數轉為百分比字串)
    def format_raw(raw_tuple):
        if raw_tuple is False:
            return ["查無評論"] * len(labels)
        
        formatted = list(raw_tuple)
        # 格式化比率 (索引 3, 5, 7, 9)
        for i in [3, 5, 7, 9]:
            formatted[i] = f"{formatted[i]*100:.1f}%"
        return formatted

    prof1_formatted = format_raw(prof1_raw)
    prof2_formatted = format_raw(prof2_raw)

    # 建立 DataFrame
    data = {'指標': labels}
    data[prof1_formatted[0]] = prof1_formatted
    data[prof2_formatted[0]] = prof2_formatted
    
    # 移除名稱列
    data[prof1_formatted[0]].pop(0)
    data[prof2_formatted[0]].pop(0)
    data['指標'].pop(0)
    
    df = pd.DataFrame(data)
    df.set_index('指標', inplace=True)
    
    st.subheader("⚖️ 教授評價數據比較")
    st.table(df)


# --- 主執行區塊 ---
if st.button("🔍 開始查詢或比較"):
    prof1_name = professor_input.strip()
    prof2_name = professor_compare_input.strip()

    if not prof1_name:
        st.warning("請至少輸入第一個教授名字才能查詢喔！")
    else:
        # --- 處理單一查詢 ---
        if not prof2_name:
            with st.spinner(f"正在搜尋並分析 {prof1_name} 的評價與成績..."):
                prof1_data, prof1_raw = get_professor_review(prof1_name)
            
            if prof1_data:
                display_single_review(prof1_data)
            else:
                st.error("❌ 查無相關資訊，請確認輸入是否正確，或爬蟲程式執行失敗。")

        # --- 處理比較查詢 ---
        else:
            # 取得第一個教授數據
            with st.spinner(f"正在搜尋並分析 {prof1_name} 的評價與成績..."):
                 prof1_data, prof1_raw = get_professor_review(prof1_name)
                
            # 取得第二個教授數據
            with st.spinner(f"正在搜尋並分析 {prof2_name} 的評價與成績..."):
                 prof2_data, prof2_raw = get_professor_review(prof2_name)
            
            st.success("✅ 數據獲取完畢！正在生成比較表。")

            # 檢查數據是否完整
            if prof1_raw is None or prof2_raw is None:
                 st.error("❌ 至少有一位教授的查詢發生錯誤，無法進行比較。")
            elif prof1_raw is False and prof2_raw is False:
                 st.error("❌ 兩位教授皆查無 PTT 評論數據進行比較。")
            elif prof1_raw is False:
                 st.error(f"❌ 無法取得第一個教授 ({prof1_name}) 的 PTT 評論數據進行比較。")
            elif prof2_raw is False:
                 st.error(f"❌ 無法取得第二個教授 ({prof2_name}) 的 PTT 評論數據進行比較。")
            else:
                 display_comparison(prof1_raw, prof2_raw)
                 
            # 額外顯示第一個教授的成績資訊
            if prof1_data:
                st.markdown("---") # 分隔線
                st.subheader(f"📝 『{prof1_name}』教授成績資訊 (主查詢)")
                st.text(prof1_data['grade_msg'])
            
            # 顯示第二個教授的成績資訊  <-- 關鍵修改
            if prof2_data:
                st.markdown("---") # 分隔線
                st.subheader(f"📝 『{prof2_name}』教授成績資訊 (比較對象)")
                st.text(prof2_data['grade_msg'])