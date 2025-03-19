from selenium.webdriver.common.by import By
import time
import re


# 조회수 처리
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


# 댓글 수 처리
def comment_tran(comment):
    comment = comment.replace(",", "")
    if comment[-1] == "만":
        new_comment = float(comment[:-1])
        new_comment *= 10000
    else:
        new_comment = comment
    return int(new_comment)


# 연재일 처리
def get_update_days(status_element):
    status_pattern_1 = r"(?P<days>[가-힣]) 연재"
    status_pattern_2 = r"(?P<days>[가-힣]), (?P<days2>[가-힣]) 연재"
    status_pattern_3 = r"(?P<days>[가-힣]), (?P<days2>[가-힣]), (?P<days3>[가-힣]) 연재"
    status_pattern_4 = r"(?P<days>[가-힣]), (?P<days2>[가-힣]), (?P<days3>[가-힣]), (?P<days4>[가-힣]) 연재"
    status_pattern_5 = r"(?P<days>[가-힣]), (?P<days2>[가-힣]), (?P<days3>[가-힣]), (?P<days4>[가-힣]), (?P<days5>[가-힣]) 연재"
    status_pattern_6 = r"(?P<days>[가-힣]), (?P<days2>[가-힣]), (?P<days3>[가-힣]), (?P<days4>[가-힣]), (?P<days5>[가-힣]), (?P<days6>[가-힣]) 연재"
    status_pattern_7 = r"(?P<days>[가-힣])~(?P<days2>[가-힣]) 연재"

    day = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
    if status_element == "완결":
        update_days_element = "-"
    elif status_element == "휴재":
        update_days_element = "-"
    else:
        if status_element == "매일 연재":
            update_days_element = (
                "월요일, 화요일, 수요일, 목요일, 금요일, 토요일, 일요일"
            )
            status_element = "연재"
        elif status_element == "연재":
            update_days_element = "-"
        elif re.search(status_pattern_7, status_element):
            idx1 = re.search(status_pattern_7, status_element).group("days") + "요일"
            idx2 = re.search(status_pattern_7, status_element).group("days2") + "요일"
            update_days_element = ", ".join(day[day.index(idx1) : day.index(idx2) + 1])
            status_element = "연재"
        elif re.search(status_pattern_6, status_element):
            update_days_element = (
                re.search(status_pattern_6, status_element).group("days")
                + "요일, "
                + re.search(status_pattern_6, status_element).group("days2")
                + "요일, "
                + re.search(status_pattern_6, status_element).group("days3")
                + "요일, "
                + re.search(status_pattern_6, status_element).group("days4")
                + "요일, "
                + re.search(status_pattern_6, status_element).group("days5")
                + "요일, "
                + re.search(status_pattern_6, status_element).group("days6")
                + "요일"
            )
            status_element = "연재"
        elif re.search(status_pattern_5, status_element):
            update_days_element = (
                re.search(status_pattern_5, status_element).group("days")
                + "요일, "
                + re.search(status_pattern_5, status_element).group("days2")
                + "요일, "
                + re.search(status_pattern_5, status_element).group("days3")
                + "요일, "
                + re.search(status_pattern_5, status_element).group("days4")
                + "요일, "
                + re.search(status_pattern_5, status_element).group("days5")
                + "요일"
            )
            status_element = "연재"
        elif re.search(status_pattern_4, status_element):
            update_days_element = (
                re.search(status_pattern_4, status_element).group("days")
                + "요일, "
                + re.search(status_pattern_4, status_element).group("days2")
                + "요일, "
                + re.search(status_pattern_4, status_element).group("days3")
                + "요일, "
                + re.search(status_pattern_4, status_element).group("days4")
                + "요일"
            )
            status_element = "연재"
        elif re.search(status_pattern_3, status_element):
            update_days_element = (
                re.search(status_pattern_3, status_element).group("days")
                + "요일, "
                + re.search(status_pattern_3, status_element).group("days2")
                + "요일, "
                + re.search(status_pattern_3, status_element).group("days3")
                + "요일"
            )
            status_element = "연재"
        elif re.search(status_pattern_2, status_element):
            update_days_element = (
                re.search(status_pattern_2, status_element).group("days")
                + "요일, "
                + re.search(status_pattern_2, status_element).group("days2")
                + "요일"
            )
            status_element = "연재"
        elif re.search(status_pattern_1, status_element):
            update_days_element = (
                re.search(status_pattern_1, status_element).group("days") + "요일"
            )
            status_element = "연재"
    return status_element, update_days_element


