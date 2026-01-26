import streamlit as st
import requests
from datetime import datetime
from pygooglenews import GoogleNews

# --- 설정 정보 ---
NAVER_CLIENT_ID = "GEGReBLC7buyb0JtGdvJ"
NAVER_CLIENT_SECRET = "y_rE3jsDV5"
KEYWORDS = ["삼성전자", "비트코인", "나스닥", "이더리움"]

st.set_page_config(page_title="통합 뉴스 대시보드", layout="wide")

def get_naver_news(kw):
    url = f"https://openapi.naver.com/v1/search/news.json?query={kw}&display=8&sort=date"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    try:
        res = requests.get(url, headers=headers)
        return res.json().get('items', [])
    except: return []

def get_google_news(kw):
    try:
        gn = GoogleNews(lang='ko')
        search = gn.search(kw)
        return search.get('entries', [])[:5]
    except: return []

st.title("🚀 네이버 & 구글 통합 뉴스 분류")

if 'news_store' not in st.session_state:
    st.session_state.news_store = {kw: [] for kw in KEYWORDS}

if st.button('🔄 전체 뉴스 실시간 수집 시작'):
    with st.spinner('네이버와 구글에서 정보를 긁어오고 있습니다...'):
        for kw in KEYWORDS:
            combined_news = []
            
            # 1. 네이버 뉴스 수집
            for n in get_naver_news(kw):
                title = n['title'].replace("<b>","").replace("</b>","").replace("&quot;", '"')
                combined_news.append({"src": "네이버", "title": title, "link": n['link']})
            
            # 2. 구글 뉴스 수집
            for g in get_google_news(kw):
                combined_news.append({"src": "구글", "title": g.title, "link": g.link})
                
            st.session_state.news_store[kw] = combined_news
        st.success("✅ 수집 완료!")

# --- 종목별 탭 출력 ---
tabs = st.tabs(KEYWORDS)
for i, kw in enumerate(KEYWORDS):
    with tabs[i]:
        news_list = st.session_state.news_store.get(kw, [])
        if not news_list:
            st.info("버튼을 눌러 뉴스를 불러오세요.")
        for news in news_list:
            color = "blue" if news['src'] == "네이버" else "green"
            st.markdown(f"**[:{color}[{news['src']}]]** [{news['title']}]({news['link']})")

