# sample 크롤링
# crawling 폴더에서 실행하는 기준으로 작성함
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium import webdriver
from dotenv import load_dotenv
import pickle
import json
import time
import re
import os

load_dotenv()
kakao_id = os.getenv("KAKAO_ID")
kakao_pw = os.getenv("KAKAO_PWD")

driver_path = ChromeDriverManager().install()
service = Service(executable_path=driver_path)
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=service, options=options)
driver.get("https://page.kakao.com/menu/10011")

# 로그인처리
login_icon = r"#__next > div > div.sticky.inset-x-0.left-0.top-0.z-100.flex.w-full.flex-col.items-center.justify-center.bg-bg-a-10 > div > div.flex.h-pc_header_height_px.w-1200pxr.items-center.px-30pxr > div.mr-16pxr.flex.shrink-0.items-center.justify-end.space-x-24pxr > button.pr-16pxr"
driver.find_element(By.CSS_SELECTOR, login_icon).click()
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

# 카카오 2차 인증 대기
time.sleep(20)
try:
    continue_selector = r"#mArticle > div > div.wrap_btn > form > button"
    driver.find_element(By.CSS_SELECTOR, continue_selector).click()
    print("2차 인증 완료")
except:
    print("2차 인증 오류")
    driver.quit()

# id 추출
URL_ids = [
    "https://page.kakao.com/menu/10011/screen/91",
    "https://page.kakao.com/menu/10011/screen/64",
    "https://page.kakao.com/menu/10011/screen/70",
    "https://page.kakao.com/menu/10011/screen/100",
    "https://page.kakao.com/menu/10011/screen/92",
    "https://page.kakao.com/menu/10011/screen/68",
    "https://page.kakao.com/menu/10011/screen/77",
]


# URL 크롤링 함수 정의
def crawling_url(url):
    link_list = []
    driver.get(url)
    time.sleep(5)
    link = "#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div > div.flex.grow.flex-col.pt-32pxr > div:nth-child(5) > div > div.flex.w-full.grow.flex-col > div > div > div > div:nth-child({id}) > div > a"

    for i in range(1, 11):
        idx = i + 1
        link_selector = link.format(id=idx)

        link_element = driver.find_element(By.CSS_SELECTOR, link_selector)
        link_meta = link_element.get_attribute("href")
        link_list.append(link_meta)
    return link_list


total_link = []
for idx, url in enumerate(URL_ids):
    link_list = []
    link_list = crawling_url(url)
    total_link.append(link_list)
    print(f"{url} 크롤링 완료")
with open("kakao_wn_url.pkl", "wb") as f:
    pickle.dump(total_link, f)


# 조회수 처리 함수
def view_tran(view):
    view = view.replace(",", "")
    if view[-1] in "억":
        new_view = float(view[:-1])
        new_view *= 100000000
    elif view[-1] == "만":
        new_view = float(view[:-1])
        new_view *= 10000
    else:
        new_view = view
    return int(new_view)


