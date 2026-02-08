import streamlit as st
import yfinance as yf
import requests
import pandas as pd

# --- 설정 정보 ---
NAVER_CLIENT_ID = "GEGReBLC7buyb0JtGdvJ"
NAVER_CLIENT_SECRET = "y_rE3jsDV5"
# 사용자가 실시간으로 소식을 듣고 싶은 뉴스 키워드
NEWS_KEYWORDS = ["비트코인", "나스닥", "이더리움", "삼성전자"]

st.set_page_config(page_title="투자 전략 대시보드", layout="wide")

# --- 1. 점수 및 등급 산출 함수 (사용자 기준표 반영) ---
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
        if score > 80: grade = "A (적극매수)"
        elif score >= 70: grade = "B (매수고려)"
        elif score >= 50: grade = "C (홀딩)"
        else: grade = "D (절대금지)"
        
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

# --- 화면 레이아웃 구성 ---
st.title("🏛️ 가치투자 올인원 인텔리전스")

# 탭 구성: 분석기 / 자동 발굴 / 뉴스 알림
tab1, tab2, tab3 = st.tabs(["🎯 실시간 종목 분석", "🚀 A-B등급 자동 발굴", "📰 실시간 뉴스 수집"])

# [Tab 1: 개별 분석]
with tab1:
    st.subheader("🔍 특정 종목 정밀 진단")
    ticker_input = st.text_input("티커 입력 (예: 005930.KS, NVDA)", key
