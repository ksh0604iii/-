import streamlit as st
import requests
from datetime import datetime
from pygooglenews import GoogleNews
import time

# --- 설정 정보 ---
NAVER_CLIENT_ID = "GEGReBLC7buyb0JtGdvJ"
NAVER_CLIENT_SECRET = "y_rE3jsDV5"
TELEGRAM_TOKEN = "8382037479:AAG57DHZVdVTJQNG6q9mmBYU_3HKO6GugVQ"
CHAT_ID = 7064992115
KEYWORDS = ["비트코인", "나스닥", "이더리움", "삼성전자"]

st.set_page_config(page_title="실시간 투자 뉴스", layout="wide")

# 세션 상태에 뉴스 저장소 만들기
if 'news_list' not in st.session_state:
    st.session_state.news_list = []

def get_naver_news(keyword):
    url = f"https://openapi.naver.com/v1/search/news.json?query={keyword}&display=5&sort=date"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    try:
        res = requests.get(url, headers=headers)
        return res.json().get('items', [])
    except: return []

# 메인 화면 구성
st.title("🚀 실시간 투자 뉴스 대시보드")
if st.button('🔄 지금 뉴스 새로고침'):
    with st.spinner('뉴스를 긁어오는 중...'):
        gn = GoogleNews(lang='ko')
        all_news = []
        for kw in KEYWORDS:
            # 네이버 뉴스 수집 로직 (간소화)
            items = get_naver_news(kw)
            for item in items:
                title = item['title'].replace("<b>","").replace("</b>","")
                all_news.append({"kw": kw, "title": title, "link": item['link'], "time": datetime.now().strftime('%H:%M')})
        st.session_state.news_list = all_news
    st.success('수집 완료!')

# 뉴스 출력
for news in st.session_state.news_list:
    st.markdown(f"**[{news['kw']}]** {news['title']} ([링크]({news['link']})) - *{news['time']}*")