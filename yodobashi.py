from settup import SeleniumSetUp
import time
from collections import defaultdict
import pandas as pd
import re 

# comment
def make_strage_data(th,td):
  if th == 'ストレージ容量（SSD）':
    td = td
  else:
    td += td + ' (HDD)'
  return th,td

def g2kg(td): # gからkgに
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


def get_index(th,td,columuns):
  rel_dic={
    '液晶モニターサイズ':'モニタサイズ(インチ)',
    'CPU':'CPU性能',
    'カラー':'色',
    'ストレージ容量（SSD）':'ストレージ容量 ※記載なしはSSD',
    'ストレージ容量（HDD）':'ストレージ容量 ※記載なしはSSD',
    '重量':'本体重量(kg)',
    '標準メモリ':'標準メモリ'
  }
  col = rel_dic[th]
  idx = columuns.index(col)

  if th in ['ストレージ容量（SSD）','ストレージ容量（HDD）']:
    th,td = make_strage_data(th,td)

  elif th == '液晶モニターサイズ':
    td_list = td.split('型')
    td = ' '.join(td_list)

  elif th == '重量':
    td = g2kg(td)
    
  return idx,td

def get_pc_info(driver,selen,path,columuns):
  driver.find_element_by_xpath(path).click()
  selen.tab_move(driver=driver,close=False)

  pc_info = ['']*len(columuns)

  name = driver.find_element_by_xpath('//*[@id="products_maintitle"]/span').text

  try:
    price = driver.find_element_by_xpath('//*[@id="js_scl_unitPrice"]').text
  except:
    price = driver.find_element_by_xpath('//span[contains(text(), "￥")]').text

  maker = driver.find_element_by_xpath('//*[@id="js_makerTD"]/a').text

  price = [s for s in price.split("￥") if s!='']
  price = price[0]
  
  pc_info[0] = name
  pc_info[1] = price
  pc_info[2] = maker

  info_tags=['CPU','カラー','標準メモリ','液晶モニターサイズ','重量','ストレージ容量（SSD）','ストレージ容量（HDD）']
  table_elements = driver.find_elements_by_xpath('//*[@id="js_specArea"]/div/div[1]/table')

  for i in range(len(table_elements)):
    detail_table = f'//*[@id="js_specArea"]/div/div[1]/table[{i+1}]/tbody/tr' 
    elements = driver.find_elements_by_xpath(detail_table) # スペック表

    for j in range(len(elements)):
      th_tag = detail_table+f'[{j+1}]/th'
      td_tag = detail_table+f'[{j+1}]/td'

      try:
        th_txt = driver.find_element_by_xpath(th_tag).text
        if th_txt in info_tags:
          td_txt = driver.find_element_by_xpath(td_tag).text # 行の内容
          index,td_txt = get_index(th_txt,td_txt,columuns)
          
          pc_info[index] = td_txt
      except:
        th_txt = th_txt
        if th_txt in info_tags:
          td_txt += f'、{driver.find_element_by_xpath(td_tag).text}'
          pc_info[index] = td_txt
  selen.tab_return(driver,close=True)
  
  return pc_info

def get_yodobashi_info(express_soldout=False):
  driver_path =  "https://www.yodobashi.com"

  selen_setting = SeleniumSetUp(driver_path)
  driver = selen_setting.driver_set()

  # ノートパソコンカテゴリまで移動
  driver.find_element_by_xpath('//*[@id="footer"]/div/div/div[1]/div[1]/div/div/div[1]/ul/li[2]/a').click()
  driver.find_element_by_xpath('//a[contains(text(), "ノートパソコン")]').click()
  driver.find_element_by_xpath('//*[@id="contents"]/div/div[1]/div/div[1]/div/a[2]').click()

  # 画面サイズ指定
  driver.find_element_by_id("categoryFacetD1_3").click()

  # メモリ指定
  driver.find_element_by_xpath('//*[@id="js_facetSpecList"]/div[14]/ul/li[1]/div/div/a/i').click()
  time.sleep(1)
  driver.find_element_by_id("categoryFacetD13_1").click()

  # 検索
  driver.find_element_by_id("js_facetSpecFilterButton").click()

  # 販売終了済みを表示
  if express_soldout:
    driver.find_element_by_xpath('//*[@id="js_dispDiscontinuedSearchConditionAreaCheckbox"]').click()

  pc_infos = []
  pc_columuns = ['商品名','値段(円)','メーカー','モニタサイズ(インチ)','CPU性能','ストレージ容量 ※記載なしはSSD','標準メモリ','本体重量(kg)','色']

  
  while True:
    pc_paths = '//*[@id="listContents"]/div[3]/div'
    pc_elements = driver.find_elements_by_xpath(pc_paths)

    for i in range(len(pc_elements)):
      path = '//*[@id="listContents"]/div[3]/div'+f'[{i+1}]/a' # 各アイテムのaタグpathの取得
      pc_inf = get_pc_info(driver,selen_setting,path,columuns=pc_columuns)
      pc_infos.append(pc_inf)
    
    try:
      driver.find_element_by_class_name("next").click() # ページ遷移
    except:
      break

  return pc_infos


if __name__=='__main__':
  info = get_yodobashi_info()
  print(info)