from os import wait
from settup import SeleniumSetUp
import time
from collections import defaultdict
import pandas as pd
from selenium import webdriver
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
 
def g2kg(td):
  kg = 'kg'
  Kg = 'Kg'
  ab = '約'
  kg_result = re.search(f'{kg}|{Kg}',td)
  if kg_result is None:
    td_list = [s for s in re.split(f'g|{ab}',td) if s!='']
    try:
        td = int(td_list[0]) / 1000
        td = str(td)
    except:
      td = td
  else:
    td_list = [s for s in re.split(f'{kg}|{Kg}|{ab}',td) if s!='']
    td = ' '.join(td_list)

  return td

def make_strage_data(td):
  ssd = 'SSD'
  colon = '：'
  space = ' '
  result = re.search(f'{ssd}',td)
  if result:
    td_list = [s for s in re.split(f'{ssd}|{colon}|{space}',td) if s!='']
    td = ' '.join(td_list)
  return td

def get_index(th,td,columuns):

  td_list = td.split('*')
  td = td_list[0]

  rel_dic={
    '商品名':'商品名',
    'メーカー':'メーカー',
    'モニタサイズ':'モニタサイズ(インチ)',
    'CPU':'CPU性能',
    '色':'色',
    'ストレージ':'ストレージ容量 ※記載なしはSSD',
    '本体重量':'本体重量(kg)',
    'メモリ':'標準メモリ'
  }
  col = rel_dic[th]

  if th == 'メーカー':
    b = '（メーカーサイトへ）'
    c = '\u3000'
    td_list = [s for s in re.split(f'{b}|{c}',td) if s!='']
    td = ' '.join(td_list)
    
  elif th == 'メモリ':
    b = 'メモリ：'
    td_list = [s for s in td.split(b) if s!='']
    td = td_list[0]
    
  elif th == '本体重量':
    td = g2kg(td)

  elif th == 'ストレージ':
    td = make_strage_data(td)

  elif th == 'モニタサイズ':
    td_list = td.split('型')
    td = ' '.join(td_list)
  
  idx = columuns.index(col)

  return idx,td

def get_pc_info(driver,wait,path,columuns):
  WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located)
  element = wait.until(EC.element_to_be_clickable((By.XPATH, path)))
  driver.execute_script(f"window.scrollTo(0, '{element.location['y']}');")
  # element = driver.find_element_by_xpath(path)
  element.click()
  
  pc_info = ['']*len(columuns)
  WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located)
  price = driver.find_element_by_xpath('//strong[@itemprop="price"]').get_attribute("content")
  pc_info[1] = price

  info_tags=['商品名','CPU','色','メモリ','モニタサイズ','本体重量','ストレージ','メーカー']
  table_elements = driver.find_elements_by_xpath('//*[@id="bcs_detail"]/table')

  for i in range(len(table_elements)):
    detail_table = f'//*[@id="bcs_detail"]/table[{i+1}]/tbody/tr'
    elements = driver.find_elements_by_xpath(detail_table) # スペック表

    for j in range(len(elements)):
      th_tag = detail_table+f'[{j+1}]/th'
      td_tag = detail_table+f'[{j+1}]/td'

      try:
        th_txt = driver.find_element_by_xpath(th_tag).text # 行の見出し
        if th_txt in info_tags:
          td_txt = driver.find_element_by_xpath(td_tag).text # 行の内容
          index,td_txt = get_index(th_txt,td_txt,columuns)
          pc_info[index] = td_txt
      except:
        th_txt = th_txt
        if th_txt in info_tags:
          td_txt += f'、{driver.find_element_by_xpath(td_tag).text}'
          pc_info[index] = td_txt

  driver.back()
  WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located)
  time.sleep(1)
  
  return pc_info

def get_biccamera_info(express_soldout=False):
  driver_path =  "https://www.biccamera.com/bc/main/"

  selen_setting = SeleniumSetUp(driver_path)
  driver = selen_setting.driver_set()

  driver.implicitly_wait(10)
  WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located)
  wait = WebDriverWait(driver, 10)

  # ノートパソコンカテゴリまで移動
  driver.find_element_by_xpath('//a[contains(text(), "カテゴリから選ぶ")]').click()
  time.sleep(1)
  element = driver.find_element_by_xpath('//a[contains(text(), "パソコン・周辺機器・PCソフト")]')
  webdriver.ActionChains(driver).move_to_element(element).perform()
  time.sleep(1)
  driver.find_element_by_xpath('//*[@id="fmCat2-b"]/div/ul[1]/li[1]/a').click()
  driver.execute_script("window.scrollTo(0,1000);")
  time.sleep(2)
  
  # 画面サイズ指定
  element = driver.find_element_by_xpath('//*[@id="catNav"]/div[5]/div/form/ul/li[5]/label/input')
  webdriver.ActionChains(driver).move_to_element(element).perform()
  element.click()
  time.sleep(2)

  # メモリ指定
  memory_elements = driver.find_elements_by_name('spec_303010_082')
  element = memory_elements[2]
  webdriver.ActionChains(driver).move_to_element(element).perform()
  element.click()

  # 検索
  driver.find_element_by_xpath('//*[@id="specSelectForm"]/p/input').click()

  # 販売終了済みを表示しない
  if not express_soldout:
    driver.find_element_by_xpath('//*[@id="bcs_sold_out_tp2_cond"]').click()

  pc_infos = []
  pc_columuns = ['商品名','値段(円)','メーカー','モニタサイズ(インチ)','CPU性能','ストレージ容量 ※記載なしはSSD','標準メモリ','本体重量(kg)','色']

  while True:
    pc_paths = '/html/body/section/div[2]/div[1]/div[3]/div[2]/form/div/ul/li'
    pc_elements = driver.find_elements_by_xpath(pc_paths)
    for i in range(len(pc_elements)):
    # for i in range(1):
      WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located)
      path = pc_paths+f'[{i+1}]/p[3]/a' # 各アイテムのaタグpathの取得
      pc_inf = get_pc_info(driver,wait,path,columuns=pc_columuns)
      pc_infos.append(pc_inf)

    try:
      element = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "次")]')))
      element = driver.find_element_by_xpath('//a[contains(text(), "次")]')
      webdriver.ActionChains(driver).move_to_element(element).perform()
      element.click()# ページ遷移
    except:
      break

  return pc_infos


if __name__=='__main__':
  info = get_biccamera_info()
  print(info)