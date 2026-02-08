import streamlit as st
import yfinance as yf
import requests
import pandas as pd

# --- 설정 정보 ---
NAVER_CLIENT_ID = "GEGReBLC7buyb0JtGdvJ"
NAVER_CLIENT_SECRET = "y_rE3jsDV5"
NEWS_KEYWORDS = ["비트코인", "나스닥", "이더리움", "삼성전자"]

st.set_page_config(page_title="가치투자 올인원 대시보드", layout="wide")

# --- 1. 투자 점수 산출 함수 (사용자 점수표 이미지 기준 반영) ---
def get_investment_report(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        score = 0
        
        # PER 점수 (20점 만점)
        per = info.get('trailingPE', 100)
        if per < 5: score += 20
        elif per < 8: score += 15
        elif per < 10: score += 10
        else: score += 5
        
        # PBR 점수 (5점 만점)
        pbr = info.get('priceToBook', 100)
        if pbr < 0.3: score += 5
        elif pbr < 0.6: score += 4
        elif pbr < 1.0: score += 3
        
        # 배당 점수 (10점 만점)
        div = (info.get('dividendYield', 0) or 0) * 100
        if div > 7: score += 10
        elif div > 5: score += 7
        elif div > 3: score += 5
        
        # 등급 판정
        if score > 80: grade = "🥇 A (적극매수)"
        elif score >= 70: grade = "🥈 B (매수고려)"
        elif score >= 50: grade = "🥉 C (홀딩)"
        else: grade = "💀 D (절대금지)"
        
        return {"티커": ticker, "점수": score, "등급": grade, "PER": round(per, 2), "PBR": round(pbr, 2), "배당률": f"{div:.2f}%"}
    except:
        return None

# --- 2. 뉴스 수집 함수 ---
def get_naver_news(kw):
    url = f"https://openapi.naver.com/v1/search/news.json?query={kw}&display=8&sort=date"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    try:
        res = requests.get(url, headers=headers)
        return res.json().get('items', [])
    except: return []

# --- 3. 화면 구성 (탭 시스템) ---
st.title("🏛️ 가치투자 올인원 대시보드")
tab_anal, tab_scan, tab_news = st.tabs(["🎯 실시간 종목 분석", "🚀 A-B등급 자동 발굴", "📰 실시간 뉴스 수집"])

# [탭 1: 개별 분석]
with tab_anal:
    st.subheader("🔍 특정 종목 정밀 진단")
    t_input = st.text_input("분석할 티커 입력 (예: 005930.KS, NVDA)")
    if st.button("즉시 분석 실행"):
        res = get_investment_report(t_input)
        if res:
            st.metric("최종 등급", res['등급'])
            st.info(f"**총점:** {res['점수']}점 | **PER:** {res['PER']} | **PBR:** {res['PBR']}")
        else:
            st.error("티커를 확인해주세요.")

# [탭 2: 자동 발굴]
with tab_scan:
    st.subheader("🌟 오늘의 가치주 자동 발굴 (A, B등급)")
    m_choice = st.selectbox("스캔 시장 선택", ["국내 코스피 상위", "미국 나스닥 100"])
    
    if st.button("전 종목 스캔 시작"):
        # 스캔 후보군 리스트
        scan_list = ["005930.KS", "005490.KS", "055550.KS", "AAPL", "KO", "VZ", "T", "JPM", "PEP", "COST"]
        final_list = []
        
        with st.spinner('사용자님 기준에 맞는 유망주 찾는 중...'):
            for t in scan_list:
                data = get_investment_report(t)
                # A, B등급만 필터링 (70점 이상)
                if data and data['점수'] >= 70:
                    final_list.append(data)
        
        if final_list:
            st.success(f"조건을 만족하는 {len(final_list)}개의 종목을 찾았습니다!")
            st.table(pd.DataFrame(final_list))
        else:
            st.warning("현재 기준을 통과한 A, B등급 종목이 없습니다.")

# [탭 3: 뉴스 수집]
with tab_news:
    st.subheader("📰 관심 키워드 실시간 뉴스")
    if st.button('뉴스 새로고침'):
        for kw in NEWS_KEYWORDS:
            st.write(f"### {kw} 관련 소식")
            items = get_naver_news(kw)
            for i in items:
                title = i['title'].replace("<b>","").replace("</b>","").replace("&quot;", '"')
                st.markdown(f"📍 [{title}]({i['link']})")

