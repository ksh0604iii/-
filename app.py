import streamlit as st
import requests
from datetime import datetime
from pygooglenews import GoogleNews

# --- 설정 정보 ---
NAVER_CLIENT_ID = "GEGReBLC7buyb0JtGdvJ"
NAVER_CLIENT_SECRET = "y_rE3jsDV5"
KEYWORDS = ["비트코인", "나스닥", "이더리움", "삼성전자"]

st.set_page_config(page_title="실시간 투자 뉴스", layout="wide")

def get_naver_news(keyword):
    url = f"https://openapi.naver.com/v1/search/news.json?query={keyword}&display=5&sort=date"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    try:
        res = requests.get(url, headers=headers)
        return res.json().get('items', [])
    except: return []

# 메인 화면
st.title("🚀 투자 뉴스 대시보드")

if st.button('🔄 지금 뉴스 새로고침'):
    with st.spinner('실시간 뉴스를 가져오는 중...'):
        all_news = []
        for kw in KEYWORDS:
            # 네이버 뉴스 수집
            items = get_naver_news(kw)
            for item in items:
                title = item['title'].replace("<b>","").replace("</b>","").replace("&quot;", '"')
                all_news.append({
                    "종목": kw,
                    "제목": title,
                    "링크": item['link'],
                    "시간": datetime.now().strftime('%H:%M')
                })
        st.session_state.news_data = all_news
    st.success(f'총 {len(all_news)}건의 뉴스를 가져왔습니다!')

# 뉴스 목록 출력 (데이터가 있을 때만)
if 'news_data' in st.session_state and st.session_state.news_data:
    for news in st.session_state.news_data:
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.info(f"📍 {news['종목']}")
            with col2:
                st.markdown(f"#### [{news['제목']}]({news['link']})")
                st.caption(f"수집 시간: {news['시간']}")
            st.divider()
else:
    st.warning("위의 버튼을 눌러 실시간 뉴스를 불러오세요!")