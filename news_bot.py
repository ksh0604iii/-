import requests
import sqlite3
from datetime import datetime
from pygooglenews import GoogleNews
import time

# --- 설정 정보 ---
TELEGRAM_TOKEN = "8382037479:AAG57DHZVdVTJQNG6q9mmBYU_3HKO6GugVQ"
CHAT_ID = 7064992115
KEYWORDS = ["날씨", "나스닥", "이더리움", "삼성전자"]

# DB 초기화 (뉴스 저장용)
def init_db():
    conn = sqlite3.connect('news_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS news
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  keyword TEXT, title TEXT, link TEXT, source TEXT, date TEXT)''')
    conn.commit()
    conn.close()

def save_news(keyword, title, link, source):
    conn = sqlite3.connect('news_data.db')
    c = conn.cursor()
    # 중복 체크
    c.execute("SELECT * FROM news WHERE link=?", (link,))
    if not c.fetchone():
        c.execute("INSERT INTO news (keyword, title, link, source, date) VALUES (?, ?, ?, ?, ?)",
                  (keyword, title, link, source, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

# ... (기존 get_naver_news, get_google_news 함수 동일) ...

def job():
    init_db()
    gn = GoogleNews(lang='ko')
    for keyword in KEYWORDS:
        # 네이버와 구글에서 뉴스를 가져온 뒤 save_news()로 저장하고, 
        # 저장이 성공(True)하면 텔레그램 전송
        pass # 실제 구현 시 위 로직 적용

if __name__ == "__main__":
    while True:
        job()

        time.sleep(600) # 10분마다 수집
