from module.crawling_detail import crawling_detail
from selenium.webdriver.common.by import By
from module.login import kakao_login
import logging
import pickle
import json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True,
)


genre_names = [
    "fantasy",
    "modern_fantasy",
    "romance",
    "romance_fantasy",
    "martial_arts",
    "bl",
    "drama",
]

for genre in genre_names:
    recrawling = {}  # 다시 크롤링할 작품
    stop_sale = []  # 판매 중지된 작품

    # url 및 데이터 로드
    with open(f"detail/{genre}.json", "r", encoding="utf-8") as f:
        webnovels = json.load(f)
    with open(f"total_links/{genre}_url.pkl", "rb") as f:
        total_link = pickle.load(f)
    try:
        with open(f"error/error_log_{genre}.json", "r", encoding="utp-8") as f:
            error_log = json.load(f)
        recrawling.update(error_log)
    except:
        pass

    # 전처리
    while True:
        # url 링크 확인
        for url, novel in zip(total_link, webnovels):
            if url != novel["url"]:
                recrawling[total_link.index(url)] = url
            for key, value in novel.items():
                if value != "-":
                    if key in ["id", "views", "episode", "comments"] and isinstance(
                        value, str
                    ):
                        novel[key] = int(value)
                    elif key == "rating" and isinstance(value, str):
                        novel[key] = float(value)
                    elif key == "first_episode" and len(value) == 8:
                        novel[key] = "20" + novel["first_episode"] + "."

        if len(recrawling) == 0:
            # 전처리된 파일 다시 저장
            with open(f"detail/{genre}.json", "w", encoding="utf-8") as f:
                json.dump(webnovels, f, indent=4, ensure_ascii=False)
            with open(f"total_links/{genre}_url.pkl", "rb") as f:
                total_link = pickle.load(f)
            logging.info(f"{genre} 전처리 완료")
            break
        else:
            # 판매 중지 / 재크롤링 확인
            for key, value in recrawling:
                driver = kakao_login(visible=True)
                driver.get(value)
                stop_selector = r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.flex.w-320pxr.flex-col > div.flex-1.overflow-hidden.rounded-b-12pxr.bg-bg-a-20.px-24pxr.pt-8pxr > div > div > span"
                try:
                    stop_element = driver.find_element(
                        By.CSS_SELECTOR, stop_selector
                    ).text
                except:
                    stop_element = "판매중"
                if stop_element == "판매중지 된 작품은 구매한 편만 볼 수 있습니다.":
                    stop_sale.append(url)
                else:
                    webnovels[key] = crawling_detail(value)

            # 판매 중지 url 제거
            for stop in stop_sale:
                total_link.remove(stop)