def get_age_rating(driver):
    age_rating_selectors = [
        r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col.overflow-hidden.rounded-12pxr > div.flex.flex-1.flex-col > div > div > div.flex.w-full.flex-col.items-center.rounded-12pxr.bg-bg-a-20 > div.flex.w-full.flex-col.items-center.overflow-hidden > div > div:nth-child(5) > span.text-el-70.break-word-anywhere",
        r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col.overflow-hidden.rounded-12pxr > div.flex.flex-1.flex-col > div > div > div.flex.w-full.flex-col.items-center.rounded-12pxr.bg-bg-a-20 > div.flex.w-full.flex-col.items-center.overflow-hidden > div > div:nth-child(4) > span.text-el-70.break-word-anywhere",
        r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col.overflow-hidden.rounded-12pxr > div.flex.flex-1.flex-col > div > div > div:nth-child(5) > div.flex.w-full.flex-col.items-center.overflow-hidden > div > div:nth-child(5) > span.text-el-70.break-word-anywhere",
        r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col.overflow-hidden.rounded-12pxr > div.flex.flex-1.flex-col > div > div > div:nth-child(5) > div.flex.w-full.flex-col.items-center.overflow-hidden > div > div:nth-child(4) > span.text-el-70.break-word-anywhere",
        r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col.overflow-hidden.rounded-12pxr > div.flex.flex-1.flex-col > div > div > div:nth-child(5) > div.flex.w-full.flex-col.items-center.overflow-hidden > div > div:nth-child(6) > span.text-el-70.break-word-anywhere",
        r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col.overflow-hidden.rounded-12pxr > div.flex.flex-1.flex-col > div > div > div:nth-child(4) > div.flex.w-full.flex-col.items-center.overflow-hidden > div > div:nth-child(6) > span.text-el-70.break-word-anywhere",
        r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col.overflow-hidden.rounded-12pxr > div.flex.flex-1.flex-col > div > div > div:nth-child(4) > div.flex.w-full.flex-col.items-center.overflow-hidden > div > div:nth-child(5) > span.text-el-70.break-word-anywhere",
        r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col.overflow-hidden.rounded-12pxr > div.flex.flex-1.flex-col > div > div > div:nth-child(4) > div.flex.w-full.flex-col.items-center.overflow-hidden > div > div:nth-child(4) > span.text-el-70.break-word-anywhere",
    ]
    for age_rating_selector in age_rating_selectors:
        try:
            age_rating_element = driver.find_element(
                By.CSS_SELECTOR, age_rating_selector
            ).text
            if age_rating_element in [
                "전체이용가",
                "12세이용가",
                "15세이용가",
                "19세이용가",
            ]:
                break
        except:
            age_rating_element = "-"
    age_rating_pattern = r"(?P<age>[0-9]+세)(?P<other>이용가)"
    if age_rating_element == "전체이용가":
        age_rating_element = "전체 이용가"
    elif re.search(age_rating_pattern, age_rating_element):
        age_rating_element = (
            re.search(age_rating_pattern, age_rating_element).group("age")
            + " "
            + re.search(age_rating_pattern, age_rating_element).group("other")
        )

    return age_rating_element


