# webnovel_kkopage 폴더에서 돌리기
from module.crawling_detail import crawling_detail
from module.login import kakao_login
import logging
import pickle
import json
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True,
)

driver = kakao_login(visible=False, second=True)

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
    with open(f"total_links/{genre}_url.pkl", "rb") as f:
        total_link = pickle.load(f)
    with open(f"ranking_ids/{genre}_url.pkl", "rb") as f:
        ranking_link = pickle.load(f)
    logging.info(f"{genre} 디테일 크롤링 시작")

    webnovels = []
    webnovel = None
    for link in total_link:
        try:
            webnovel = crawling_detail(link, driver)
            logging.info(f"{webnovel["title"]} 크롤링 완료")
            if webnovel["url"] in ranking_link:
                webnovel["ranking"] = ranking_link.index(webnovel["url"]) + 1
        except Exception as e:
            logging.error(f"{link} 크롤링을 완료하지 못했습니다.\n{e}", exc_info=True)
        webnovels.append(webnovel)

    driver.quit()

    error_log = {}
    for novel in webnovels:
        for key, value in novel.items():
            if key == "title" and value == "-":
                logging.info(f"{novel["title"]}, title")
                error_log[total_link.index(novel["url"])] = novel["url"]
            elif key == "synopsis" and value == "-":
                logging.info(f"{novel["title"]}, synopsis")
                error_log[total_link.index(novel["url"])] = novel["url"]
            elif key == "status" and value == "-":
                logging.info(f"{novel["title"]}, status")
                error_log[total_link.index(novel["url"])] = novel["url"]
            elif key == "age_rating" and value not in [
                "전체 이용가",
                "12세 이용가",
                "15세 이용가",
                "19세 이용가",
            ]:
                logging.info(f"{novel["title"]}, age_rating, {value}")
                error_log[total_link.index(novel["url"])] = novel["url"]
            elif key == "price" and value == "-":
                logging.info(f"{novel["title"]}, price")
                error_log[total_link.index(novel["url"])] = novel["url"]
            elif key == "thumbnail" and value == "-":
                logging.info(f"{novel["title"]}, thumbnail")
                error_log[total_link.index(novel["url"])] = novel["url"]
            elif key == "ganre" and value == "-":
                logging.info(f"{novel["title"]}, ganre")
                error_log[total_link.index(novel["url"])] = novel["url"]
            elif key == "view" and value == "-":
                logging.info(f"{novel["title"]}, view")
                error_log[total_link.index(novel["url"])] = novel["url"]
            elif key == "author" and value == "-":
                logging.info(f"{novel["title"]}, author")
                error_log[total_link.index(novel["url"])] = novel["url"]
            elif key == "episode" and value == "-":
                logging.info(f"{novel["title"]}, episode")
                error_log[total_link.index(novel["url"])] = novel["url"]
            else:
                pass

    if len(error_log) == 0:
        logging.info("오류 없음")
    else:
        if not os.path.exists("error"):
            os.mkdir("error")
        with open(f"error\error_log_{genre}.json", "w", encoding="utf-8") as f:
            json.dump(error_log, f, indent=4, ensure_ascii=False)

    if not os.path.exists("detail"):
        os.mkdir("detail")
    with open(f"detail\{genre}.json", "w", encoding="utf-8") as f:
        json.dump(webnovels, f, indent=4, ensure_ascii=False)
    logging.info("저장 완료")
