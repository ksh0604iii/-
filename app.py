import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from deep_translator import GoogleTranslator

# --- [설정] API 정보 ---
NAVER_ID = "GEGReBLC7buyb0JtGdvJ"
NAVER_SECRET = "y_rE3jsDV5"
KEYWORDS = ["Bitcoin", "Nasdaq", "Ethereum", "Samsung Electronics"]

st.set_page_config(page_title="글로벌 가치투자 대시보드", layout="wide")

# --- [로직] 점수 산출 및 등급 판정 (사용자 점수표 100% 반영) ---
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

        # 4. 정성적 지표 기본 점수 (20점 부여)
        score += 20 
        
        # --- [등급 판정] ---
        if score > 80: grade = "🥇 A (적극매수)"
        elif 70 <= score <= 80: grade = "🥈 B (매수고려)"
        elif 50 <= score < 70: grade = "🥉 C (홀딩)"
        else: grade = "💀 D (절대금지)"
        
        return {"티커": ticker, "점수": score, "등급": grade, "PER": round(per, 2), "PBR": round(pbr, 2), "배당": f"{div:.2f}%"}
    except: return None

# --- [로직] 구글 외신 실시간 수집 및 번역 ---
def fetch_global_news(kw):
    news_list = []
    rss_url = f"https://news.google.com/rss/search?q={kw}&hl=en-US&gl=US&ceid=US:en"
    try:
        res = requests.get(rss_url)
        root = ET.fromstring(res.content)
        for item in root.findall('./channel/item')[:3]:
            title = item.find('title').text
            link = item.find('link').text
            # 실시간 한글 번역
            trans = GoogleTranslator(source='en', target='ko').translate(title)
            news_list.append({"t": trans, "l": link})
    except: pass
    return news_list

# --- [화면] 탭 시스템 구성 ---
st.title("🏛️ 글로벌 가치투자 올인원 대시보드")
t1, t2, t3 = st.tabs(["🎯 실시간 분석", "🚀 우량주 스캐너", "📰 글로벌 뉴스"])

with t1:
    target = st.text_input("티커 입력 (예: AAPL, NVDA)")
    if st.button("분석 실행"):
        data = get_report(target)
        if data: st.json(data)

with t2:
    st.subheader("🚀 시장 전체 종목 중 A-B등급 발굴")
    if st.button("전체 스캔 시작"):
        # 스캔 대상을 우량주 위주로 대폭 확장
        master_list = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "KO", "T", "VZ", "JPM", "005930.KS", "005490.KS"]
        final_results = []
        with st.spinner('전 세계 시장 데이터 수집 중...'):
            for t in master_list:
                res = get_report(t)
                if res: final_results.append(res)
        
        if final_results:
            df = pd.DataFrame(final_results)
            # 점수 높은 순으로 정렬
            st.table(df.sort_values(by="점수", ascending=False))

with t3:
    st.subheader("📰 실시간 외신 한글 번역 뉴스")
    if st.button("뉴스 새로고침"):
        for kw in KEYWORDS:
            st.write(f"### 🔥 {kw} 글로벌 리포트")
            # 네이버 국내 뉴스 수집
            n_res = requests.get(f"https://openapi.naver.com/v1/search/news.json?query={kw}&display=3", 
                                 headers={"X-Naver-Client-Id": NAVER_ID, "X-Naver-Client-Secret": NAVER_SECRET})
            for i in n_res.json().get('items', []):
                st.markdown(f"📍 [국내] [{i['title'].replace('<b>','').replace('</b>','')}]({i['link']})")
            
            # 구글 해외 외신 수집 및 번역
            items = fetch_global_news(kw)
            for n in items:
                st.markdown(f"📍 [해외] [{n['t']}]({n['l']})")
