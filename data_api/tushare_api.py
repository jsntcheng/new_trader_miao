from cgitb import reset
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

    @staticmethod
    def reset_dict_key(old_dict, reset_dict):
        """
        重置字典的key
        """
        new_dict = {}
        for key in old_dict.keys():
            new_dict[reset_dict[key]] = old_dict[key]
        return new_dict

    def get_all_stock_basic_info(self) -> list:
        """
        获取所有股票的基本信息[TS代码，股票代码，股票名称，地区，行业，上市日期]
        """
        data = self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
        return self.dataframe_to_dict(data,'ts_code')

    def get_single_stock_advanced_info(self,ts_code='',trade_date='') -> dict:
        """
        获取所有股票单日的进阶信息
            :param ts_code: 股票代码
            :param trade_date: 交易日期
            :return: 返回一个字典，key为ts_code，value为各个字段值
            Examples
            --------
            >>> .get_single_stock_advanced_info(ts_code='000001.SZ',trade_date='20190806')
            {'000001.SZ': {'pe': 7.71,                   # 市盈率（动）
                           'float_share': 171.7,         # 流通股本（亿）
                           'total_share': 171.7,         # 总股本（亿）
                           'total_assets': 35301.7984,   # 总资产（亿）
                           'liquid_assets': 0.0,         # 流动资产（亿）
                           'fixed_assets': 106.23,       # 固定资产（亿）
                           'reserved': 564.65,           # 公积金
                           'reserved_pershare': 3.29,    # 每股公积金
                           'eps': 0.38,                  # 每股收益
                           'bvps': 13.45,                # 每股净资产
                           'pb': 0.99,                   # 市净率
                           'undp': 1016.09,              # 未分配利润
                           'per_undp': 5.92,             # 每股未分配利润
                           'rev_yoy': 15.88,             # 收入同比（%）
                           'profit_yoy': 12.9,           # 利润同比（%）
                           'gpr': 0.0,                   # 毛利率（%）
                           'npr': 22.93,                 # 净利润率（%）
                           'holder_num': 354508.0}       # 股东人数
                           }
        """
        data = self.pro.bak_basic(ts_code=ts_code, trade_date=trade_date, fields='ts_code,pe,float_share,total_share,total_assets,liquid_assets,fixed_assets,reserved,reserved_pershare,eps,bvps,pb,undp,per_undp,rev_yoy,profit_yoy,gpr,npr,holder_num')
        data = self.dataframe_to_dict(data,'ts_code')
        return data
    
    def get_stock_moneyflow(self,ts_code='',trade_date='',start_date='',end_date='') -> dict:
        """
        获取股票的资金流动情况
            :param ts_code: 股票代码
            :param trade_date: 交易日期
            :param start_date: 开始日期
            :param end_date: 结束日期
            return {ts_code:{}}
            Examples
            --------
            >>> .get_stock_moneyflow('000001.SZ','20220830')
             {'000001.SZ': {'trade_date': '20220830',    # 交易日期
                            'buy_sm_vol': 174724,        # 小单买入量（手）
                            'buy_sm_amount': 21625.57,   # 小单买入金额（万元）
                            'sell_sm_vol': 184932,       # 小单卖出量（手）
                            'sell_sm_amount': 22948.11,  # 小单卖出金额（万元）
                            'buy_md_vol': 219068,        # 中单买入量（手）
                            'buy_md_amount': 27150.53,   # 中单买入金额（万元）
                            'sell_md_vol': 229456,       # 中单卖出量（手）
                            'sell_md_amount': 28466.74,  # 中单卖出金额（万元）
                            'buy_lg_vol': 215363,        # 大单买入量（手）
                            'buy_lg_amount': 26713.16,   # 大单买入金额（万元）
                            'sell_lg_vol': 215281,       # 大单卖出量（手）
                            'sell_lg_amount': 26702.66,  # 大单卖出金额（万元）
                            'buy_elg_vol': 190558,       # 特大单买入量（手）
                            'buy_elg_amount': 23655.51,  # 特大单买入金额（万元）
                            'sell_elg_vol': 170043,      # 特大单卖出量（手）
                            'sell_elg_amount': 21027.25, # 特大单卖出金额（万元）
                            'net_mf_vol': -109975,       # 净流入量（手）
                            'net_mf_amount': -13500.38}}"# 净流入额（万元）
        """
        data = self.pro.moneyflow(ts_code=ts_code,trade_date=trade_date,start_date=start_date,end_date=end_date)
        return self.dataframe_to_dict(data,'ts_code')
    
if __name__ == '__main__':
    api = TushareApi()
    api.get_single_stock_advanced_info()
    print(api.get_all_stock_info())
    
