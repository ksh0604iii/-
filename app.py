import streamlit as st
import yfinance as yf
import requests
import pandas as pd
from deep_translator import GoogleTranslator

# --- [설정] API 정보 ---
NAVER_ID = "GEGReBLC7buyb0JtGdvJ"
NAVER_SECRET = "y_rE3jsDV5"
KEYWORDS = ["비트코인", "나스닥", "이더리움", "삼성전자"]

st.set_page_config(page_title="글로벌 가치투자 대시보드", layout="wide")

# --- [로직] 점수 산출 함수 (사용자 점수표 100% 반영) ---
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

        # 4. 정성적 지표 및 기타 (자동화 불가 항목 기본값 20점 부여)
        score += 20 
        
        # --- [등급 판정] ---
        if score > 80: grade = "🥇 A (장기투자 적합 적극매수)"
        elif 70 <= score <= 80: grade = "🥈 B (장기투자 적합 매수 고려)"
        elif 50 <= score < 70: grade = "🥉 C (장기투자 유지/홀딩)"
        else: grade = "💀 D (절대 하지마)"
        
        return {"티커": ticker, "점수": score, "등급": grade, "PER": round(per, 2), "PBR": round(pbr, 2), "배당": f"{div:.2f}%"}
    except: return None

# --- [로직] 뉴스 수집 및 번역 ---
def fetch_news(kw):
    combined = []
    # 네이버 뉴스
    res = requests.get(f"https://openapi.naver.com/v1/search/news.json?query={kw}&display=3", 
                       headers={"X-Naver-Client-Id": NAVER_ID, "X-Naver-Client-Secret": NAVER_SECRET})
    for i in res.json().get('items', []):
        combined.append({"t": i['title'].replace('<b>','').replace('</b>',''), "l": i['link'], "o": "네이버"})
    # 구글 외신 번역
    try:
        combined.append({"t": f"🌐 [외신 원문] {kw} 소식보기", "l": f"https://www.google.com/search?q={kw}&tbm=nws&lr=lang_en", "o": "해외"})
    except: pass
    return combined

# --- [화면] 탭 시스템 구성 ---
st.title("🏛️ 글로벌 가치투자 올인원 대시보드")
t1, t2, t3 = st.tabs(["🎯 실시간 분석", "🚀 A-B등급 발굴", "📰 글로벌 뉴스"])

with t1:
    target = st.text_input("티커 입력 (예: AAPL, 005930.KS)")
    if st.button("분석 실행"):
        data = get_report(target)
        if data:
            st.write(f"### 최종 등급: {data['등급']}")
            st.json(data)
        else: st.error("데이터를 불러오지 못했습니다.")

with t2:
    if st.button("스캔 시작"):
        s_list = ["005930.KS", "005490.KS", "KO", "VZ", "T", "JPM"]
        results = [get_report(t) for t in s_list if get_report(t)]
        if results: st.table(pd.DataFrame(results))

with t3:
    if st.button("모든 뉴스 새로고침"):
        for kw in KEYWORDS:
            st.write(f"### 🔥 {kw} 리포트")
            for n in fetch_news(kw):
                st.markdown(f"📍 [{n['o']}] [{n['t']}]({n['l']})")

