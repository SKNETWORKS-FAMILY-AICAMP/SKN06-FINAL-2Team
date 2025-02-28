import json
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs

# ✅ Selenium WebDriver 설정
def thumbnail_crawling():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    action = ActionChains(driver)  # ActionChains 생성

    # 카카오 웹툰 페이지 열기
    url = "https://webtoon.kakao.com"
    driver.get(url)
    time.sleep(1)  # 페이지 로딩 대기

    # 기존 JSON 파일 로드
    with open("webtoon_kko_crawling_with_thumbnails.json", "r", encoding="utf-8") as f:
        webtoon_data = json.load(f)

    # 웹툰 ID 추출 함수
    def extract_webtoon_id(url):
        """웹툰 URL에서 ID 추출"""
        match = re.search(r'/content/.+/(\d+)', url)
        return int(match.group(1)) if match else None

    # 점진적 스크롤 함수
    def slow_scroll(driver):
        """페이지가 로딩될 수 있도록 천천히 스크롤을 내리는 함수"""
        scroll_pause_time = 0.5
        webtoons = driver.find_elements(By.CSS_SELECTOR, "a[href*='/content/']")

        for webtoon in webtoons:
            try:
                action.move_to_element(webtoon).perform()  # 해당 요소까지 이동
                time.sleep(scroll_pause_time)
            except:
                pass

    # 카테고리 & "전체보기" 버튼 선택자
    day_sel = "#root > main > div > div.px-11.mx-auto.my-0.w-full.lg\:w-default-max-width.md\:w-\[490px\] > div.sticky.w-full.z-navigationBarPlus1.mt-6.transition-all.duration-\[250ms\].bg-background > div.relative.z-navigationBarMinus1.mx-auto.my-0.w-full > div.w-full.h-full.relative > ul > li:nth-child({}) > p"
    total_sel = "#root > main > div > div.px-11.mx-auto.my-0.w-full.lg\:w-default-max-width.md\:w-\[490px\] > div.sticky.w-full.z-navigationBarPlus1.mt-6.transition-all.duration-\[250ms\].bg-background > div.w-full.h-40.sticky.flex.px-11.border-t-1.pb-10.justify-center.overflow-hidden > div > button:nth-child(1)"

    # 웹툰 ID-썸네일 저장 딕셔너리
    webtoon_thumbnails = {}

    # 카테고리별 웹툰 크롤링
    for id in range(9, 10):  # 월~완결 (신작 제외)
        try:
            category_selector = day_sel.format(id)
            category = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, category_selector))
            )
            category.click()
            time.sleep(0.3)

            total = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, total_sel))
            )
            total.click()
            time.sleep(0.3)

            slow_scroll(driver)

            # 웹툰 리스트 가져오기
            webtoons = driver.find_elements(By.CSS_SELECTOR, "a[href*='/content/']")

            # 웹툰 ID & 썸네일 크롤링
            for webtoon in webtoons:
                webtoon_url = webtoon.get_attribute("href")

                # 웹툰 ID 추출
                webtoon_id = extract_webtoon_id(webtoon_url)
                if not webtoon_id:
                    continue

                # 썸네일 이미지 URL 가져오기
                try:
                    thumbnail_element = webtoon.find_element(By.CSS_SELECTOR, "img.w-full.h-full.object-cover.object-top")
                    thumbnail = thumbnail_element.get_attribute("src")
                except:
                    thumbnail = ""  # 썸네일이 없는 경우 빈 문자열

                # ID 기준으로 썸네일 정보 저장
                webtoon_thumbnails[webtoon_id] = thumbnail
                print(f"웹툰 {webtoon_id}번 썸네일 저장 완료")

        except Exception as e:
            print(f"❌ 카테고리 {id} 크롤링 중 오류 발생: {e}")

    # 기존 JSON 파일과 매칭하여 썸네일 추가
    for webtoon in webtoon_data:
        webtoon_id = webtoon["id"]
        if webtoon_id in webtoon_thumbnails:
            webtoon["thumbnail"] = webtoon_thumbnails[webtoon_id]

    # JSON 파일 저장
    with open("detail/webtoon_kko_crawling_thumbnail.json", "w", encoding="utf-8") as f:
        json.dump(webtoon_data, f, ensure_ascii=False, indent=4)

    print("웹툰 썸네일 추가 완료!")

    # WebDriver 종료
    driver.quit()