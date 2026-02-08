import streamlit as st
import yfinance as yf
import requests
import pandas as pd
from deep_translator import GoogleTranslator

# --- 네이버/구글 설정은 이전과 동일 ---
NAVER_ID = "GEGReBLC7buyb0JtGdvJ"
NAVER_SECRET = "y_rE3jsDV5"
KEYWORDS = ["비트코인", "나스닥", "이더리움", "삼성전자"]

st.set_page_config(page_title="글로벌 가치투자 대시보드", layout="wide")

def get_report(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info: return None
            
        score = 0
        per = info.get('trailingPE', 100)
        pbr = info.get('priceToBook', 100)
        div = (info.get('dividendYield', 0) or 0) * 100
        
        # --- [정밀 점수 산출] ---
        # 1. PER 점수
        if per < 5: score += 20
        elif per < 8: score += 15
        elif per < 10: score += 10
        else: score += 5
        
        # 2. PBR 점수
        if pbr < 0.3: score += 5
        elif pbr < 0.6: score += 4
        elif pbr < 1.0: score += 3
        else: score += 0
        
        # 3. 배당 수익률 점수
        if div > 7: score += 10
        elif div > 5: score += 7
        elif div > 3: score += 5
        else: score += 2

        # 4. 정성적 지표 (자동 수집 불가 항목 - 기본값 부여)
        # 이익 지속성(5), 단독상장(5), 성장 잠재력(5), 경영자(5), 브랜드(0) 등 임시 합산
        score += 20 
        
        # --- [등급 판정] ---
        if score > 80: grade = "🥇 A (장기투자 적합 적극매수)"
        elif 70 <= score <= 80: grade = "🥈 B (장기투자 적합 매수 고려)"
        elif 50 <= score < 70: grade = "🥉 C (장기투자 유지/홀딩)"
        else: grade = "💀 D (절대 하지마)"
        
        return {"티커": ticker, "점수": score, "등급": grade, "PER": round(per, 2), "PBR": round(pbr, 2), "배당": f"{div:.2f}%"}
    except: return None

# --- 화면 출력 부분은 이전과 동일하게 유지 ---
st.title("🏛️ 글로벌 가치투자 올인원 대시보드")
t1, t2, t3 = st.tabs(["🎯 실시간 분석", "🚀 A-B등급 발굴", "📰 글로벌 뉴스"])

with t1:
    target = st.text_input("분석할 티커 (예: AAPL)")
    if st.button("즉시 분석"):
        data = get_report(target)
        if data:
            st.write(f"### 최종 등급: {data['등급']}")
            st.json(data)