# 크롤링 함수 정의
def crawling_detail(url):
    webnovel = {}
    URL = url + "?tab_type=about"
    driver.get(URL)
    time.sleep(2)
    id_pattern = r"[0-9]+"
    id = re.search(id_pattern, url).group()
    webnovel["id"] = int(id)

    webnovel["type"] = "웹소설"
    webnovel["platform"] = "카카오페이지"

    try:
        title_selector = r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.flex.w-320pxr.flex-col > div.rounded-t-12pxr.bg-bg-a-20 > div > div.relative.px-18pxr.text-center.bg-bg-a-20.mt-24pxr > a > div > span.font-large3-bold.mb-3pxr.text-ellipsis.break-all.text-el-70.line-clamp-2"
        title_element = driver.find_element(By.CSS_SELECTOR, title_selector).text
    except:
        title_element = "-"
    webnovel["title"] = title_element

    try:
        status_selector = r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.flex.w-320pxr.flex-col > div.rounded-t-12pxr.bg-bg-a-20 > div > div.relative.px-18pxr.text-center.bg-bg-a-20.mt-24pxr > a > div > div.mt-6pxr.flex.items-center > span"
        status_element = driver.find_element(By.CSS_SELECTOR, status_selector).text
    except:
        status_element = "-"
    webnovel["status"] = status_element

    try:
        thumbnail_selector = r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.flex.w-320pxr.flex-col > div.rounded-t-12pxr.bg-bg-a-20 > div > div.relative.overflow-hidden.h-326pxr.w-320pxr.pt-40pxr > div.relative.h-full.min-h-\[inherit\] > div > div > div.jsx-794524088.image-container.relative > img"
        thumbnail_element = driver.find_element(
            By.CSS_SELECTOR, thumbnail_selector
        ).get_attribute("src")
    except:
        thumbnail_element = "-"
    webnovel["thumbnail"] = thumbnail_element

    try:
        genre_selector = r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.flex.w-320pxr.flex-col > div.rounded-t-12pxr.bg-bg-a-20 > div > div.relative.px-18pxr.text-center.bg-bg-a-20.mt-24pxr > a > div > div.flex.h-16pxr.items-center.justify-center.all-child\:font-small2.\[\&\>\*\:not\(\:last-child\)\]\:mr-10pxr > div:nth-child(1) > div > span:nth-child(3)"
        genre_element = driver.find_element(By.CSS_SELECTOR, genre_selector).text
    except:
        genre_element = "-"
    webnovel["genre"] = genre_element

    try:
        views_selector = r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.flex.w-320pxr.flex-col > div.rounded-t-12pxr.bg-bg-a-20 > div > div.relative.px-18pxr.text-center.bg-bg-a-20.mt-24pxr > a > div > div.flex.h-16pxr.items-center.justify-center.all-child\:font-small2.\[\&\>\*\:not\(\:last-child\)\]\:mr-10pxr > div:nth-child(2) > span"
        views_element = driver.find_element(By.CSS_SELECTOR, views_selector).text
        views_element = view_tran(views_element)
    except:
        views_element = "-"
    webnovel["views"] = views_element

    try:
        rating_selector = r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.flex.w-320pxr.flex-col > div.rounded-t-12pxr.bg-bg-a-20 > div > div.relative.px-18pxr.text-center.bg-bg-a-20.mt-24pxr > a > div > div.flex.h-16pxr.items-center.justify-center.all-child\:font-small2.\[\&\>\*\:not\(\:last-child\)\]\:mr-10pxr > div:nth-child(3) > span"
        rating_element = driver.find_element(By.CSS_SELECTOR, rating_selector).text
        rating_element = float(rating_element)
    except:
        rating_element = "-"
    webnovel["rating"] = rating_element

    webnovel["like"] = "-"

    try:
        description_selector = r'//*[@id="__next"]/div/div[2]/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[2]/div/div[1]/span'
        description_element = driver.find_element(By.XPATH, description_selector).text
        description_element = description_element.replace("\n", " ")
        description_element = description_element.replace("  ", " ")
    except:
        description_element = "-"
    webnovel["description"] = description_element

    try:
        keywords_selector = r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col.overflow-hidden.rounded-12pxr > div.flex.flex-1.flex-col > div > div > div:nth-child(2) > div.flex.w-full.flex-col.items-center.overflow-hidden > div"

        keywords_element = driver.find_element(By.CSS_SELECTOR, keywords_selector).text
        keywords_element = keywords_element.replace("#", "")
        keywords_element = keywords_element.split("\n")
    except:
        keywords_element = "-"
    webnovel["keywords"] = keywords_element

    try:
        author_selector = r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col.overflow-hidden.rounded-12pxr > div.flex.flex-1.flex-col > div > div > div:nth-child(5) > div.flex.w-full.flex-col.items-center.overflow-hidden > div > div:nth-child(1) > span.text-el-70.break-word-anywhere"
        author_element = driver.find_element(By.CSS_SELECTOR, author_selector).text
    except:
        try:
            author_selector = r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col.overflow-hidden.rounded-12pxr > div.flex.flex-1.flex-col > div > div > div:nth-child(4) > div.flex.w-full.flex-col.items-center.overflow-hidden > div > div:nth-child(1) > span.text-el-70.break-word-anywhere"
            author_element = driver.find_element(By.CSS_SELECTOR, author_selector).text
        except:
            try:
                author_selector = r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col.overflow-hidden.rounded-12pxr > div.flex.flex-1.flex-col > div > div > div.flex.w-full.flex-col.items-center.rounded-12pxr.bg-bg-a-20 > div.flex.w-full.flex-col.items-center.overflow-hidden > div > div:nth-child(1) > span.text-el-70.break-word-anywhere"
                author_element = driver.find_element(
                    By.CSS_SELECTOR, author_selector
                ).text
            except:
                try:
                    author_selector = r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.flex.w-320pxr.flex-col > div.rounded-t-12pxr.bg-bg-a-20 > div > div.relative.px-18pxr.text-center.bg-bg-a-20.mt-24pxr > a > div > span.font-small2.mb-6pxr.text-ellipsis.text-el-70.opacity-70.break-word-anywhere.line-clamp-2"
                    author_element = driver.find_element(
                        By.CSS_SELECTOR, author_selector
                    ).text
                except:
                    author_element = "-"
    webnovel["author"] = author_element

    webnovel["illustrator"] = "-"

    webnovel["original"] = "-"

    try:
        age_rating_selector = r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col.overflow-hidden.rounded-12pxr > div.flex.flex-1.flex-col > div > div > div.flex.w-full.flex-col.items-center.rounded-12pxr.bg-bg-a-20 > div.flex.w-full.flex-col.items-center.overflow-hidden > div > div:nth-child(4) > span.text-el-70.break-word-anywhere"
        age_rating_element = driver.find_element(
            By.CSS_SELECTOR, age_rating_selector
        ).text
    except:
        try:
            age_rating_selector = r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col.overflow-hidden.rounded-12pxr > div.flex.flex-1.flex-col > div > div > div:nth-child(5) > div.flex.w-full.flex-col.items-center.overflow-hidden > div > div:nth-child(4) > span.text-el-70.break-word-anywhere"
            age_rating_element = driver.find_element(
                By.CSS_SELECTOR, age_rating_selector
            ).text
        except:
            age_rating_element = "-"
    webnovel["age_rating"] = age_rating_element

    free_selector = r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.flex.w-320pxr.flex-col > div.rounded-t-12pxr.bg-bg-a-20 > div > div.relative.overflow-hidden.h-326pxr.w-320pxr.pt-40pxr > div.relative.h-full.min-h-\[inherit\] > div > div > div.flex.flex-col.items-start.space-y-2pxr.absolute.left-4px.top-4px.z-10 > div > span"
    wait_selector = r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.flex.w-320pxr.flex-col > div.flex-1.overflow-hidden.rounded-b-12pxr.bg-bg-a-20.px-24pxr.pt-8pxr > div.mb-8pxr.flex.flex-col.space-y-8pxr > div > div.flex.h-48px.cursor-pointer.items-center.justify-between.px-16pxr > div.flex.flex-wrap.under-320-view\:max-w-\[96px\].under-320-view\:flex-col > span.font-small2-bold.mr-4pxr.text-ellipsis.text-el-70.line-clamp-1 > span"
    try:
        driver.find_element(By.CSS_SELECTOR, free_selector)
        price_element = driver.find_element(By.CSS_SELECTOR, free_selector).text
        price_element = list(price_element)
    except:
        try:
            driver.find_element(By.CSS_SELECTOR, wait_selector)
            price_element = driver.find_element(By.CSS_SELECTOR, wait_selector).text

            price_pattern = r"[0-9][가-힣]+"
            price = re.search(price_pattern, price_element)
            price = price.group() + " 기다리면 무료"
            price_element = [price]
        except:
            price_element = ["유료", "100캐시"]
    webnovel["price"] = price_element

    webnovel["url"] = url

    URL = url + "?tab_type=overview"
    driver.get(URL)
    time.sleep(1)
    try:
        episode_selector = r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col.overflow-hidden.rounded-12pxr > div.flex-1.flex.flex-col > div.rounded-b-12pxr.bg-bg-a-20 > div.flex.h-44pxr.w-full.flex-row.items-center.justify-between.bg-bg-a-20.px-18pxr > div.flex.h-full.flex-1.items-center.space-x-8pxr > span"
        episode_element = driver.find_element(By.CSS_SELECTOR, episode_selector).text
        episode_element = episode_element.strip("전체 ")
        episode_element = episode_element.replace(",", "")
        episode_element = int(episode_element)
    except:
        episode_element = "-"
    webnovel["episode"] = episode_element

    return webnovel


