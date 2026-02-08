import streamlit as st
import yfinance as yf
import requests
import pandas as pd
from pygooglenews import GoogleNews
from googletrans import Translator

# --- 기본 설정 ---
NAVER_CLIENT_ID = "GEGReBLC7buyb0JtGdvJ"
NAVER_CLIENT_SECRET = "y_rE3jsDV5"
KEYWORDS = ["비트코인", "나스닥", "이더리움", "삼성전자"]
translator = Translator()

st.set_page_config(page_title="글로벌 가치투자 대시보드", layout="wide")

# --- 1. 투자 등급 산출 로직 (사용자 이미지 기준) ---
def get_investment_report(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        score = 0
        # PER/PBR 점수 (이미지 c2e7e2 기준)
        per = info.get('trailingPE', 100)
        pbr = info.get('priceToBook', 100)
        div = (info.get('dividendYield', 0) or 0) * 100
        
        if per < 10: score += 10
        if pbr < 1.0: score += 5
        if div > 3: score += 5
        
        grade = "🥈 B (매수고려)" if score >= 15 else "💀 D (절대금지)"
        return {"티커": ticker, "점수": score, "등급": grade, "PER": round(per, 2), "PBR": round(pbr, 2), "배당": f"{div:.2f}%"}
    except: return None

# --- 2. 통합 뉴스 수집 및 번역 함수 ---
def fetch_global_news(kw):
    # (1) 구글 해외 외신 수집 (영어 검색)
    gn_en = GoogleNews(lang='en', country='US')
    en_search = gn_en.search(kw)
    en_entries = en_search.get('entries', [])[:3]
    
    translated_news = []
    for entry in en_entries:
        try:
            # 영어 제목을 한글로 번역
            trans = translator.translate(entry.title, src='en', dest='ko')
            translated_news.append({"title": trans.text, "link": entry.link, "origin": "해외외신"})
        except: pass

    # (2) 네이버 뉴스 수집
    n_url = f"https://openapi.naver.com/v1/search/news.json?query={kw}&display=3&sort=date"
    n_headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    try:
        res = requests.get(n_url, headers=n_headers)
        items = res.json().get('items', [])
        for item in items:
            title = item['title'].replace("<b>","").replace("</b>","")
            translated_news.append({"title": title, "link": item['link'], "origin": "네이버"})
    except: pass

    return translated_news

# --- 3. 화면 구성 ---
st.title("🏛️ 글로벌 가치투자 올인원 대시보드")
t_anal, t_scan, t_news = st.tabs(["🎯 실시간 분석", "🚀 A-B등급 발굴", "🌎 글로벌 뉴스(번역)"])

with t_anal:
    st.subheader("🔍 종목 정밀 진단")
    target = st.text_input("티커 입력 (예: AAPL)")
    if st.button("즉시 분석"):
        report = get_investment_report(target)
        if report: st.json(report)

with t_scan:
    st.subheader("🌟 오늘의 유망주 스캐너")
    if st.button("전 종목 스캔 시작"):
        scan_list = ["005930.KS", "KO", "VZ", "T", "JPM", "PEP"]
        final = [get_investment_report(t) for t in scan_list if get_investment_report(t) and get_investment_report(t)['점수'] >= 15]
        if final: st.table(pd.DataFrame(final))
        else: st.warning("조건을 만족하는 종목이 없습니다.")

with t_news:
    st.subheader("📰 해외 외신 번역 및 국내 뉴스 통합")
    if st.button('글로벌 뉴스 새로고침'):
        with st.spinner('해외 외신 번역 및 수집 중...'):
            for kw in KEYWORDS:
                st.write(f"### 🔥 {kw} 글로벌 리포트")
                all_news = fetch_global_news(kw)
                if all_news:
                    for news in all_news:
                        st.markdown(f"[{news['origin']}] [{news['title']}]({news['link']})")
                else: st.write("소식이 없습니다.")


