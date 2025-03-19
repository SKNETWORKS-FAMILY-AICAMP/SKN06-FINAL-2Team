# root 폴더에서 실행
from dotenv import load_dotenv
import pymysql
import logging
import json
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True,
)

# 환경 변수 로드
load_dotenv()

# MySQL 연결
conn = pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
)

cursor = conn.cursor()

genre_list = ["all"]  # 장르 더 있으면 추가


# 본인 데이터 있는 경로(data부터 시작/본인 폴더/장르명 전까지 파일명)
file_path = "SKN06-FINAL-2Team/data/webtoon_naver/webtoon_naver"

# JSON 파일 불러오기
with open(
    f"{file_path}_all.json",
    "r",
    encoding="utf-8",
) as json_file:
    data = json.load(json_file)

# 데이터 삽입 SQL
insert_sql = """
INSERT INTO contents (
    id, type, platform, title, status, update_days, thumbnail, genre, views, rating, likes,
    synopsis, keywords, author, illustrator, original, age_rating, price, url, episode, comments, first_episode,
    score, recent_comments_count
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s
)
"""

# 데이터 삽입
for row in data:
    for key, value in row.items():
        if value == "-":
            row[key] = None
    cursor.execute(
        insert_sql,
        (
            row.get("id"),
            row.get("type"),
            row.get("platform"),
            row.get("title"),
            row.get("status"),
            row.get("update_days"),
            row.get("thumbnail"),
            row.get("genre"),
            row.get("views"),
            row.get("rating"),
            row.get("likes"),
            row.get("synopsis"),
            row.get("keywords"),
            row.get("author"),
            row.get("illustrator"),
            row.get("original"),
            row.get("age_rating"),
            row.get("price"),
            row.get("url"),
            row.get("episode"),
            row.get("comments"),
            row.get("first_episode"),
            row.get("score"),
            row.get("recent_comments_count"),
        ),
    )

conn.commit()
logging.info(f"✅ 데이터 삽입 완료!")
cursor.close()
conn.close()
