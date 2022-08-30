from re import S
from turtle import st
import tushare as ts
import configparser
from loguru import logger
import numpy as np
import os

class TushareApi(object):
    def __init__(self) -> None:
        super().__init__()
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        logger.add(f"{__file__}", format="{time} {level} {message}", level="INFO")
        logger.add('tushare.log')
        self.config = configparser.ConfigParser()
        self.config.read(parent_dir + '/config.ini', encoding='utf-8')
        self.pro = ts.pro_api(self.config.get('tushare','token'))

    @staticmethod
    def dataframe_to_list(data_frame):
        temp = np.array(data_frame)
        return temp.tolist()
    @staticmethod
    def dataframe_to_dict(data_frame,key):
        return data_frame.set_index(key).T.to_dict()

    def get_all_stock_basic_info(self) -> list:
        """
        获取所有股票的基本信息[TS代码，股票代码，股票名称，地区，行业，上市日期]
        """
        data = self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
        return self.dataframe_to_list(data)

    def get_single_stock_advanced_info(self,trade_date,ts_code) -> list:
        """
        获取单只股票单日的进阶信息[市盈率，流通股本，总股本，总资产，流动资产，固定资产，公积金，每股公积金，每股收益，每股净资产，市净率，未分配利润，收入同比，利润同比，毛利率，净利润率，股东人数]
        """
        data = self.pro.bak_basic(ts_code=ts_code, trade_date=trade_date, fields='ts_code,pe,float_share,total_share,total_assets,liquid_assets,fixed_assets,reserved,reserved_pershare,eps,bvps,pb,undp,per_undp,rev_yoy,profit_yoy,gpr,npr,holder_num')
        return self.dataframe_to_dict(data,'ts_code')
    
    def get_all_stock_moneyflow(self,trade_date) -> list:
        data = self.pro.moneyflow(trade_date=trade_date)
        return self.dataframe_to_dict(data,'ts_code')
    
if __name__ == '__main__':
    api = TushareApi()
    print(api.get_all_stock_info())
    
