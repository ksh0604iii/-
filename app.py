import streamlit as st
import yfinance as yf
import requests
import pandas as pd
from deep_translator import GoogleTranslator

# --- 기본 설정 ---
NAVER_ID = "GEGReBLC7buyb0JtGdvJ"
NAVER_SECRET = "y_rE3jsDV5"
KEYWORDS = ["비트코인", "나스닥", "이더리움", "삼성전자"]

st.set_page_config(page_title="글로벌 가치투자 대시보드", layout="wide")

# --- 종목 분석 함수 ---
def get_report(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        score = 0
        per = info.get('trailingPE', 100)
        pbr = info.get('priceToBook', 100)
        div = (info.get('dividendYield', 0) or 0) * 100
        if per < 10: score += 10 #
        if pbr < 1.0: score += 5  #
        if div > 3: score += 5    #
        grade = "🥈 B (매수고려)" if score >= 15 else "💀 D (절대금지)"
        return {"티커": ticker, "점수": score, "등급": grade, "PER": round(per, 2), "PBR": round(pbr, 2), "배당": f"{div:.2f}%"}
    except: return None

# --- [새로운 방식] 뉴스 수집 함수 ---
def fetch_news_safe(kw):
    all_news = []
    # 1. 네이버 뉴스
    n_res = requests.get(f"https://openapi.naver.com/v1/search/news.json?query={kw}&display=3", 
                         headers={"X-Naver-Client-Id": NAVER_ID, "X-Naver-Client-Secret": NAVER_SECRET})
    for i in n_res.json().get('items', []):
        all_news.append({"t": i['title'].replace('<b>','').replace('</b>',''), "l": i['link'], "o": "네이버"})
    
    # 2. 구글 뉴스 (RSS 주소 방식 - 라이브러리 불필요)
    try:
        # 영문 뉴스 검색 결과를 직접 가져오기 위한 URL
        all_news.append({"t": f"🌐 [외신 원문보기] {kw} 최신 소식", "l": f"https://www.google.com/search?q={kw}&tbm=nws&lr=lang_en", "o": "구글외신"})
    except: pass
    return all_news

# --- 화면 구성 ---
st.title("🏛️ 글로벌 가치투자 올인원 대시보드")
t1, t2, t3 = st.tabs(["🎯 실시간 분석", "🚀 A-B등급 발굴", "📰 글로벌 뉴스"])

with t1:
    target = st.text_input("티커 입력 (예: AAPL)")
    if st.button("분석"): st.json(get_report(target))

with t2:
    if st.button("스캐너 실행"):
        s_list = ["005930.KS", "005490.KS", "KO", "VZ", "T"]
        st.table([get_report(t) for t in s_list if get_report(t)])

with t3:
    if st.button("뉴스 새로고침"):
        for kw in KEYWORDS:
            st.write(f"### 🔥 {kw} 리포트")
            for n in fetch_news_safe(kw):
                st.markdown(f"📍 [{n['o']}] [{n['t']}]({n['l']})")

