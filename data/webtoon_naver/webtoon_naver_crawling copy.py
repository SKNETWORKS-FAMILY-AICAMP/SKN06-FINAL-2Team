# 필요한 모듈 임포트
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests
import json
import time
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 환경 변수 로드 (네이버 로그인 정보)
load_dotenv()
# NAVER_ID = os.getenv("NAVER_ID")
# NAVER_PW = os.getenv("NAVER_PW")

# ✅ API 요청을 위한 함수 (재사용 가능)
def fetch_json_data(url):
    """API에서 JSON 데이터를 가져오는 함수"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None

# ✅ 네이버 웹툰 ID 수집 함수
def get_webtoon_ids():
    """네이버 웹툰의 ID 목록을 수집하는 함수"""
    ids = set()

    # 요일별 웹툰
    url_weekday = "https://comic.naver.com/api/webtoon/titlelist/weekday?order=user"
    data = fetch_json_data(url_weekday)
    if data:
        for day_webtoons in data.get("titleListMap", {}).values():
            ids.update(webtoon["titleId"] for webtoon in day_webtoons)

    # dailyPlus 웹툰
    url_dailyplus = "https://comic.naver.com/api/webtoon/titlelist/weekday?week=dailyPlus&order=user"
    data = fetch_json_data(url_dailyplus)
    if data:
        ids.update(webtoon["titleId"] for webtoon in data.get("titleList", []))

    # 완결 웹툰 (페이지 반복)
    for i in range(1, 70):
        url_finished = f"https://comic.naver.com/api/webtoon/titlelist/finished?page={i}&order=UPDATE"
        data = fetch_json_data(url_finished)
        if data:
            ids.update(webtoon["titleId"] for webtoon in data.get("titleList", []))

    return list(ids)  # 리스트로 변환

# ✅ Selenium 드라이버 설정 + 로그인
def setup_driver():
    """Selenium 웹드라이버를 설정하고 네이버에 로그인하는 함수"""
    driver_path = ChromeDriverManager().install()
    service = Service(executable_path=driver_path)
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    # 네이버 로그인 페이지 접속
    driver.get("https://nid.naver.com/nidlogin.login")
    time.sleep(120)

    # # 로그인 진행 (ID, PW 입력)
    # driver.find_element(By.ID, "id").send_keys(NAVER_ID)
    # driver.find_element(By.ID, "pw").send_keys(NAVER_PW)
    # driver.find_element(By.ID, "pw").send_keys(Keys.RETURN)
    
    print("✅ 네이버 로그인 완료! 크롤링을 시작합니다.")
    time.sleep(5)  # 로그인 후 대기

    return driver

# ✅ 웹툰 상세정보 크롤링 함수
def crawl_webtoon_details(webtoon_id, driver):
    """개별 웹툰의 상세 정보를 크롤링하는 함수"""
    url = f"https://comic.naver.com/api/article/list/info?titleId={webtoon_id}"
    data = fetch_json_data(url)
    if not data:
        return None

    # 기본 정보 추출
    title = data.get("titleName", "정보 없음")
    thumbnail = data.get("thumbnailUrl", "")
    genre = data.get("curationTagList", [{}])[0].get("tagName", "") if data.get("curationTagList") else ""
    synopsis = data.get("synopsis", "").replace("\n", " ")
    age_rating = data.get("age", {}).get("description", "전체 이용가")
    keywords = data.get("gfpAdCustomParam", {}).get("tags", [])

    # 작가 정보 추출
    artist_info = {"author": "-", "illustrator": "-", "original": "-"}
    for artist in data.get("communityArtists", []):
        for artist_type in artist.get("artistTypeList", []):
            if artist_type == "ARTIST_WRITER":
                artist_info["author"] = artist.get("name", "-")
            elif artist_type == "ARTIST_PAINTER":
                artist_info["illustrator"] = artist.get("name", "-")
            elif artist_type == "ARTIST_NOVEL_ORIGIN":
                artist_info["original"] = artist.get("name", "-")

    # 상태 및 가격 설정
    webtoon_status = "연재"
    update_days = "-"
    if data.get("finished"):
        webtoon_status = "완결"
    elif data.get("rest"):
        webtoon_status = "휴재"
    if data.get("dailyPass"):
        price = "기다리면 무료"
    else:
        price = "무료"

    # 첫 화 업로드 날짜 가져오기 (Selenium 사용)
    driver.get(f"https://comic.naver.com/webtoon/list?titleId={webtoon_id}&page=1&sort=ASC")
    # 요소가 나타날 때까지 기다리기
    WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "div.EpisodeListList__info_area--Rq03U > div > span.date"))
    )
    try:
        first_date_element = driver.find_element(By.CSS_SELECTOR, '#content div ul li a div span.date')
        first_release_date = first_date_element.text.strip()
    except Exception:
        first_release_date = "알 수 없음"

    # 최종 데이터 정리
    return {
        "id": webtoon_id,
        "title": title,
        "platform": "네이버 웹툰",
        "status": webtoon_status,
        "update_days": update_days,
        "thumbnail": thumbnail,
        "genre": genre,
        "synopsis": synopsis,
        "keywords": keywords,
        "author": artist_info["author"],
        "illustrator": artist_info["illustrator"],
        "original": artist_info["original"],
        "age_rating": age_rating,
        "price": price,
        "first_release_date": first_release_date,
        "url": f"https://comic.naver.com/webtoon/list?titleId={webtoon_id}"
    }

# ✅ 전체 크롤링 실행 함수
def run_crawling():
    """전체 웹툰 크롤링 실행"""
    webtoon_ids = get_webtoon_ids()
    driver = setup_driver()

    all_webtoons = []
    for i, webtoon_id in enumerate(webtoon_ids, 1):
        print(f"({i}/{len(webtoon_ids)}) 웹툰 {webtoon_id} 크롤링 중...")
        webtoon_data = crawl_webtoon_details(webtoon_id, driver)
        if webtoon_data:
            all_webtoons.append(webtoon_data)

    driver.quit()

    # 결과 저장
    with open("webtoon_data.json", "w", encoding="utf-8") as f:
        json.dump(all_webtoons, f, ensure_ascii=False, indent=4)

    print(f"총 {len(all_webtoons)}개의 웹툰 데이터가 저장되었습니다.")

# ✅ 실행
if __name__ == "__main__":
    run_crawling()