webnovels = []
with open("kakao_wn_url.pkl", "rb") as f:
    link_list = pickle.load(f)
for link in link_list:
    try:
        webnovel = crawling_detail(link)
        webnovels.append(webnovel)
    except:
        print(f"{link} 크롤링을 완료하지 못했습니다.")

driver.quit()

for novel in webnovels:
    error_log = set()
    for key, value in novel.items():
        if key == "title" and value == "-":
            print(novel)
            error_log.add(novel["url"])
        if key == "discription" and value == "-":
            print(novel)
            error_log.add(novel["url"])
        if key == "status" and value == "-":
            print(novel)
            error_log.add(novel["url"])
        if key == "price" and value == "-":
            print(novel)
            error_log.add(novel["url"])
        if key == "age_rating" and value == "-":
            print(novel)
            error_log.add(novel["url"])
        if key == "thumbnail" and value == "-":
            print(novel)
            error_log.add(novel["url"])
        if key == "ganre" and value == "-":
            print(novel)
            error_log.add(novel["url"])
        if key == "view" and value == "-":
            print(novel)
            error_log.add(novel["url"])
        if key == "author" and value == "-":
            print(novel)
            error_log.add(novel["url"])
        if key == "episode" and value == "-":
            print(novel)
            error_log.add(novel["url"])

if len(error_log) == 0:
    print("오류 없음")
else:
    with open("error_log.json", "w") as f:
        json.dump(error_log, f, indent=4, ensure_ascii=False)

with open("..\Raw_DB\kp_wn_sample.json", "w") as f:
    json.dump(webnovels, f, indent=4, ensure_ascii=False)
print("저장 완료")
