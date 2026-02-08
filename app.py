import streamlit as st
import yfinance as yf
import requests
import pandas as pd
from pygooglenews import GoogleNews
from deep_translator import GoogleTranslator # 안정적인 번역기로 교체

# --- 기본 설정 ---
NAVER_ID = "GEGReBLC7buyb0JtGdvJ"
NAVER_SECRET = "y_rE3jsDV5"
KEYWORDS = ["비트코인", "나스닥", "이더리움", "삼성전자"]

st.set_page_config(page_title="글로벌 가치투자 대시보드", layout="wide")

# --- 점수 산출 함수 (사용자 점수표 반영) ---
def get_report(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        score = 0
        per = info.get('trailingPE', 100)
        pbr = info.get('priceToBook', 100)
        div = (info.get('dividendYield', 0) or 0) * 100
        # 사용자 기준 반영
        if per < 10: score += 10
        if pbr < 1.0: score += 5
        if div > 3: score += 5
        grade = "🥈 B (매수고려)" if score >= 15 else "💀 D (절대금지)"
        return {"티커": ticker, "점수": score, "등급": grade, "PER": round(per, 2), "PBR": round(pbr, 2), "배당": f"{div:.2f}%"}
    except: return None

# --- 화면 구성 ---
st.title("🏛️ 글로벌 가치투자 올인원 대시보드")
t1, t2, t3 = st.tabs(["🎯 실시간 분석", "🚀 A-B등급 발굴", "📰 글로벌 뉴스"])

with t1:
    target = st.text_input("분석할 티커 (예: AAPL)")
    if st.button("분석 실행"):
        st.json(get_report(target))

with t2:
    if st.button("A-B등급 스캔 시작"):
        # 사용자 관심 종목 리스트
        s_list = ["005930.KS", "005490.KS", "KO", "VZ", "T", "JPM"]
        st.table([get_report(t) for t in s_list if get_report(t)])

with t3:
    if st.button("뉴스 새로고침"):
        for kw in KEYWORDS:
            st.write(f"### 🔥 {kw} 글로벌 소식")
            # 1. 네이버 뉴스 수집
            n_res = requests.get(f"https://openapi.naver.com/v1/search/news.json?query={kw}&display=3", 
                                 headers={"X-Naver-Client-Id": NAVER_ID, "X-Naver-Client-Secret": NAVER_SECRET})
            for i in n_res.json().get('items', []):
                st.markdown(f"📍 [국내] [{i['title'].replace('<b>','').replace('</b>','')}]({i['link']})")
            # 2. 해외 뉴스 수집 및 번역
            try:
                gn = GoogleNews(lang='en', country='US')
                for e in gn.search(kw).get('entries', [])[:2]:
                    # deep-translator로 번역 실행
                    tr = GoogleTranslator(source='en', target='ko').translate(e.title)
                    st.markdown(f"📍 [외신번역] [{tr}]({e.link})")
            except: pass

