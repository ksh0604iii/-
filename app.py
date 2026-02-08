import streamlit as st
import yfinance as yf
import requests
import pandas as pd
from pygooglenews import GoogleNews
from googletrans import Translator

# --- 네이버 API 정보 ---
NAVER_CLIENT_ID = "GEGReBLC7buyb0JtGdvJ"
NAVER_CLIENT_SECRET = "y_rE3jsDV5"
KEYWORDS = ["비트코인", "나스닥", "이더리움", "삼성전자"]

# 번역기 초기화 (세션 상태 유지)
if 'translator' not in st.session_state:
    st.session_state.translator = Translator()

st.set_page_config(page_title="글로벌 가치투자 대시보드", layout="wide")

# --- 종목 분석 및 등급 판정 로직 ---
def get_report(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        score = 0
        per = info.get('trailingPE', 100)
        pbr = info.get('priceToBook', 100)
        div = (info.get('dividendYield', 0) or 0) * 100
        
        # 이미지 기준 반영 점수 산출
        if per < 10: score += 10
        if pbr < 1.0: score += 5
        if div > 3: score += 5
        
        # 등급 판정
        if score >= 15: grade = "🥈 B (매수고려)"
        elif score >= 20: grade = "🥇 A (적극매수)"
        else: grade = "💀 D (절대금지)"
        
        return {"티커": ticker, "점수": score, "등급": grade, "PER": round(per, 2), "PBR": round(pbr, 2), "배당": f"{div:.2f}%"}
    except: return None

# --- 화면 구성: 탭 시스템 ---
st.title("🏛️ 글로벌 가치투자 올인원 대시보드")
tab_an, tab_sc, tab_nw = st.tabs(["🎯 실시간 분석", "🚀 A-B등급 발굴", "📰 글로벌 뉴스"])

with tab_an:
    st.subheader("🔍 특정 종목 정밀 진단")
    t_in = st.text_input("티커 입력 (예: AAPL, 005930.KS)")
    if st.button("분석 실행"):
        res = get_report(t_in)
        if res: st.json(res)

with tab_sc:
    st.subheader("🚀 가치주 자동 발굴")
    if st.button("스캔 시작"):
        s_list = ["005930.KS", "005490.KS", "KO", "VZ", "T", "JPM"]
        final = [get_report(t) for t in s_list if get_report(t) and get_report(t)['점수'] >= 15]
        if final: st.table(pd.DataFrame(final))

with tab_nw:
    st.subheader("🌎 해외 외신 번역 및 국내 뉴스")
    if st.button('뉴스 새로고침'):
        for kw in KEYWORDS:
            st.write(f"### 🔥 {kw} 리포트")
            # 네이버 뉴스
            n_res = requests.get(f"https://openapi.naver.com/v1/search/news.json?query={kw}&display=3", 
                                 headers={"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET})
            for item in n_res.json().get('items', []):
                st.markdown(f"📍 [네이버] [{item['title'].replace('<b>','').replace('</b>','')}]({item['link']})")
            # 구글 외신 번역
            gn = GoogleNews(lang='en', country='US')
            for entry in gn.search(kw).get('entries', [])[:2]:
                try:
                    tr = st.session_state.translator.translate(entry.title, dest='ko').text
                    st.markdown(f"📍 [해외번역] [{tr}]({entry.link})")
                except: pass


