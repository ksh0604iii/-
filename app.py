import streamlit as st
import yfinance as yf
import requests
from datetime import datetime

# --- 설정 정보 ---
NAVER_CLIENT_ID = "GEGReBLC7buyb0JtGdvJ"
NAVER_CLIENT_SECRET = "y_rE3jsDV5"
KEYWORDS = ["비트코인", "나스닥", "이더리움", "삼성전자"]

st.set_page_config(page_title="통합 투자 대시보드", layout="wide")

# --- 1. 기업 정밀 분석 및 점수 산출 함수 ---
def evaluate_stock(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        score = 0
        
        # PER 점수 (최대 20점)
        per = info.get('trailingPE', 100)
        if per < 5: score += 20
        elif per < 8: score += 15
        elif per < 10: score += 10
        else: score += 5
        
        # PBR 점수 (최대 20점)
        pbr = info.get('priceToBook', 100)
        if pbr < 0.3: score += 5
        elif pbr < 0.6: score += 4
        elif pbr < 1.0: score += 3
        
        # 배당 수익률 (최대 10점)
        div = (info.get('dividendYield', 0) or 0) * 100
        if div > 7: score += 10
        elif div > 5: score += 7
        elif div > 3: score += 5
        
        return score, per, pbr, div, info
    except: return None, None, None, None, None

# --- 2. 실시간 뉴스 수집 함수 ---
def get_naver_news(kw):
    url = f"https://openapi.naver.com/v1/search/news.json?query={kw}&display=8&sort=date"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    try:
        res = requests.get(url, headers=headers)
        return res.json().get('items', [])
    except: return []

# --- [섹션 1] 기업 정밀 분석 ---
st.title("🏛️ 통합 투자 대시보드")
st.subheader("🔍 사용자 기준 종목 가치 평가")
ticker_input = st.text_input("분석할 티커 입력 (예: 005930.KS, AAPL)", "")

if st.button("🚀 정밀 분석 및 점수 산출"):
    score, per, pbr, div, raw_info = evaluate_stock(ticker_input)
    if score is not None:
        # 등급 판정
        if score > 80: grade, desc, color = "🥇 A등급", "장기투자 적합 적극매수", "green"
        elif score >= 70: grade, desc, color = "🥈 B등급", "장기투자 적합 매수 고려", "blue"
        elif score >= 50: grade, desc, color = "🥉 C등급", "장기투자 유지(홀딩)", "orange"
        else: grade, desc, color = "💀 D등급", "절대 하지마", "red"
        
        st.header(f"분석 결과: :{color}[{grade}]")
        st.info(f"**총점: {score}점** | **투자 전략:** {desc}")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("PER", f"{per:.2f}")
        c2.metric("PBR", f"{pbr:.2f}")
        c3.metric("배당수익률", f"{div:.2f}%")
    else:
        st.error("티커를 확인해주세요. (한국 주식은 .KS 또는 .KQ를 붙여야 합니다)")

st.divider()

# --- [섹션 2] 실시간 뉴스 리스트 ---
st.subheader("📰 실시간 관심 테마 뉴스")
if 'news_store' not in st.session_state:
    st.session_state.news_store = {kw: [] for kw in KEYWORDS}

if st.button('🔄 전체 뉴스 새로고침'):
    with st.spinner('뉴스를 수집 중...'):
        for kw in KEYWORDS:
            st.session_state.news_store[kw] = get_naver_news(kw)
    st.success("업데이트 완료!")

tabs = st.tabs(KEYWORDS)
for i, kw in enumerate(KEYWORDS):
    with tabs[i]:
        items = st.session_state.news_store.get(kw, [])
        for item in items:
            title = item['title'].replace("<b>","").replace("</b>","").replace("&quot;", '"')
            st.markdown(f"📍 [{title}]({item['link']})")
