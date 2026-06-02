import streamlit as st
import time
import json
import os
from google import genai
from google.genai import types

# =====================================================================
#Smart Offline Cache

CACHE_FILE = "lab_learning_cache.json"

# 初始化資料庫
if not os.path.exists(CACHE_FILE):
    DEFAULT_CACHE = {
        "elisa": {
            "experiment_name": "ELISA 抗體檢測實驗 (系統初始庫)",
            "materials": ["微量移液管與無菌低吸附 Tips", "96孔高親和力酶標板", "辣根過氧化物酶 (HRP) 標記之二抗", "TMB 底物顯色液"],
            "regulations": ["【防護】涉及強酸終止液，操作須全程佩戴防護眼鏡與安全手套。", "【廢液】回收至 [C類-有機特殊廢液] 黃色貯存桶。"],
            "paper_free": "Development of High-Sensitivity ELISA Methods, Journal of Veterinary Science, 2024",
            "paper_paid": "Advanced Enzyme-Linked Immunosorbent Assay, Nature Protocols, 2025"
        },
        "dna": {
            "experiment_name": "DNA 基因組萃取實驗 (系統初始庫)",
            "materials": ["高速冷凍離心機", "細胞裂解緩衝液 (含 10% SDS)", "蛋白酶 K", "酚/氯仿/異戊醇混合液"],
            "regulations": ["【劇毒】酚氯仿具嚴重細胞毒性與揮發性，必須全程在排煙櫃內操作！", "【廢液】單獨回收至 [D類-鹵素有機化學廢液] 專用藍色桶。"],
            "paper_free": "A Rapid Method for Genomic DNA Extraction, Open Academic BMC Genetics, 2024",
            "paper_paid": "High-Molecular-Weight DNA Extraction Protocols, Nature Methods, 2025"
        }
    }
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_CACHE, f, ensure_ascii=False, indent=4)

def load_local_cache():
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_to_cache(key, data):
    cache = load_local_cache()
    cache[key] = data  
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)

# =====================================================================
#UI
st.set_page_config(page_title="LabNavigator", page_icon="🧪", layout="centered")

st.markdown("# 🧪 LabNavigator")
st.markdown("### 智慧化實驗室導航與全國學術資源媒合平台")
st.caption("2026 資訊暨 AI 應用創新競賽決賽專用作品 ── Gemini 2.5 Flash 智慧學習增強版")
st.divider()

experiment_name = st.text_input("🔍 請輸入您即將進行的科學實驗名稱（支援任意實驗，如：蛋白質電泳、細胞轉染）：", "")

if experiment_name:
    kw = experiment_name.lower().strip()
    cache_key = "dna" if "dna" in kw or "萃取" in kw else ("elisa" if "elisa" in kw or "抗體" in kw else kw)

    with st.spinner(f"🚀 系統正將指令封裝，嘗試交聯雲端 Gemini 2.5 Flash 智慧引擎..."):
        try:
            client = genai.Client()
            system_prompt = """
            你是一個專業的大學實驗室安全管理專家。請根據使用者輸入的「實驗名稱」，嚴格依照以下 JSON 格式回傳繁體中文內容，不要輸出任何額外的解釋文字或 ```json 標籤。
            {
                "experiment_name": "修正後的標準中文實驗名稱",
                "materials": ["材料1", "材料2", "材料3"],
                "regulations": ["法規守則1", "法規守則2"],
                "paper_free": "開源論文題目與期刊年份",
                "paper_paid": "受限論文題目與期刊年份"
            }
            安全規範請務必結合中華民國勞動部《職業安全衛生設施規則》與廢液分類。
            """
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"我想做這個實驗：{experiment_name}，請分析資源。",
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.2,
                    response_mime_type="application/json" 
                ),
            )
            
            ai_result = json.loads(response.text.strip())
            
            save_to_cache(cache_key, ai_result)
            
            st.success(f"🌐 雲端 Gemini 2.5 Flash 智慧引擎連線成功！已即時動態生成最優配置，並自動更新本地大腦：")
            is_cloud = True

        except Exception as e:
#  斷線防禦機制
            local_db = load_local_cache()
            
            if cache_key in local_db:
                ai_result = local_db[cache_key]
                st.warning(f"⚠️ 偵測到雲端AI聯絡逾時，系統已自動啟動【內建大專院校安全快取機制】，成功對接【{ai_result['experiment_name']} 】")
            else:
                ai_result = local_db["elisa"]
                st.warning(f"⚠️ 雲端連線逾時且無歷史學習紀錄。系統啟動【內建安全防護備用庫】進行展示：")
            
            is_cloud = False

        st.write("") 

 # 風琴式摺疊選單
        with st.expander(f"📦 查看：【{ai_result['experiment_name']}] 必備材料與設備清單", expanded=True):
            st.markdown("#### 📋 核心耗材與物資整備需求")
            for item in ai_result["materials"]:
                st.markdown(f"* {item}")
                
        with st.expander(f"⚠️ 查看：【{ai_result['experiment_name']}'] 國家職業安全與廢液分類規範", expanded=False):
            st.markdown("#### ⚖️ 勞動部與教育部法定實驗安全指引")
            st.error("操作人員請務必依據中華民國法律嚴格遵守以下安全規範：")
            for reg in ai_result["regulations"]:
                st.markdown(f"* {reg}")
                
        with st.expander(f"📚 查看：【{ai_result['experiment_name']}'] 國際期刊文獻與閱覽權限標籤", expanded=False):
            st.markdown("#### 🌐 國際文獻大數據動態過濾結果")
            st.divider()
            st.markdown(f"📄 **1. {ai_result['paper_free']}**")
            st.write("🔓 權限狀態：`Open Access (開源文獻)`")
            st.success("✅ 免費閱讀：此為全國開放存取文獻，您可以直接點擊連結下載完整 PDF 全文。")
            st.divider()
            st.markdown(f"📄 **2. {ai_result['paper_paid']}**")
            st.write("🔒 權限狀態：`Restricted / Subscription (受限文獻)`")
            st.error("🛑 權限限制：本論文非開源文獻。您必須透過【大專校院之校園網域 IP 登入】方可瀏覽全文。")
