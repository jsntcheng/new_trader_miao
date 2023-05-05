# 通用任务父类
from multiprocessing import Pool
from sqlalchemy import create_engine
from data_api.tushare_api import TushareApi
import sys
import os
import pandas as pd
from loguru import logger
import schedule
from time import sleep

location = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_file_path = os.path.join(location,f'logs/daily_task.log')
logger.add(log_file_path,rotation="daily", encoding="utf-8", enqueue=True, retention="10 days")

start = '20080103'
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
conn = create_engine(
'mysql+pymysql://root:543049601a@192.168.61.158:33063/tushare')

class StockBasic(object):
    def __init__(self):
        self.tushare = TushareApi()
        self.now_date = self.get_now_date()
        self.yes_date = self.get_yes_date()
        self.trade_dates = self.get_trade_date()
        self.all_ts_code = self.get_all_ts_code()

    def get_now_date(self):
        return self.tushare.get_date()

    def check_trade_date(self):
        if self.now_date in self.trade_dates:
            return True
        else:
            return False

    def get_yes_date(self):
        return self.tushare.get_date(1)

    def get_trade_date(self):
        return self.tushare.trade_date

    def get_all_ts_code(self):
        return self.tushare.all_ts_code

    def get_table_name(self, ts_code):
        return self.tushare.all_info[ts_code]['股票代码']+self.tushare.all_info[ts_code]['股票名称']

    def symbol_start_date(self, ts_code, start_date):
        return str(max(int(self.tushare.all_info[ts_code]['上市日期']), int(start_date)))
