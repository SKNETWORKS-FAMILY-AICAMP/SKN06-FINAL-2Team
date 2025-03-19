from selenium.webdriver.common.by import By
import logging
import time


def crawling_url(cnt, type, driver):
    link_list = []
    time.sleep(1)
    if type == "ranking":
        link = "#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div > div > div > div > div.flex.w-full.grow.flex-col > div.px-11pxr > div > div > div:nth-child({id}) > div > a"
        unit = 50
    elif type == "total":
        link = "#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div > div.flex.grow.flex-col.pt-32pxr > div.mb-4pxr.flex-col > div > div.flex.grow.flex-col > div > div > div > div:nth-child({id}) > div > a"
        unit = 24
    min_count = cnt * unit
    max_count = min_count + unit
    logging.info(f"{min_count+1}부터 {max_count}까지 크롤링합니다")
    for i in range(min_count, max_count):
        idx = i + 1
        link_selector = link.format(id=idx)
        try:
            link_element = driver.find_element(By.CSS_SELECTOR, link_selector)
            link_meta = link_element.get_attribute("href")
            link_list.append(link_meta)
        except:
            break
    return link_list