# detail 크롤링
def crawling_detail(url, driver):
    webnovel = {}
    URL = url + "?tab_type=about"
    driver.get(URL)
    time.sleep(1)
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

    webnovel["status"], webnovel["update_days"] = get_update_days(status_element)

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

    try:
        description_selector = r'//*[@id="__next"]/div/div[2]/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[2]/div/div[1]/span'
        description_element = driver.find_element(By.XPATH, description_selector).text
    except:
        description_element = "-"
    webnovel["synopsis"] = description_element

    try:
        keywords_selector = r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col.overflow-hidden.rounded-12pxr > div.flex.flex-1.flex-col > div > div > div:nth-child(2) > div.flex.w-full.flex-col.items-center.overflow-hidden > div"

        keywords_element = driver.find_element(By.CSS_SELECTOR, keywords_selector).text
        keywords_element = keywords_element.replace("#", "")
        keywords_element = keywords_element.split("\n")
        keywords_element = ", ".join(keywords_element)
    except:
        keywords_element = "-"
    webnovel["keywords"] = keywords_element

    try:
        author_selector = r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.flex.w-320pxr.flex-col > div.rounded-t-12pxr.bg-bg-a-20 > div > div.relative.px-18pxr.text-center.bg-bg-a-20.mt-24pxr > a > div > span.font-small2.mb-6pxr.text-ellipsis.text-el-70.opacity-70.break-word-anywhere.line-clamp-2"
        author_element = driver.find_element(By.CSS_SELECTOR, author_selector).text
    except:
        author_element = "-"
    webnovel["author"] = author_element

    webnovel["age_rating"] = get_age_rating(driver)

    free_selector = r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.flex.w-320pxr.flex-col > div.rounded-t-12pxr.bg-bg-a-20 > div > div.relative.overflow-hidden.h-326pxr.w-320pxr.pt-40pxr > div.relative.h-full.min-h-\[inherit\] > div > div > div.flex.flex-col.items-start.space-y-2pxr.absolute.left-4px.top-4px.z-10 > div > span"
    wait_selector = r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.flex.w-320pxr.flex-col > div.flex-1.overflow-hidden.rounded-b-12pxr.bg-bg-a-20.px-24pxr.pt-8pxr > div.mb-8pxr.flex.flex-col.space-y-8pxr > div > div.flex.h-48px.cursor-pointer.items-center.justify-between.px-16pxr > div.flex.flex-wrap.under-320-view\:max-w-\[96px\].under-320-view\:flex-col > span.font-small2-bold.mr-4pxr.text-ellipsis.text-el-70.line-clamp-1 > span"
    try:
        driver.find_element(By.CSS_SELECTOR, free_selector)
        price_element = driver.find_element(By.CSS_SELECTOR, free_selector).text
        price_element = price_element
    except:
        try:
            driver.find_element(By.CSS_SELECTOR, wait_selector)
            price_element = driver.find_element(By.CSS_SELECTOR, wait_selector).text

            price_pattern = r"[0-9][가-힣]+"
            price = re.search(price_pattern, price_element)
            price = "기다리면 무료"
            price_element = price
        except:
            price_element = "유료"
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

    try:
        comment_selector = r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col.overflow-hidden.rounded-12pxr > div.flex-1.flex.flex-col > div.mt-4pxr.flex.min-h-200pxr.flex-1.flex-col.overflow-hidden.rounded-12pxr.bg-bg-a-20 > div > div.flex.h-44pxr.w-full.flex-row.items-center.justify-between.px-18pxr.bg-bg-a-20 > div.flex.h-full.flex-1.items-center.space-x-8pxr > span"
        comment_element = driver.find_element(By.CSS_SELECTOR, comment_selector).text
        comment_element = comment_element.strip("전체 ")
        comment_element = comment_tran(comment_element)
    except:
        comment_element = "-"
    webnovel["comments"] = comment_element

    sort_selector = r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col.overflow-hidden.rounded-12pxr > div.flex-1.flex.flex-col > div.rounded-b-12pxr.bg-bg-a-20 > div.flex.h-44pxr.w-full.flex-row.items-center.justify-between.bg-bg-a-20.px-18pxr > div.relative.flex.h-full.items-center.space-x-16pxr.ml-16pxr > div:nth-child(2)"
    sort_element = driver.find_element(By.CSS_SELECTOR, sort_selector)
    if sort_element.text != "첫화부터":
        sort_element.click()
        first_sort = r"body > div.fixed.inset-0.z-100.flex.justify-center > div.z-100.flex.flex-col.bg-bg-b-20.use-gpu.foldable\:max-h-9\/10.foldable\:w-360pxr.foldable\:self-center.foldable\:rounded-16pxr.max-h-9\/10.w-360pxr.self-center.rounded-16pxr.pt-20pxr > div.overflow-y-auto.scrollbar-hide > div.pb-20pxr.mx-24pxr > div:nth-child(1)"
        driver.find_element(By.CSS_SELECTOR, first_sort).click()
    time.sleep(1)
    try:
        first_episode_selector = r"#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1.flex-col > div > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col.overflow-hidden.rounded-12pxr > div.flex-1.flex.flex-col > div.rounded-b-12pxr.bg-bg-a-20 > div.flex.min-h-\[250px\].flex-col.justify-center > div.min-h-364pxr > ul > li:nth-child(1) > div > div > a > div > div.flex.flex-col.pr-14pxr > div.line-clamp-1.text-ellipsis.font-x-small1.h-16pxr.text-el-50 > span"
        first_episode_element = driver.find_element(
            By.CSS_SELECTOR, first_episode_selector
        ).text
    except:
        first_episode_element = "-"
    webnovel["first_episode"] = first_episode_element

    return webnovel
