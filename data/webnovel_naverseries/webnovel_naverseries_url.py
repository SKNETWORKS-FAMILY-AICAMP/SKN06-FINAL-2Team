import urllib.request
from bs4 import BeautifulSoup
import json
import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Selenium 설정
driver = webdriver.Chrome()

# 장르별 URL 설정
base_urls = {
    "romance": "https://series.naver.com/novel/categoryProductList.series?categoryTypeCode=genre&genreCode=201",
    "rofan": "https://series.naver.com/novel/categoryProductList.series?categoryTypeCode=genre&genreCode=207",
    "fantasy": "https://series.naver.com/novel/categoryProductList.series?categoryTypeCode=genre&genreCode=202",
    "modernfantasy": "https://series.naver.com/novel/categoryProductList.series?categoryTypeCode=genre&genreCode=208",
    "wuxia": "https://series.naver.com/novel/categoryProductList.series?categoryTypeCode=genre&genreCode=206",
    "mystery": "https://series.naver.com/novel/categoryProductList.series?categoryTypeCode=genre&genreCode=203",
    "lightnovel": "https://series.naver.com/novel/categoryProductList.series?categoryTypeCode=genre&genreCode=205",
    "BL": "https://series.naver.com/novel/categoryProductList.series?categoryTypeCode=genre&genreCode=209"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# ✅ 크롤링 데이터 저장 함수
def extract_novel_links(novel_links):
    extracted_urls = []
    for href in novel_links:
        link = href.find("a")  # a 태그 가져오기
        if link and "href" in link.attrs:
            href_value = link["href"]
            if "categoryProductList.series" not in href_value:  # 불필요한 링크 제외
                full_url = "https://series.naver.com" + href_value
                if full_url not in extracted_urls:  # 중복 방지
                    extracted_urls.append(full_url)
    return extracted_urls

# ✅ json 저장 함수 정의
def save_json(path: str, file_name: str, data: list):
    os.makedirs(path, exist_ok=True)
    with open(f"{path}/{file_name}", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ✅ 장르별 크롤링 실행
DATA_DIR = "webnovelseries_url"
for genre, base_url in base_urls.items():
    seriesnovel_urls = []
    page = 1
    while True:
        url = f"{base_url}&page={page}"
        req = urllib.request.Request(url, headers=headers)
        try:
            sourcecode = urllib.request.urlopen(req).read()
            soup = BeautifulSoup(sourcecode, "html.parser")

            novel_links = soup.select("div.comic_lst_thum_wrap ul.comic_top_lst li")
            backup_links = soup.select("div.lst_thum_wrap ul.lst_list li")
            
            if not novel_links and not backup_links:
                logging.info(f"{genre} - 마지막 페이지 도달 ({page - 1}페이지까지 크롤링 완료)")
                break

            if novel_links:
                seriesnovel_urls.extend(extract_novel_links(novel_links))
            else:
                seriesnovel_urls.extend(extract_novel_links(backup_links))
        except Exception as e:
            logging.info(f"{genre} - {page}페이지 크롤링 중 오류 발생")
            break
        
        logging.info(f"{genre} - {page}페이지 크롤링 완료. 현재까지 {len(seriesnovel_urls)}개 URL 수집.")
        page += 1
    
    # 파일 저장
    file_name = f"{genre}.json"
    save_json(DATA_DIR, file_name, seriesnovel_urls)
