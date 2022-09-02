from cgitb import reset
from re import S
import time
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
        self.default_days = self.config.getint('tushare','default_days')
        self.now_time_dict = self.get_time_dict()
        self.start_time_dict = self.get_time_dict(last_days=self.default_days)
        self.trade_date = self.get_all_trade_date
        self.all_ts_code = list(self.get_all_stock_basic_info().keys())

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

    # 获取时间字典
    def get_time_dict(self, last_days=0):
        """
        获取时间字典
            :param last_days:int, 前多少天，负数即后多少天
            :return: dict
            Examples
            --------
            >>> .get_time_dict()
            {'year': 2022, 'month': 7, 
            'day': 29, 'hour': 14, 
            'minute': 16, 'second': 26, 
            'week_day': '周五'}
        """
        time_tuple = time.localtime(time.time() - 3600 * 24 * last_days)
        week_day_dict = {0: '周一', 1: '周二', 2: '周三', 3: '周四', 4: '周五', 5: '周六', 6: '周日'}
        time_dict = {'year': time_tuple[0], 'month': time_tuple[1], 'day': time_tuple[2], 'hour': time_tuple[3],
                     'minute': time_tuple[4], 'second': time_tuple[5], 'week_day': week_day_dict[time_tuple[6]]}
        return time_dict

    # 获取所有股票的基本信息
    def get_all_stock_basic_info(self) -> list:
        """
        获取所有股票的基本信息
            :return: 返回一个列表，列表中每个元素为一个字典，key为ts_code，value为各个字段值
            Examples
            --------
            >>> .get_all_stock_basic_info()
            '000001.SZ': {'symbol': '000001',  # 股票代码
                          'name': '平安银行',   # 股票名称
                          'area': '深圳',       # 所在地域
                          'industry': '银行',   # 所属行业
                          'list_date': '19910403'}# 上市日期
        """
        data = self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
        return self.dataframe_to_dict(data,'ts_code')

    # 获取所有交易日期
    def get_all_trade_date(self,start_date=None):
        """
        获取所有交易日期
        """
        if start_date == None:
            self.start_date = str(self.start_time_dict['year'])+str(self.start_time_dict['month']).zfill(2)+str(self.start_time_dict['day']).zfill(2)
        data = self.pro.trade_cal(start_date=start_date, is_open='1')
        return list(self.dataframe_to_dict(data,'cal_date').keys())

    # 获取股票的日线行情
    def get_stock_daily(self, ts_code='', trade_date='', start_date='') -> dict:
        """
        获取股票的日线行情
            :param ts_code: str, 股票代码，如：'000001.SZ'
            :param trade_date: str, 日期，如：'20191231'
            :param start_date: str, 开始日期，如：'20191231'
            :return: 返回一个字典，key为ts_code，value为各个字段值
            Examples
            --------
            >>> .get_stock_daily(ts_code='000001.SZ', trade_date='20191231')
            '000001.SZ': {'ts_code': '000001.SZ',  # 股票代码
                            'trade_date': '20191231', # 交易日期

        """
        data = self.pro.bak_daily(ts_code=ts_code, trade_date=trade_date, start_date=start_date, 
        fields='ts_code,trade_date,pct_change,close,change,open,high,low,pre_close,vol_ratio,turn_over,swing,vol,amount,selling,buying,strength,activity,avg_turnover,attack')
        if not trade_date:
            data = self.dataframe_to_dict(data,'trade_date')
        else:
            data = self.dataframe_to_dict(data,'ts_code')
        return data
    # 获取股票的进阶信息
    def get_single_stock_advanced_info(self,ts_code='',trade_date='',start_date='') -> dict:
        """
        获取股票的进阶信息
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
        data = self.pro.bak_basic(ts_code=ts_code, trade_date=trade_date, start_date=start_date, fields='ts_code,trade_date,pe,float_share,total_share,total_assets,liquid_assets,fixed_assets,reserved,reserved_pershare,eps,bvps,pb,undp,per_undp,rev_yoy,profit_yoy,gpr,npr,holder_num')
        if not trade_date:
            data = self.dataframe_to_dict(data,'trade_date')
        else:
            data = self.dataframe_to_dict(data,'ts_code')
        return data
    
    # 获取股票的资金流动情况
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
        if not trade_date:
            data = self.dataframe_to_dict(data,'trade_date')
        else:
            data = self.dataframe_to_dict(data,'ts_code')
        return self.dataframe_to_dict(data,'ts_code')
    
if __name__ == '__main__':
    api = TushareApi()
    api.get_all_stock_basic_info()
    print(api.get_all_stock_info())
    
