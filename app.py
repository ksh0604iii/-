import streamlit as st
import yfinance as yf
import pandas as pd

# --- 사용자 점수 산출 로직 (이미지 기준 완벽 반영) ---
def get_investment_grade(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        score = 0
        
        # PER 점수
        per = info.get('trailingPE', 100)
        if per < 5: score += 20
        elif per < 8: score += 15
        elif per < 10: score += 10
        else: score += 5
        
        # PBR 점수
        pbr = info.get('priceToBook', 100)
        if pbr < 0.3: score += 5
        elif pbr < 0.6: score += 4
        elif pbr < 1.0: score += 3
        
        # 배당 점수
        div_yield = (info.get('dividendYield', 0) or 0) * 100
        if div_yield > 7: score += 10
        elif div_yield > 5: score += 7
        elif div_yield > 3: score += 5
        
        return {"티커": ticker, "점수": score, "PER": round(per, 2), "PBR": round(pbr, 2), "배당": f"{div_yield:.2f}%"}
    except: return None

st.title("🏛️ 가치투자 올인원 대시보드")
tab1, tab2, tab3 = st.tabs(["🎯 실시간 분석", "📰 테마 뉴스", "🏆 A-B등급 자동 스캐너"])

with tab1:
    st.subheader("🔍 개별 종목 정밀 진단")
    # (기존 개별 분석 코드 위치)

with tab2:
    st.subheader("📰 실시간 관심 테마 뉴스")
    # (기존 뉴스 탭 코드 위치)

with tab3:
    st.header("🌟 가치주 자동 발굴기")
    market_choice = st.radio("스캔할 시장을 선택하세요", ["한국 (코스피 상위)", "미국 (나스닥 100)"])
    
    if st.button("🚀 스캔 시작"):
        # 시장별 대표 티커 리스트 (서버 부하 방지를 위해 주요 종목부터 시작)
        if market_choice == "한국 (코스피 상위)":
            tickers = ["005930.KS", "000660.KS", "005380.KS", "035420.KS", "005490.KS", "055550.KS"]
        else:
            tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "PEP", "COST"]
            
        results = []
        progress_bar = st.progress(0)
        
        for i, t in enumerate(tickers):
            data = get_investment_grade(t)
            if data and data['점수'] >= 15: # 사용자님의 B등급 수준으로 필터링
                results.append(data)
            progress_bar.progress((i + 1) / len(tickers))
            
        if results:
            df = pd.DataFrame(results)
            st.table(df.sort_values(by="점수", ascending=False))
            st.success("✅ 사용자님의 기준에 부합하는 A~B등급 종목을 찾아냈습니다!")
        else:
            st.warning("현재 기준을 충족하는 저평가 종목이 없습니다.")
