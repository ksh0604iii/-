import streamlit as st
import requests

# --- 설정 정보 (네이버 개발자 센터에서 새로 복사해서 넣으세요!) ---
NAVER_CLIENT_ID = "GEGreBLC7buyb0JtGdvJ"
NAVER_CLIENT_SECRET = "y_rE3jsDV5"
KEYWORDS = ["삼성전자", "비트코인", "나스닥", "이더리움"]

st.set_page_config(page_title="종목별 뉴스 알리미", layout="wide")

def get_news(kw):
    url = f"https://openapi.naver.com/v1/search/news.json?query={kw}&display=10&sort=date"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID, 
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 401:
            return "AUTH_ERROR"
        return res.json().get('items', [])
    except:
        return []

st.title("📊 종목별 실시간 뉴스 분류")

# 뉴스 데이터를 담을 딕셔너리 초기화
if 'news_store' not in st.session_state:
    st.session_state.news_store = {kw: [] for kw in KEYWORDS}

if st.button('🔄 전 종목 뉴스 업데이트'):
    with st.spinner('최신 정보를 분류 중입니다...'):
        auth_fail = False
        for kw in KEYWORDS:
            items = get_news(kw)
            if items == "AUTH_ERROR":
                auth_fail = True
                break
            st.session_state.news_store[kw] = items
        
        if auth_fail:
            st.error("❌ 네이버 API 인증에 실패했습니다. ID와 Secret을 확인해주세요.")
        else:
            st.success("✅ 모든 종목의 수집이 완료되었습니다!")

# --- 키워드별 탭 구성 ---
tabs = st.tabs(KEYWORDS)

for i, kw in enumerate(KEYWORDS):
    with tabs[i]:
        st.header(f"🔍 {kw} 최신 소식")
        news_items = st.session_state.news_store.get(kw, [])
        
        if not news_items:
            st.write("아직 수집된 뉴스가 없습니다. 업데이트 버튼을 눌러주세요.")
        else:
            for item in news_items:
                title = item['title'].replace("<b>","").replace("</b>","").replace("&quot;", '"')
                st.markdown(f"📍 [{title}]({item['link']})")
                st.caption(f"출처: 네이버 뉴스 | {kw}")
                st.divider()

