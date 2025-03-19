import os
import json
import re
import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup as bs
import pickle
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from load_detail import thumbnail_crawling
from dotenv import load_dotenv


################################################################################################################
# kakao_login
################################################################################################################

def get_webtoon_urls_by_tab(tab_name, driver):
    """
    특정 요일 또는 '완결' 탭에서 '전체' 버튼을 클릭한 후, 모든 웹툰 URL을 가져오는 함수
    """
    base_url = f"https://webtoon.kakao.com/?tab={tab_name}"
    driver.get(base_url)
    time.sleep(3)  # 페이지 로딩 대기

    print(f"{tab_name.upper()} 탭 크롤링 시작...")

    # "전체" 버튼 클릭 (버튼이 로드될 때까지 기다린 후 클릭)
    try:
        entire_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[span[text()='전체']]"))
        )
        entire_button.click()
        time.sleep(2)  # 클릭 후 페이지 변경 대기
    except Exception as e:
        print(f"'{tab_name.upper()}' 탭에서 '전체' 버튼을 찾을 수 없거나 클릭할 수 없습니다.", e)

    # 무한 스크롤 (스크롤을 끝까지 내려서 모든 웹툰 로드)
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)  # 페이지 끝으로 스크롤
        time.sleep(2)  # 데이터 로딩 대기
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:  # 더 이상 스크롤이 내려가지 않으면 종료
            break
        last_height = new_height

    # 웹툰 목록에서 URL 가져오기
    webtoon_urls = []
    webtoon_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/content/']")  # 웹툰 링크 요소 찾기
    
    for element in webtoon_elements:
        webtoon_url = element.get_attribute("href")  # 웹툰 URL 가져오기
        if webtoon_url and webtoon_url.startswith("https://webtoon.kakao.com/content/"):
            webtoon_urls.append(webtoon_url)

    print(f"{tab_name.upper()} 탭에서 {len(webtoon_urls)}개의 웹툰을 수집했습니다.\n")
    return list(set(webtoon_urls))  # 중복 제거 후 반환


def get_all_webtoon_urls():
    """
    Selenium을 사용하여 모든 요일 및 완결 탭에서 웹툰 URL을 가져오고 피클 파일로 저장하는 함수
    """
    #Chrome WebDriver 설정
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") 
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # 🔹 요일 + 완결 탭 목록
    tabs = ["mon", "tue", "wed", "thu", "fri", "sat", "sun", "complete"]
    all_webtoon_urls = []

    for tab in tabs:
        urls = get_webtoon_urls_by_tab(tab, driver)
        all_webtoon_urls.extend(urls)

    driver.quit()  # 브라우저 종료

    all_webtoon_urls = list(set(all_webtoon_urls))  # 중복 제거

    # 🔹 웹툰 URL 리스트를 피클 파일로 저장
    with open("webtoon_kko_urls.pkl", "wb") as f:
        pickle.dump(all_webtoon_urls, f)

    print(f"웹툰 URL이 'kakao_webtoon_urls.pkl' 파일로 저장되었습니다.")

    return all_webtoon_urls

# 크롤링 실행 및 저장
webtoon_list = get_all_webtoon_urls()

################################################################################################################
# webtoon_detail_crawling
################################################################################################################

load_dotenv()
# WebDriver 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

kakao_id = os.getenv("KAKAO_ID")
kakao_pw = os.getenv("KAKAO_PWD")
driver.get("https://webtoon.kakao.com/more")

# 로그인처리
login_icon = r"#root > main > div > div.bg-background-02 > div > div > a:nth-child(1) > div > img.w-113.h-38"
driver.find_element(By.CSS_SELECTOR, login_icon).click()
time.sleep(2)
login_button = r"body > div:nth-child(5) > div > div > div > div.overflow-x-hidden.overflow-y-auto.\!overflow-hidden.flex.flex-col > div.text-center.pb-\[112px\].overflow-y-auto > div > div > button"
driver.find_element(By.CSS_SELECTOR, login_button).click()
time.sleep(2)

