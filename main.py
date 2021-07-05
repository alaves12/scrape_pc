from yodobashi import get_yodobashi_info
from biccamera import get_biccamera_info
import pandas as pd

def main():
    yodobashi_info = get_yodobashi_info(express_soldout=False) # Falseで販売終了済みを表示しない
    bic_info = get_biccamera_info(express_soldout=False) # Falseで販売終了済みを表示しない

    pc_infos = yodobashi_info+bic_info

    pc_columuns = ['商品名','値段(円)','メーカー','モニタサイズ(インチ)','CPU性能','ストレージ容量 ※記載なしはSSD','標準メモリ','本体重量(kg)','色']
    pd_data = pd.DataFrame(pc_infos,columns=pc_columuns)
    pd_data_i = pd_data.set_index('商品名')
    pd_data_i.to_csv('pc_info.csv', encoding='utf_8_sig')
    print(pd.DataFrame(pc_infos,columns=pc_columuns))

if __name__=='__main__':
    main()