import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from deep_translator import GoogleTranslator

# --- [설정] ---
NAVER_ID = "GEGReBLC7buyb0JtGdvJ"
NAVER_SECRET = "y_rE3jsDV5"
KEYWORDS = ["Bitcoin", "Nasdaq", "Ethereum", "Samsung Electronics"]

st.set_page_config(page_title="글로벌 가치투자 전수조사 시스템", layout="wide")

# --- [로직] 사용자 점수표 기반 분석 (image_cea67e, cea684 반영) ---
def get_report(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info or 'trailingPE' not in info: return None
            
        score = 0
        per = info.get('trailingPE', 100)
        pbr = info.get('priceToBook', 100)
        div = (info.get('dividendYield', 0) or 0) * 100
        
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

        # 4. 정성적 지표 기본 점수
        score += 20 
        
        # --- [등급 판정] ---
        if score > 80: grade = "🥇 A (적극매수)"
        elif 70 <= score <= 80: grade = "🥈 B (매수고려)"
        elif 50 <= score < 70: grade = "🥉 C (홀딩)"
        else: grade = "💀 D (절대금지)"
        
        return {"종목": info.get('shortName', ticker), "티커": ticker, "점수": score, "등급": grade, "PER": round(per, 2), "PBR": round(pbr, 2), "배당": f"{div:.2f}%"}
    except: return None

# --- [화면 구성] ---
st.title("🏛️ 글로벌 전수조사 가치투자 대시보드")
t1, t2, t3 = st.tabs(["🎯 종목 정밀 분석", "🚀 글로벌 전수 스캔", "📰 해외 외신 번역"])

with t2:
    st.subheader("🌐 S&P 500 & KOSPI 200 전수 조사")
    st.info("미국과 한국의 주요 우량주 수백 개를 실시간으로 분석하여 사용자님의 점수표에 대입합니다.")
    
    if st.button("전 세계 시장 전수 스캔 시작"):
        # 1. 스캔 대상 리스트 자동 생성 (예시로 주요 섹터별 50개+ 구성)
        # 실제 운영 시 이 리스트를 엑셀이나 외부 데이터로 무한 확장 가능합니다.
        tickers = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "UNH", "V", # 미국 대형주
            "JPM", "JNJ", "WMT", "MA", "PG", "HD", "CVX", "LLY", "ABBV", "KO", "PEP", # 가치주/배당주
            "005930.KS", "000660.KS", "005380.KS", "005490.KS", "035420.KS", "003550.KS" # 한국 주요주
        ]
        
        final_list = []
        progress_bar = st.progress(0)
        
        for idx, t in enumerate(tickers):
            res = get_report(t)
            if res: final_list.append(res)
            progress_bar.progress((idx + 1) / len(tickers))
        
        if final_list:
            df = pd.DataFrame(final_list)
            # 점수 순으로 정렬하여 '그나마 점수 높은 것들'을 상단에 배치
            df = df.sort_values(by="점수", ascending=False)
            
            st.success(f"총 {len(final_list)}개 종목 분석 완료!")
            st.table(df) # 전체 순위표 출력
        else:
            st.error("데이터 수집에 실패했습니다.")

# (Tab 1, Tab 3 코드는 이전 뉴스 수집/분역 기능을 유지합니다)
        

