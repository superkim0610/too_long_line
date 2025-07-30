import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import pandas as pd
from tqdm import tqdm

class NaverMapCrawler:
    def __init__(self, headless=False):
        self.data = []
        self.date_str = None

        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--lang=ko-KR")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument('--disable-dev-shm-usage')
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        }
        options.add_experimental_option("prefs", prefs)

        self.driver = uc.Chrome(options=options, headless=headless)
        self.wait = WebDriverWait(self.driver, timeout=10, poll_frequency=0.2)

    def set_date(self):
        self.date_str = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    def search_query(self, query):
        # 검색 시간이 파일명에 반영됨
        self.set_date()

        driver = self.driver
        wait = self.wait

        query.replace(' ', '%20')
        url = f"https://map.naver.com/p/search/{query}"
        driver.get(url)

        wait.until(EC.presence_of_element_located((By.ID, "searchIframe")))

    def save(self):
        raw_path = "Database/raw"
        if not os.path.exists(raw_path):
            os.makedirs(raw_path)

        df = pd.DataFrame(self.data)
        df.to_csv(f"{raw_path}/{self.date_str}_raw.csv", index=False)

        # print("[successfully saved]")

    def _run(self, page):
        driver = self.driver
        wait = self.wait

        # dynamic scroll
        search_iframe = driver.find_element(By.ID, "searchIframe")
        driver.switch_to.frame(search_iframe)

        restaurant_list_scroll_container = driver.find_element(By.ID, '_pcmap_list_scroll_container')

        scroll_num = 0
        prev_scroll_remain = None
        while True:
            scroll_top = driver.execute_script("return arguments[0].scrollTop", restaurant_list_scroll_container)
            scroll_height = driver.execute_script("return arguments[0].scrollHeight", restaurant_list_scroll_container)
            scroll_remain = scroll_height - scroll_top
            # print(f"scroll_num: {scroll_num}, scroll_height: {scroll_height}, scroll_remain: {scroll_remain}")

            # end-of-loop
            if scroll_remain <= 0 or scroll_num >= 20 or prev_scroll_remain == scroll_remain:
                break

            # do scroll
            for _ in range(10):
                driver.execute_script(f"arguments[0].scrollTop += {scroll_remain // 10}",
                                      restaurant_list_scroll_container)
                time.sleep(0.1)

            scroll_num += 1
            prev_scroll_remain = int(scroll_remain)

        # check each restaurant info, review_data
        restaurant_a_list = driver.find_elements(By.CSS_SELECTOR, "div.CHC5F > div.bSoi3 > a")

        for a in tqdm(restaurant_a_list, desc=f"page={page}"):
            n_data = dict()

            a.click()

            # delay
            driver.switch_to.default_content()
            restaurant_iframe_locator = (By.XPATH, '//*[@id="entryIframe"]')
            try:
                wait.until(
                    EC.frame_to_be_available_and_switch_to_it(restaurant_iframe_locator)
                )
            except:
                time.sleep(2)
                # driver.switch_to.default_content()

                driver.switch_to.frame(driver.find_element(*restaurant_iframe_locator))
                print('switched')

            # get info
            # restaurant_info : restaurant_name, restaurant_category, restaurant_address, restaurant_tel
            # review_data : total, key...

            # get restaurant_info
            for i in [
                ["restaurant_name", (By.CSS_SELECTOR, "#_title > div > span.GHAhO")],
                ["restaurant_category", (By.CSS_SELECTOR, "#_title > div > span.lnJFt")],
                ["restaurant_address", (By.CSS_SELECTOR, "div > a > span.LDgIH")],
                ["restaurant_tel", (By.CSS_SELECTOR, "div > span.xlx7Q")],
            ]:
                try:
                    # print(i[0], driver.find_element(*i[1]).text)
                    n_data[i[0]] = driver.find_element(*i[1]).text
                    # exec(f'{i[0]}="{driver.find_element(*i[1]).text}"')
                except:
                    print(i[0], None)
                    n_data[i[0]] = None
                    # exec(f"{i[0]}=None")

            # get review_data
            driver.switch_to.default_content()
            driver.switch_to.frame(driver.find_element(*restaurant_iframe_locator))

            review_button = None
            for i in range(1, 6):
                review_button = driver.find_element(By.XPATH, f'//a[@data-index="{i}"]')
                if "리뷰" in review_button.text:
                    break
            review_button.click()
            time.sleep(1)

            try:
                review_total = int(driver.find_element(By.XPATH, '//div[@class="jypaX"]/em').text[:-1].replace(",", ""))
            except:
                review_total = None

            # press review_showmore_button
            while True:
                review_showmore_button = driver.find_elements(By.XPATH, '//div[@class="IUbn3"]/a')

                if len(review_showmore_button) == 0:
                    break

                review_showmore_button[0].click()
                time.sleep(0.2)

            review_li_list = driver.find_elements(By.XPATH, '//ul[@class="K4J9r"]/li')

            review_num = {"total_num": review_total}
            for review_li in review_li_list:
                l = review_li.text.strip().split("\n")
                review_keyword = l[0].replace("\"", "")
                review_keyword_num = int(l[2])
                # print(review_keyword, review_keyword_num)
                review_num[review_keyword] = review_keyword_num

            n_data.update({
                "review_num": review_num,
            })
            self.data.append(n_data)
            self.save()

            driver.switch_to.default_content()
            driver.switch_to.frame(search_iframe)

        driver.switch_to.default_content()

    def run(self, region):
        driver = self.driver
        wait = self.wait

        # search query
        self.search_query(f"{region} 음식점")



        for page in tqdm(range(1, 6), desc=f"{region}"):
            if page != 1:
                search_iframe = driver.find_element(By.ID, "searchIframe")
                driver.switch_to.frame(search_iframe)
                driver.find_elements(By.XPATH, '//div[@class="zRM9F"]/a')[page-1].click()
                driver.switch_to.default_content()

            self._run(page)




if __name__ == '__main__':
    c = NaverMapCrawler()
    c.run("대치동")