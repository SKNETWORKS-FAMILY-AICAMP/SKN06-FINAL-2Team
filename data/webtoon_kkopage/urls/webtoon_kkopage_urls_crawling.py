import json
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# logging 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 장르별 설정
uids = [115,116,121,69,112,122,119]
genres = ["fantasy","drama","romance","rofan","historical","action","bl"]

# Selenium 옵션 
options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)

for uid, genre in zip(uids, genres):
    page_url = f"https://page.kakao.com/menu/10010/screen/82?subcategory_uid={uid}"
    logging.info(f"Processing URL: {page_url}")
    driver.get(page_url)
    time.sleep(3)  # 초기 로딩 대기

    urls = set()
    last_height = driver.execute_script("return document.body.scrollHeight")       

    while True:
        # 페이지 내에서 '/content/'를 포함하는 모든 링크 요소 추출
        page_url = driver.find_elements(By.CSS_SELECTOR, "a[href*='/content/']")
        for a in page_url:
            href = a.get_attribute("href")
            if href:
                urls.add(href)
        
        urls_count = len(urls)
        logging.info(f"[{genre}] 현재까지 크롤링된 URL 개수: {urls_count}")

        # 페이지 맨 아래로 스크롤
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        # 새로 로드된 페이지 높이 확인
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # 더 이상 새 콘텐츠가 로드되지 않으면 종료
        last_height = new_height

    urls_list = list(urls)
    output_filename = f"webtoon_kkopage_{genre}_urls.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(urls_list, f, ensure_ascii=False, indent=4)
    logging.info(f"총 {urls_count}개의 URL이 {output_filename}에 저장되었습니다.")
        
driver.quit()

