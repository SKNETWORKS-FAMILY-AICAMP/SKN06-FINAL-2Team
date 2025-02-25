from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium import webdriver
from dotenv import load_dotenv
import logging
import time
import os


def kakao_login(visible, second):
    load_dotenv()
    kakao_id = os.getenv("KAKAO_ID")
    kakao_pw = os.getenv("KAKAO_PWD")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    driver_path = ChromeDriverManager().install()
    service = Service(executable_path=driver_path)
    options = webdriver.ChromeOptions()
    if visible == False:
        options.add_argument("--headless")
    elif visible == True:
        pass
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://page.kakao.com/")

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
    login_selector = r"#mainContent > div > div > form > div.confirm_btn > button.btn_g.highlight.submit"
    driver.find_element(By.CSS_SELECTOR, login_selector).click()

    if second == True:
        # 카카오 2차 인증 대기
        time.sleep(10)
        try:
            continue_selector = r"#mArticle > div > div.wrap_btn > form > button"
            driver.find_element(By.CSS_SELECTOR, continue_selector).click()
            time.sleep(2)
            if driver.current_url == "https://page.kakao.com/":
                logging.info("2차 인증 완료")
            else:
                logging.error("2차 인증 오류")
                driver.quit()
        except Exception as e:
            logging.error(f"2차 인증 오류: {e}", exc_info=True)
            driver.quit()
    else:
        pass
    return driver
