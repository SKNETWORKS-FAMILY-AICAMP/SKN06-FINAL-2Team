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

genre_list = [
    "fantasy",
    "drama",
    "romance",
    "rofan",
    "historical",
    "action",
    "bl"
]  # 장르 더 있으면 추가

for genre in genre_list:
    # 본인 데이터 있는 경로(data부터 시작/본인 폴더/장르명 전까지 파일명)
    file_path = "data/webtoon_kkopage/"

    # JSON 파일 불러오기
    with open(
        f"{file_path}{genre}.json",
        "r",
        encoding="utf-8",
    ) as json_file:
        data = json.load(json_file)

    # 데이터 삽입 SQL
    insert_sql = """
    INSERT INTO contents (
        id, type, platform, title, status, update_days, thumbnail, genre, views, rating, 
        synopsis, keywords, author, illustrator, original, age_rating, price, url, episode, comments_count, recent_commnets_count,
        score
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
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
                row.get("views", 0),
                row.get("rating"),
                row.get("likes", 0),
                row.get("synopsis"),
                row.get("keywords"),
                row.get("author"),
                row.get("illustrator"),
                row.get("original"),
                row.get("age_rating"),
                row.get("price"),
                row.get("url"),
                row.get("episode", 0),
                row.get("comments", 0),
                row.get("first_episode"),
                row.get("score", 0),
            ),
        )

    conn.commit()
    logging.info(f"✅ {genre} 데이터 삽입 완료!")
cursor.close()
conn.close()
