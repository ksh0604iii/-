import streamlit as st
import requests
from datetime import datetime

# --- 설정 정보 (본인 값으로 유지) ---
NAVER_CLIENT_ID = "GEGreBLC7buyb0JtGdvJ"
NAVER_CLIENT_SECRET = "y_rE3jsDV5"
KEYWORDS = ["정치", "날씨", "삼성전자"]

st.set_page_config(page_title="실시간 뉴스 대시보드", layout="wide")

def get_news(kw):
    url = f"https://openapi.naver.com/v1/search/news.json?query={kw}&display=10&sort=date"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID, 
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    try:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            st.error(f"API 오류: {res.status_code} - {res.text}")
            return []
        items = res.json().get('items', [])
        return items
    except Exception as e:
        st.error(f"연결 오류: {e}")
        return []

st.title("🚀 실시간 뉴스 수집기")

if st.button('🔄 뉴스 긁어오기'):
    with st.spinner('데이터 수집 중...'):
        all_results = []
        for kw in KEYWORDS:
            news_items = get_news(kw)
            for item in news_items:
                all_results.append({
                    "kw": kw,
                    "title": item['title'].replace("<b>","").replace("</b>","").replace("&quot;", '"'),
                    "link": item['link']
                })
        st.session_state.news_list = all_results

# 결과 출력 로직
if 'news_list' in st.session_state and st.session_state.news_list:
    st.success(f"총 {len(st.session_state.news_list)}개의 뉴스를 찾았습니다!")
    for n in st.session_state.news_list:
        st.markdown(f"**[{n['kw']}]** [{n['title']}]({n['link']})")
else:
    st.info("버튼을 눌러주세요. 만약 계속 0건이라면 API 설정을 확인해야 합니다.")

