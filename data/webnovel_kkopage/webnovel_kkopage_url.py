from selenium.webdriver.common.by import By
from module.crawling_url import crawling_url
from module.login import kakao_login
import logging
import pickle
import time
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True,
)

driver = kakao_login(visible=False, second=True)

# id 추출 2025.02.24
# 월간 장르별 TOP 300
RANKING_URL_ids = [
    "https://page.kakao.com/landing/ranking/11/86?ranking_type=monthly",  # 판타지
    "https://page.kakao.com/landing/ranking/11/120?ranking_type=monthly",  # 현판
    "https://page.kakao.com/landing/ranking/11/89?ranking_type=monthly",  # 로맨스
    "https://page.kakao.com/landing/ranking/11/117?ranking_type=monthly",  # 로판
    "https://page.kakao.com/landing/ranking/11/87?ranking_type=monthly",  # 무협
    "https://page.kakao.com/landing/ranking/11/123?ranking_type=monthly",  # BL
    "https://page.kakao.com/landing/ranking/11/125?ranking_type=monthly",  # 드라마
]

# 전체 장르
TOTAL_URL_ids = [
    "https://page.kakao.com/menu/10011/screen/84?subcategory_uid=86&sort_opt=latest",  # 판타지 10,553
    "https://page.kakao.com/menu/10011/screen/84?subcategory_uid=120&sort_opt=latest",  # 현판 7,692
    "https://page.kakao.com/menu/10011/screen/84?subcategory_uid=89&sort_opt=latest",  # 로맨스 20,537
    "https://page.kakao.com/menu/10011/screen/84?subcategory_uid=117&sort_opt=latest",  # 로판 8,989
    "https://page.kakao.com/menu/10011/screen/84?subcategory_uid=87&sort_opt=latest",  # 무협 4,013
    "https://page.kakao.com/menu/10011/screen/84?subcategory_uid=123&sort_opt=latest",  # BL 3,239
    "https://page.kakao.com/menu/10011/screen/84?subcategory_uid=125&sort_opt=latest",  # 드라마 302
]

genre_list = [
    "fantasy",
    "modern_fantasy",
    "romance",
    "romance_fantasy",
    "martial_arts",
    "bl",
    "drama",
]

if not os.path.exists("ranking_ids"):
    os.mkdir("ranking_ids")
if not os.path.exists("total_links"):
    os.mkdir("total_links")

for genre_name, ranking_url, total_url in zip(
    genre_list, RANKING_URL_ids, TOTAL_URL_ids
):
    # ranking
    ranking_link = []

    logging.info(f"{genre_name} ranking url 크롤링 시작")
    link_list = []
    driver.get(ranking_url)
    actions = driver.find_element(By.CSS_SELECTOR, "body")
    SCROLL_PAUSE_TIME = 1

    last_height = driver.execute_script("return document.body.scrollHeight")
    cnt = 0
    while True:
        links = crawling_url(cnt=cnt, type="ranking", driver=driver)
        link_list += links
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(SCROLL_PAUSE_TIME)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        cnt += 1

    ranking_link += link_list
    with open(f"ranking_ids/{genre_name}_url.pkl", "wb") as f:
        pickle.dump(ranking_link, f)
    logging.info(f"{genre_name} ranking 크롤링 완료")

    # total
    total_link = []

    logging.info(f"{genre_name} total url 크롤링 시작")
    link_list = []
    driver.get(total_url)
    actions = driver.find_element(By.CSS_SELECTOR, "body")
    SCROLL_PAUSE_TIME = 1

    last_height = driver.execute_script("return document.body.scrollHeight")
    cnt = 0
    while True:
        links = crawling_url(cnt=cnt, type="total", driver=driver)
        link_list += links
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(SCROLL_PAUSE_TIME)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        cnt += 1

    total_link += link_list
    with open(f"total_links/{genre_name}_url.pkl", "wb") as f:
        pickle.dump(total_link, f)
    logging.info(f"{genre_name} total 크롤링 완료")

driver.quit()
