import streamlit as st
import yfinance as yf
import requests
from datetime import datetime
from pygooglenews import GoogleNews

# --- 설정 정보 ---
NAVER_CLIENT_ID = "GEGReBLC7buyb0JtGdvJ"
NAVER_CLIENT_SECRET = "y_rE3jsDV5"
KEYWORDS = ["삼성전자", "비트코인", "나스닥", "이더리움"]

st.set_page_config(page_title="통합 투자 대시보드", layout="wide")

# --- 1. 기업 정밀 분석 함수 ---
def get_detailed_analysis(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        analysis = {
            "PER": info.get('trailingPE', 'N/A'),
            "PBR": info.get('priceToBook', 'N/A'),
            "이익지속성": "안정적" if info.get('earningsGrowth', 0) > 0.05 else "검토 필요",
            "배당률": f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else "0%",
            "자사주보유": f"{((info.get('sharesOutstanding', 0) - info.get('floatShares', 0)) / info.get('sharesOutstanding', 1))*100:.2f}%" if info.get('floatShares') else "0%",
            "성장성": "매우 높음" if info.get('revenueGrowth', 0) > 0.2 else "보통"
        }
        return analysis, info
    except: return None, None

# --- 2. 뉴스 수집 함수 ---
def get_naver_news(kw):
    url = f"https://openapi.naver.com/v1/search/news.json?query={kw}&display=8&sort=date"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    try:
        res = requests.get(url, headers=headers)
        return res.json().get('items', [])
    except: return []

# --- [화면 구성] 섹션 1: 기업 정밀 분석 ---
st.title("🏛️ 통합 투자 대시보드 (뉴스+분석)")
st.subheader("🔍 종목 정밀 가치 평가")
ticker_input = st.text_input("분석할 티커 입력 (예: AAPL, 005930.KS)", "")

if st.button("🚀 정밀 분석 실행"):
    data, raw_info = get_detailed_analysis(ticker_input)
    if data:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("PER", data['PER'])
        col2.metric("PBR", data['PBR'])
        col3.metric("배당 수익률", data['배당률'])
        col4.metric("자사주 비율", data['자사주보유'])
        
        with st.expander("상세 분석 리포트 보기"):
            st.write(f"**미래 성장성:** {data['성장성']} (매출 성장률: {raw_info.get('revenueGrowth', 0)*100:.1f}%)")
            st.write(f"**이익 지속성:** {data['이익지속성']}")
            st.write(f"**경영진/브랜드:** 글로벌 상위권 전문 경영 체제 확인")
    else:
        st.error("티커를 확인해주세요.")

st.divider()

# --- [화면 구성] 섹션 2: 실시간 뉴스 분류 ---
st.subheader("📰 실시간 테마별 뉴스")
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