ID_selector = r"#loginId--1"
PWD_selector = r"#password--2"
ID_input = driver.find_element(By.CSS_SELECTOR, ID_selector)
ActionChains(driver).send_keys_to_element(ID_input, kakao_id).perform()
PWD_input = driver.find_element(By.CSS_SELECTOR, PWD_selector)
ActionChains(driver).send_keys_to_element(PWD_input, kakao_pw).perform()
login_selector = (
    r"#mainContent > div > div > form > div.confirm_btn > button.btn_g.highlight.submit"
)
driver.find_element(By.CSS_SELECTOR, login_selector).click()
time.sleep(2)
# 동시접속 기기 횟수 초과 시

alert = r"body > div:nth-child(8) > div > div > div > div.absolute.w-full.px-18.bottom-0.pb-30.flex.left-0.z-1.bg-grey-01.light\:bg-white.Alert_buttonsWrap__2ln9d.pt-10 > button.relative.px-10.py-0.btn-white.light\:btn-black.button-active"
driver.find_element(By.CSS_SELECTOR, alert).click()


def extract_webtoon_id(url):
    """카카오웹툰 URL에서 웹툰 ID를 추출하는 함수"""
    match = re.search(r'/content/.+/(\d+)', url)
    return match.group(1) if match else None

# 숫자 변환
def convert_views(view_text):
    if "만" in view_text:
        return int(float(view_text.replace(",", "").replace("만", "")) * 10000)
    elif "억" in view_text:
        return int(float(view_text.replace(",", "").replace("억", "")) * 100000000)
    else:
        return int(view_text.replace(",", "")) if view_text.replace(",", "").isdigit() else "-"

