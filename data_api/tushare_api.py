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
        self.config = configparser.ConfigParser()
        self.config.read(parent_dir + '/config.ini', encoding='utf-8')
        self.pro = ts.pro_api(self.config.get('tushare', 'token'))
        self.default_days = self.config.getint('tushare', 'default_days')
        self.start_date = self.get_date(self.default_days)
        self.trade_date = self.get_all_trade_date()
        self.all_ts_code = self.get_all_stock_ts_code()
        self.get_count = self.init_get_count()
        self.all_info = self.get_all_stock_basic_info()
    @staticmethod
    def init_get_count():
        return {'all_stock_basic_info': 0,
                'all_trade_date': 0,
                'chip_distribution': 0,
                'stock_daily': 0,
                'stock_advanced_info': 0,
                'stock_moneyflow': 0,
                }

    @staticmethod
    def dataframe_to_list(data_frame):
        temp = np.array(data_frame)
        return temp.tolist()

    @staticmethod
    def dataframe_to_dict(data_frame, key):
        return data_frame.set_index(key).T.to_dict()

    @staticmethod
    def reset_dict_key(old_dict, reset_dict):
        """
        重置字典的key
        """
        new_dict = {'未知':{}}
        for key in old_dict.keys():
            if key not in reset_dict:
                new_dict['未知'][key] = old_dict[key]
                continue
            new_dict[reset_dict[key]] = old_dict[key]
        return new_dict

    def get_date(self, last_days=0):
        time_dict = self.get_time_dict(last_days=last_days)
        date = str(time_dict['year']) + str(time_dict['month']).zfill(2) + str(time_dict['day']).zfill(2)
        return date

    # 获取时间字典
    def get_time_dict(self, last_days=0):
        """
        获取时间字典
            :param last_days:int, 前多少天，负数即后多少天
            :return: dict
            Examples
            --------
            >>> self.get_time_dict()
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
    def get_all_stock_basic_info(self) -> dict:
        """
        获取所有股票的基本信息
            :return: 返回一个列表，列表中每个元素为一个字典，key为ts_code，value为各个字段值
            Examples
            --------
            >>> self.get_all_stock_basic_info()
            '000001.SZ': {'symbol': '000001',  # 股票代码
                          'name': '平安银行',   # 股票名称
                          'area': '深圳',       # 所在地域
                          'industry': '银行',   # 所属行业
                          'list_date': '19910403'}# 上市日期
        """
        data = self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
        data = self.dataframe_to_dict(data, 'ts_code')
        for symbol in data:
            data[symbol] = self.reset_dict_key(data[symbol],
                                               {'symbol': '股票代码', 'name': '股票名称', 'area': '所在地域',
                                                'industry': '所属行业', 'list_date': '上市日期'})
        return data

    # 获取所有股票的TS代码
    def get_all_stock_ts_code(self) -> list:
        return list(self.get_all_stock_basic_info().keys())

    # 获取所有交易日期
    def get_all_trade_date(self, start_date=None, end_date='') -> list:
        """
        获取所有交易日期
        """
        if start_date == None:
            start_date = self.start_date
        data = self.pro.trade_cal(start_date=start_date, end_date=end_date, is_open='1')
        return list(self.dataframe_to_dict(data, 'cal_date').keys())

    # 获取日线行情
    def get_stock_daily(self, ts_code='', trade_date='', start_date='', end_date='') -> dict:
        """
        获取股票的日线行情
            :param ts_code: str, 股票代码，如：'000001.SZ'
            :param trade_date: str, 日期，如：'20191231'
            :param start_date: str, 开始日期，如：'20191231'
            :return: 返回一个字典，key为ts_code，value为各个字段值
            Examples
            --------

            {'000001.SZ': {'trade_date': '20191231',  # 交易日期
                            'pct_change': -0.72,      # 涨跌幅
                            'close': 16.45,           # 收盘价
                            'change': -0.12,          # 涨跌额
                            'open': 16.57,            # 开盘价
                            'high': 16.63,            # 最高价
                            'low': 16.31,             # 最低价
                            'pre_close': 16.57,       # 昨收价
                            'vol_ratio': 1.08,        # 成交量比
                            'turn_over': 0.36,        # 换手率
                            'swing': 1.93,            # 振幅
                            'vol': 704442.0,          # 成交量
                            'amount': 1154704384.0,   # 成交额
                            'selling': 323640.0,      # 卖出量
                            'buying': 380802.0,       # 买入量
                            'strength': -1.35,        # 强弱指数
                            'activity': 4539.0,       # 活跃度
                            'avg_turnover': 0.0,      # 笔换手
                            'attack': 0.86}}          # 攻击波

        """
        data = self.pro.bak_daily(ts_code=ts_code, trade_date=trade_date, start_date=start_date, end_date=end_date,
                                   fields='ts_code,trade_date,pct_change,close,change,open,high,low,pre_close,vol_ratio,turn_over,swing,vol,amount,selling,buying,strength,activity,avg_turnover,attack')
        if not trade_date:
            data = self.dataframe_to_dict(data, 'trade_date')
        else:
            data = self.dataframe_to_dict(data, 'ts_code')
        return data

    # 获取进阶信息（单次最大5000行数据，可以根据日期参数循环获取，正式权限需要5000积分）
    def get_stock_advanced_info(self, ts_code='', trade_date='', start_date='', end_date='') -> dict:
        """
        获取股票的进阶信息
            :param ts_code: 股票代码
            :param trade_date: 交易日期
            :return: 返回一个字典，key为ts_code，value为各个字段值
            Examples
            --------
            >>> self.get_stock_advanced_info(ts_code='000001.SZ',trade_date='20190806')
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
        data = self.pro.bak_basic(ts_code=ts_code, trade_date=trade_date, start_date=start_date, end_date=end_date,
                                   fields='ts_code,trade_date,pe,float_share,total_share,total_assets,liquid_assets,fixed_assets,reserved,reserved_pershare,eps,bvps,pb,undp,per_undp,rev_yoy,profit_yoy,gpr,npr,holder_num')
        if not trade_date:
            data = self.dataframe_to_dict(data, 'trade_date')
        else:
            data = self.dataframe_to_dict(data, 'ts_code')
        return data

    # 获取资金流动情况（单次最大提取5000行记录，总量不限制）
    def get_stock_moneyflow(self, ts_code='', trade_date='', start_date='', end_date='') -> dict:
        """
        获取股票的资金流动情况
            :param ts_code: 股票代码
            :param trade_date: 交易日期
            :param start_date: 开始日期
            :param end_date: 结束日期
            return {ts_code:{}}
            Examples
            --------
            >>> self.get_stock_moneyflow('000001.SZ','20220830')
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
        data = self.pro.moneyflow(ts_code=ts_code, trade_date=trade_date, start_date=start_date, end_date=end_date)
        self.get_count['stock_moneyflow'] += 1
        if not trade_date:
            data = self.dataframe_to_dict(data, 'trade_date')
        else:
            data = self.dataframe_to_dict(data, 'ts_code')
        return data

    # 获取筹码分布（单次最大2000条，5000积分每天20000次）
    def get_chip_distribution(self, ts_code='', trade_date='', start_date='', end_date='') -> list:
        if self.get_count['chip_distribution'] >= 20000:
            logger.info('获取筹码分布超过限制，请稍后再试')
        data = self.pro.cyq_chips(ts_code=ts_code, trade_date=trade_date, start_date=start_date, end_date=end_date)
        self.get_count['chip_distribution'] += 1
        data = self.dataframe_to_list(data)
        for index,item in enumerate(data):
            data[index] = item[2:]
        return data

    # 获取筹码及胜率(单次最大5000条，5000积分每天20000次)
    def get_chip_winrate(self, ts_code='', trade_date='', start_date='', end_date='') -> dict:
        data = self.pro.cyq_perf(ts_code=ts_code, trade_date=trade_date, start_date=start_date, end_date=end_date)
        if not trade_date:
            data = self.dataframe_to_dict(data, 'trade_date')
        else:
            data = self.dataframe_to_dict(data, 'ts_code')
        return data

    # 获取技术面因子
    def get_factor(self, ts_code='', trade_date='', start_date='', end_date='') -> dict:
        data = self.pro.cyq_chips(ts_code=ts_code, trade_date=trade_date, start_date=start_date)
        if not trade_date:
            data = self.dataframe_to_dict(data, 'trade_date')
        else:
            data = self.dataframe_to_dict(data, 'ts_code')
        return data


if __name__ == '__main__':
    api = TushareApi()
    api.get_all_stock_basic_info()
    print()