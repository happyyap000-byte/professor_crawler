# 檔案：tools/excel_tool.py

import pandas as pd
import glob
import os

# --- 設定 Excel 欄位名稱 (請確保妳的 Excel 標題與此一致) ---
PROFESSOR_COL = '授課教師'
COURSE_COL = '課程名稱'
RATIO_COL = 'A+比例'
# -------------------------------------------------------------

def search_grade(professor_name):
    """
    搜尋所有 grades_*.xlsx 檔案，合併資料，並根據教授姓名查找 A+ 比例。
    """
    # 1. 資料讀取與合併
    try:
        # 找出所有符合 'grades_*.xlsx' 規則的檔案
       all_files = glob.glob("grades_*.csv")
        
        if not all_files:
            return ">> 錯誤：找不到任何 grades_*.xlsx 檔案。請確認它們在專案根目錄下。"
            
        all_data = [] # 儲存所有年份的資料表
        
        # print(f"✅ 找到 {len(all_files)} 個成績檔案，正在讀取...")
        
        for f in all_files:
            try:
                df = pd.read_csv(f, header=0)
                
                # 清理欄位名稱前後的空白 (避免 Excel 格式問題)
                df.columns = df.columns.str.strip() 

                # 提取年份資訊 (從檔名，例如 grades_2023.xlsx -> 2023)
                year = os.path.basename(f).split('_')[-1].split('.')[0]
                df['學年'] = year
                
                all_data.append(df)
            except KeyError as e:
                # 處理欄位名稱不符的錯誤
                return f"❌ 讀取檔案 {f} 失敗：欄位名稱錯誤。請確認標題是 {PROFESSOR_COL}, {COURSE_COL}, {RATIO_COL}。"
            except Exception as e:
                return f"❌ 讀取檔案 {f} 時發生錯誤: {e}"

        # 將所有 DataFrames 合併成一個總表
        df_combined = pd.concat(all_data, ignore_index=True)
        # print("✅ 所有成績資料合併完成。")
        
    except Exception as e:
        return f"總體資料讀取或合併發生錯誤：{e}"
    
    
    # 2. 搜尋與格式化輸出
    try:
        # 清理教授姓名欄位的空白，確保搜尋準確
        df_combined[PROFESSOR_COL] = df_combined[PROFESSOR_COL].astype(str).str.strip()
        
        # 使用 str.contains 模糊搜尋 (只要包含輸入的姓名就算找到)
        target = df_combined[df_combined[PROFESSOR_COL].str.contains(professor_name, na=False)] 

        if target.empty:
            return f"\n>> 查無『{professor_name}』教授的 A+ 比例資料 (Excel無紀錄)"

        # 格式化輸出
        result_msg = f"\n=== 『{professor_name}』教授歷年 A+ 比例資料 ===\n"
        
        # 讓最新的資料顯示在最前面
        target = target.sort_values(by=['學年'], ascending=False)
        
        for index, row in target.iterrows():
            course = row[COURSE_COL]
            score = row[RATIO_COL]
            year = row['學年'] 
            result_msg += f"學年：{year} | 課程：{course} | A+比例：{score}\n"
            
        result_msg += "========================================\n"
        return result_msg

    except Exception as e:
        return f"資料搜尋或格式化時發生錯誤：{e}"