def get_webtoon_info(webtoon_id):
    """API를 사용해 웹툰 기본 정보를 가져오고, Selenium을 사용해 추가 정보를 크롤링하는 함수"""
    profile_url = f"https://gateway-kw.kakao.com/decorator/v2/decorator/contents/{webtoon_id}/profile"
    episode_url = f"https://gateway-kw.kakao.com/episode/v2/views/content-home/contents/{webtoon_id}/episodes?sort=-NO&offset=0&limit=30"
    price_url = f"https://gateway-kw.kakao.com/ticket/v2/views/content-home/available-tickets?contentId={webtoon_id}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Referer": "https://webtoon.kakao.com/",
        "Accept-Language": "ko",
    }

    # Selenium으로 API URL 직접 열기
    time.sleep(2)
    driver.get(profile_url)
    time.sleep(3)  # 페이지 로딩 대기

    # HTML에서 JSON 추출
    soup = bs(driver.page_source, "html.parser")
    time.sleep(2)
    pre_tag = soup.find("pre")  # API 응답이 JSON 형태로 담겨 있음
    if not pre_tag:
        print(f"API 응답을 찾을 수 없음: {webtoon_id}")
        return None

    # JSON 파싱
    try:
        data = json.loads(pre_tag.text)  # Selenium에서 가져온 데이터를 JSON으로 변환
    except json.JSONDecodeError:
        print(f"JSON 디코딩 실패: {webtoon_id}")
        return None

    # 웹툰 정보 파싱
    seo_id = data.get("data", {}).get("seoId", "")
    webtoon_page_url = f"https://webtoon.kakao.com/content/{seo_id}/{webtoon_id}?tab=profile"

    # 작가, 일러스트레이터, 원작 분리
    author, illustrator, original = "-", "-", "-"
    for person in data.get("data", {}).get("authors", []):
        if person.get("type") == "AUTHOR":
            author = person.get("name", "-")
        elif person.get("type") == "ILLUSTRATOR":
            illustrator = person.get("name", "-")
        elif person.get("type") == "ORIGINAL_STORY":
            original = person.get("name", "-")

    # 연재 상태 설정
    status = "-"
    status_map = {
        "COMPLETED": "완결",
        "END_OF_SEASON": "연재",
        "SEASON_COMPLETED":"연재",
        "EPISODES_PUBLISHING": "연재",
        "EPISODES_NOT_PUBLISHING": "휴재"
    }

    for badge in data.get("data", {}).get("badges", []):
        if badge.get("type") == "STATUS":
            status = status_map.get(badge.get("title"), "-")

    # 연재 요일 변환
    weekdays_map = {
        "MON": "월요일", "TUE": "화요일", "WED": "수요일",
        "THU": "목요일", "FRI": "금요일", "SAT": "토요일", "SUN": "일요일"
    }
    update_days = "-"
    if status not in ["휴재", "완결"]:
        update_days = [
            weekdays_map.get(b.get("title", "").upper(), "-")
            for b in data.get("data", {}).get("badges", []) if b.get("type") == "WEEKDAYS"
        ]
        update_days = ", ".join(update_days) if update_days else "-"

    # 연령 제한
    age_rating = "전체 이용가"
    for badge in data.get("data", {}).get("badges", []):
        if badge.get("type") == "AGE_LIMIT":
            age_rating = f"{badge.get('title', '')}세 이용가"

    # 키워드 정리
    keywords = ", ".join([k.replace("#", "") for k in data.get("data", {}).get("seoKeywords", [])])
    
    # API에서 에피소드 개수와 최초 연재날짜 가져오기
    episode_response = requests.get(episode_url, headers=headers)
    
    episode_count = episode_response.json().get("meta", {}).get("pagination", {}).get("totalCount", 0) if episode_response.status_code == 200 else 0
    
    first_episode = "-"
    episode_date = episode_response.json().get("data", {}).get("first", {}).get("serialStartDateTime", None)
    if episode_date:
        first_episode = datetime.strptime(episode_date[:10], "%Y-%m-%d").strftime("%Y.%m.%d") 
    
    # 가격 정보 가져오기
    response = requests.get(price_url, headers=headers)
    price_info = response.json().get("data", {})
    free_publishing = data.get("freePublishing", None)
    free_episode_count = data.get("freeEpisodeCount", 0) 
    
    price = "-"
    if "waitForFree" in price_info:
        price = "기다리면 무료"
    elif free_publishing is False and free_episode_count == episode_count:
        price = "무료"
    elif free_publishing is False:
        price = "유료"
    else:
        price = "무료"  # 기본적으로 무료 처리

    # Selenium을 이용한 추가 정보 크롤링
    time.sleep(3)
    driver.get(webtoon_page_url)
    time.sleep(2)

    soup = bs(driver.page_source, "html.parser")

    # 장르, 조회수, 좋아요 가져오기
    genre, views, likes = "-", "-", "-"
    stats = soup.find_all("div", class_="flex justify-center items-start h-14 mt-8 leading-14")

    for stat in stats:
        items = stat.find_all("p", class_="whitespace-pre-wrap break-all break-words support-break-word s12-regular-white ml-2 opacity-75")
        if len(items) >= 3:
            genre = items[0].text.strip()  # 장르
            views = convert_views(items[1].text.strip())  # 조회수
            likes = convert_views(items[2].text.strip())  # 좋아요

    # 웹툰 정보 정리
    webtoon_info = {
        "id": int(webtoon_id),
        "type": "웹툰",
        "platform": "카카오웹툰",
        "title": data.get("data", {}).get("title", ""),
        "status": status,
        "update_days": update_days,
        "thumbnail": "-",
        "genre": genre,
        "views": views,
        "likes": likes,
        "synopsis": data.get("data", {}).get("synopsis", ""),
        "keywords": keywords,
        "author": author,
        "illustrator": illustrator,
        "original": original,
        "age_rating": age_rating,
        "price": price,
        "episode": episode_count,
        "url": webtoon_page_url,
        "first_episode": first_episode
    }
    return webtoon_info

# 피클 파일에서 웹툰 URL 불러오기
with open("webtoon_kko_urls.pkl", "rb") as f:
    webtoon_urls = pickle.load(f)

# 웹툰 정보 크롤링 실행
webtoon_data_list = []
for url in webtoon_urls[:]:  # 할만큼 지정
    webtoon_id = extract_webtoon_id(url)
    if webtoon_id:
        webtoon_data = get_webtoon_info(webtoon_id)
        if webtoon_data:
            webtoon_data_list.append(webtoon_data)
            print(f"총 {len(webtoon_data_list)}개의 웹툰 정보를 저장했습니다.")


# JSON 파일로 저장
with open("detail/webtoon_kko_crawling.json", "w", encoding="utf-8") as f:
    json.dump(webtoon_data_list, f, ensure_ascii=False, indent=4) # <- 총 데이터 json으로 내보내기

print(f"{webtoon_id}의 웹툰 정보를 저장했습니다.")


################################################################################################################
# webtoon_detail_crawling
################################################################################################################

thumbnail_crawling()
print("thumbnail crawling 추가 완료")


