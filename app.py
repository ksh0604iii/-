import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="실시간 주식/코인 뉴스 대시보드", layout="wide")

st.title("🚀 실시간 투자 뉴스 대시보드")
st.sidebar.header("설정")
target = st.sidebar.selectbox("종목 선택", ["전체", "비트코인", "나스닥", "이더리움", "삼성전자"])

def load_data():
    conn = sqlite3.connect('news_data.db')
    query = "SELECT keyword, title, source, date, link FROM news ORDER BY date DESC LIMIT 50"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

df = load_data()

if target != "전체":
    df = df[df['keyword'] == target]

# 화면 출력
for i, row in df.iterrows():
    with st.container():
        st.subheader(f"[{row['source']}] {row['title']}")
        st.write(f"종목: {row['keyword']} | 수집시간: {row['date']}")
        st.markdown(f"[기사 읽으러 가기]({row['link']})")
        st.divider()