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
        # 데이터가 비어있는 경우를 대비한 방어 로직
        if not info or 'trailingPE' not in info:
            return None
            
        score = 0
        per = info.get('trailingPE', 100)
        pbr = info.get('priceToBook', 100)
        div = (info.get('dividendYield', 0) or 0) * 100
        
        if per < 10: score += 10 #
        if pbr < 1.0: score += 5  #
        if div > 3: score += 5    #
        
        grade = "🥈 B (매수고려)" if score >= 15 else "💀 D (절대금지)"
        return {"티커": ticker, "점수": score, "등급": grade, "PER": round(per, 2), "PBR": round(pbr, 2), "배당": f"{div:.2f}%"}
    except: 
        return None

# --- 뉴스 수집 함수 ---
def fetch_news_safe(kw):
    all_news = []
    try:
        n_res = requests.get(f"https://openapi.naver.com/v1/search/news.json?query={kw}&display=3", 
                             headers={"X-Naver-Client-Id": NAVER_ID, "X-Naver-Client-Secret": NAVER_SECRET})
        for i in n_res.json().get('items', []):
            all_news.append({"t": i['title'].replace('<b>','').replace('</b>',''), "l": i['link'], "o": "네이버"})
        
        all_news.append({"t": f"🌐 [외신 원문보기] {kw} 최신 소식", "l": f"https://www.google.com/search?q={kw}&tbm=nws&lr=lang_en", "o": "구글외신"})
    except: pass
    return all_news

# --- 화면 구성 ---
st.title("🏛️ 글로벌 가치투자 올인원 대시보드")
t1, t2, t3 = st.tabs(["🎯 실시간 분석", "🚀 A-B등급 발굴", "📰 글로벌 뉴스"])

with t1:
    st.subheader("🔍 종목 정밀 진단")
    target = st.text_input("분석할 티커 (예: AAPL, 005930.KS)")
    if st.button("분석 실행"):
        with st.spinner('데이터를 분석 중입니다...'):
            data = get_report(target)
            if data:
                st.success(f"✅ {target} 분석 완료!")
                st.write(f"### 최종 등급: {data['등급']}")
                st.json(data) # 정상 데이터일 때만 출력
            else:
                st.error("데이터를 불러오지 못했습니다. 티커가 정확한지 확인해 주세요.")

with t2:
    st.subheader("🚀 가치주 자동 스캐너")
    if st.button("스캐너 실행"):
        s_list = ["005930.KS", "005490.KS", "KO", "VZ", "T", "JPM"]
        results = [get_report(t) for t in s_list if get_report(t)]
        if results:
            st.table(pd.DataFrame(results))

with t3:
    st.subheader("📰 실시간 글로벌 뉴스")
    if st.button("뉴스 새로고침"):
        for kw in KEYWORDS:
            st.write(f"### 🔥 {kw} 리포트")
            for n in fetch_news_safe(kw):
                st.markdown(f"📍 [{n['o']}] [{n['t']}]({n['l']})")

