import requests
from selenium import webdriver
from webdriver_manager.utils import chrome_version
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import pandas as pd
# これをimportしておくことで自分でcheromedriverをインストールする必要がない
import chromedriver_binary
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from concurrent.futures import ThreadPoolExecutor
from functools import partial

class SeleniumSetUp:
    def __init__(self, home_url:str):
        self.op = Options()
        # --headlessだけではOSによって動かない、プロキシが弾かれる、
        # CUI用の省略されたHTMLが帰ってくるなどの障害が出ます。
        # 長いですが、これら6行あって最強かつどんな環境でも動きますので、必ず抜かさないようにしてください。
        self.op.add_argument("no-sandbox")
        self.op.add_argument("--disable-extensions")
        # self.op.add_argument("--headless")
        self.op.add_argument('--disable-gpu')  
        self.op.add_argument('--ignore-certificate-errors')
        self.op.add_argument('--allow-running-insecure-content')
        self.op.add_argument('--disable-web-security')
        self.op.add_argument('--disable-desktop-notifications')
        self.op.add_argument("--disable-extensions")
        self.op.add_argument('--lang=ja')
        self.op.add_argument('--blink-settings=imagesEnabled=false')
        self.op.add_argument('--disable-dev-shm-usage')
        self.op.add_argument('--proxy-server="direct://"')
        self.op.add_argument('--proxy-bypass-list=*')    
        self.op.add_argument('--start-maximized')

        self.home_url = home_url
  

    def driver_set(self):
        driver = webdriver.Chrome(chrome_options = self.op)
        driver.get(self.home_url)
        time.sleep(1)
        return driver

    # 元のタブを閉じて２つ目のタブをメインタブにする
    def tab_move(self, driver, close=True):
        # tab移動
        # driver.window_handles[タブの番号]
        driver.switch_to.window(driver.window_handles[1])
        driver.switch_to.window(driver.window_handles[0])
        if close == True:

            # 初めに開いていたウインドウを閉じる
            driver.close()

            # 新しく開かれたタブを新規にインスタンスウインドウとする これをしないとNosuchElementエラーになる
            driver.switch_to.window(driver.window_handles[0])

        else:
            driver.switch_to.window(driver.window_handles[1])

        return driver

    # 元のタブを閉じて２つ目のタブをメインタブにする
    def tab_return(self, driver, close=True):
        # tab移動
        # driver.window_handles[タブの番号]
        driver.switch_to.window(driver.window_handles[0])
        driver.switch_to.window(driver.window_handles[1])
        if close == True:
            driver.switch_to.window(driver.window_handles[1])
            # 初めに開いていたウインドウを閉じる
            driver.close()

            # 新しく開かれたタブを新規にインスタンスウインドウとする これをしないとNosuchElementエラーになる
            driver.switch_to.window(driver.window_handles[0])

        else:
            driver.switch_to.window(driver.window_handles[0])

        return driver