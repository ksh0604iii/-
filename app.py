import streamlit as st
import yfinance as yf
import requests
import pandas as pd
from pygooglenews import GoogleNews
from googletrans import Translator

# --- 기본 설정 (본인의 API 정보를 입력하세요) ---
NAVER_CLIENT_ID = "GEGReBLC7buyb0JtGdvJ"
NAVER_CLIENT_SECRET = "y_rE3jsDV5"
KEYWORDS = ["비트코인", "나스닥", "이더리움", "삼성전자"]

# 번역기 초기화
if 'translator' not in st.session_state:
    st.session_state.translator = Translator()

st.set_page_config(page_title="글로벌 가치투자 대시보드", layout="wide")

# --- 1. 투자 점수 산출 로직 (사용자 이미지 기준 반영) ---
def get_investment_report(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        score = 0
        per = info.get('trailingPE', 100)
        pbr = info.get('priceToBook', 100)
        div = (info.get('dividendYield', 0) or 0) * 100
        
        if per < 10: score += 10 # PER 기준 점수
        if pbr < 1.0: score += 5 # PBR 기준 점수
        if div > 3: score += 5   # 배당 기준 점수
        
        if score >= 15: grade = "🥈 B (매수고려)"
        elif score >= 20: grade = "🥇 A (적극매수)" # 점수 체계에 따른 등급 판정
        else: grade = "💀 D (절대금지)"
        
        return {"티커": ticker, "점수": score, "등급": grade, "PER": round(per, 2), "PBR": round(pbr, 2), "배당률": f"{div:.2f}%"}
    except: return None

# --- 2. 통합 뉴스 수집 및 번역 함수 ---
def fetch_combined_news(kw):
    all_news = []
    # (1) 네이버 뉴스 수집
    n_url = f"https://openapi.naver.com/v1/search/news.json?query={kw}&display=3&sort=date"
    n_headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    try:
        res = requests.get(n_url, headers=n_headers)
        items = res.json().get('items', [])
        for item in items:
            title = item['title'].replace("<b>","").replace("</b>","")
            all_news.append({"title": title, "link": item['link'], "origin": "네이버"})
    except: pass

    # (2) 구글 해외 외신 번역 수집
    try:
        gn_en = GoogleNews(lang='en', country='US')
        en_entries = gn_en.search(kw).get('entries', [])[:2]
        for entry in en_entries:
            trans = st.session_state.translator.translate(entry.title, src='en', dest='ko')
            all_news.append({"title": f"[번역] {trans.text}", "link": entry.link, "origin": "해외외신"})
    except: pass
    return all_news

# --- 3. 화면 구성 (탭 시스템) ---
st.title("🏛️ 글로벌 가치투자 올인원 대시보드")
t1, t2, t3 = st.tabs(["🎯 실시간 종목 분석", "🚀 A-B등급 자동 발굴", "📰 글로벌 뉴스 수집"])

with t1:
    st.subheader("🔍 개별 종목 정밀 진단")
    target = st.text_input("분석할 티커 입력 (예: 005930.KS, AAPL)")
    if st.button("즉시 분석 실행"):
        res = get_investment_report(target)
        if res: st.json(res)
        else: st.error("티커를 확인해주세요.")

with t2:
    st.subheader("🌟 오늘의 유망 가치주 (A, B등급)")
    if st.button("시장 전체 스캔 시작"):
        scan_list = ["005930.KS", "005490.KS", "KO", "VZ", "T", "JPM", "PEP"]
        final = []
        with st.spinner('사용자 기준에 맞는 종목 찾는 중...'):
            for t in scan_list:
                data = get_investment_report(t)
                if data and data['점수'] >= 15: final.append(data)
        if final: st.table(pd.DataFrame(final))
        else: st.warning("현재 기준을 통과한 A-B등급 종목이 없습니다.")

with t3:
    st.subheader("📰 국내외 주요 뉴스 통합")
    if st.button('모든 뉴스 새로고침'):
        with st.spinner('해외 뉴스 번역 및 수집 중...'):
            for kw in KEYWORDS:
                st.write(f"### 🔥 {kw} 관련 리포트")
                news_list = fetch_combined_news(kw)
                for n in news_list:
                    st.markdown(f"📍 [{n['origin']}] [{n['title']}]({n['link']})")


