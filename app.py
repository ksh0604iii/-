import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from deep_translator import GoogleTranslator

# --- [설정] API 정보 및 키워드 ---
NAVER_ID = "GEGReBLC7buyb0JtGdvJ"
NAVER_SECRET = "y_rE3jsDV5"
# 뉴스 수집을 원하는 키워드 리스트
KEYWORDS = ["Bitcoin", "Nasdaq", "Ethereum", "Samsung Electronics"]

st.set_page_config(page_title="글로벌 가치투자 통합 대시보드", layout="wide")

# --- 1. [로직] 사용자 점수표 기반 분석 (image_cea67e, cea684 반영) ---
def get_report(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info or 'trailingPE' not in info: return None
            
        score = 0
        per = info.get('trailingPE', 100)
        pbr = info.get('priceToBook', 100)
        div = (info.get('dividendYield', 0) or 0) * 100
        
        # PER 점수
        if per < 5: score += 20
        elif per < 8: score += 15
        elif per < 10: score += 10
        else: score += 5
        
        # PBR 점수
        if pbr < 0.3: score += 5
        elif pbr < 0.6: score += 4
        elif pbr < 1.0: score += 3
        else: score += 0
        
        # 배당 점수
        if div > 7: score += 10
        elif div > 5: score += 7
        elif div > 3: score += 5
        else: score += 2

        score += 20 # 정성적 지표 기본 점수
        
        # 등급 판정
        if score > 80: grade = "🥇 A (적극매수)"
        elif 70 <= score <= 80: grade = "🥈 B (매수고려)"
        elif 50 <= score < 70: grade = "🥉 C (홀딩)"
        else: grade = "💀 D (절대금지)"
        
        return {"종목": info.get('shortName', ticker), "티커": ticker, "점수": score, "등급": grade, 
                "PER": round(per, 2), "PBR": round(pbr, 2), "배당": f"{div:.2f}%"}
    except: return None

# --- 2. [로직] 국내/해외 뉴스 수집 및 번역 함수 ---
def fetch_all_news(kw):
    news_list = []
    # (1) 네이버 뉴스 (국내 호재/악재)
    try:
        n_url = f"https://openapi.naver.com/v1/search/news.json?query={kw}&display=3&sort=date"
        n_res = requests.get(n_url, headers={"X-Naver-Client-Id": NAVER_ID, "X-Naver-Client-Secret": NAVER_SECRET})
        for i in n_res.json().get('items', []):
            title = i['title'].replace('<b>','').replace('</b>','').replace('&quot;','')
            news_list.append({"t": title, "l": i['link'], "o": "네이버"})
    except: pass

    # (2) 구글 해외 외신 (영어 수집 및 한글 번역)
    try:
        rss_url = f"https://news.google.com/rss/search?q={kw}&hl=en-US&gl=US&ceid=US:en"
        response = requests.get(rss_url)
        root = ET.fromstring(response.content)
        for item in root.findall('./channel/item')[:2]:
            title_en = item.find('title').text
            # 실시간 번역
            title_ko = GoogleTranslator(source='en', target='ko').translate(title_en)
            news_list.append({"t": f"[외신번역] {title_ko}", "l": item.find('link').text, "o": "구글해외"})
    except: pass
    return news_list

# --- 3. [화면] 통합 탭 구성 ---
st.title("🏛️ 글로벌 가치투자 통합 대시보드")
t1, t2, t3 = st.tabs(["🎯 종목 정밀 분석", "🚀 글로벌 전수 스캔", "📰 통합 뉴스 리포트"])

with t1:
    st.subheader("🔍 개별 종목 정밀 진단")
    target = st.text_input("분석할 티커 입력 (예: AAPL, 005930.KS)")
    if st.button("분석 실행"):
        res = get_report(target)
        if res:
            st.success(f"### {target} 분석 결과: {res['등급']}")
            st.json(res)
        else: st.error("데이터를 불러오지 못했습니다.")

with t2:
    st.subheader("🌐 글로벌 시장 전수 조사")
    if st.button("전 세계 시장 전수 스캔 시작"):
        tickers = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "KO", "T", "JPM", "005930.KS", "005490.KS", "035420.KS"]
        final_results = []
        with st.spinner('전 세계 시장 데이터를 대조 분석 중...'):
            for t in tickers:
                data = get_report(t)
                if data: final_results.append(data)
        
        if final_results:
            df = pd.DataFrame(final_results).sort_values(by="점수", ascending=False)
            st.table(df) # 등급이 없더라도 점수 높은 순으로 나열

with t3:
    st.subheader("📰 국내외 실시간 통합 뉴스")
    if st.button("모든 뉴스 및 번역본 가져오기"):
        for kw in KEYWORDS:
            st.write(f"### 🔥 {kw} 리포트")
            items = fetch_all_news(kw)
            for n in items:
                st.markdown(f"📍 [{n['o']}] [{n['t']}]({n['l']})")


