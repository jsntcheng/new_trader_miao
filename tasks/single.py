# 获取单个股票一段时间内的数据
from multiprocessing import Pool
from sqlalchemy import create_engine
from data_api.tushare_api import TushareApi
import sys
import os
import pandas as pd
from loguru import logger
import schedule
from time import sleep
from tasks.basic import StockBasic


location = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_file_path = os.path.join(location,f'logs/daily_task.log')
logger.add(log_file_path,rotation="daily", encoding="utf-8", enqueue=True, retention="10 days")

start = '20080103'
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
conn = create_engine(
'mysql+pymysql://root:543049601a@192.168.61.158:33063/tushare_dev')

reset_dict = {'chip_distribute':'筹码分布(价格，占比)','trade_date': '交易日期', 'buy_sm_vol': '小单买入量（手）',
              'buy_sm_amount': '小单买入金额（万元）', 'sell_sm_vol': '小单卖出量（手）',
              'sell_sm_amount': '小单卖出金额（万元）', 'buy_md_vol': '中单买入量（手）',
              'buy_md_amount': '中单买入金额（万元）', 'sell_md_vol': '中单卖出量（手）',
              'sell_md_amount': '中单卖出金额（万元）', 'buy_lg_vol': '大单买入量（手）',
              'buy_lg_amount': '大单买入金额（万元）', 'sell_lg_vol': '大单卖出量（手）',
              'sell_lg_amount': '大单卖出金额（万元）', 'buy_elg_vol': '特大单买入量（手）',
              'buy_elg_amount': '特大单买入金额（万元）', 'sell_elg_vol': '特大单卖出量（手）',
              'sell_elg_amount': '特大单卖出金额（万元）', 'net_mf_vol': '净流入量（手）',
              'net_mf_amount': '净流入额（万元）', "pct_change": '涨跌幅', "close": '收盘价',
              'change': '涨跌额', 'open': '开盘价', 'high': '最高价', 'low': '最低价', 'pre_close': '昨收价',
              'vol_ratio': '成交量比', 'turn_over': '换手率', 'swing': '振幅', 'vol': '成交量',
              'amount': '成交额', 'selling': '卖出量', 'buying': '买入量', 'strength': '强弱指数',
              'activity': '活跃度', 'avg_turnover': '笔换手', 'attack': '攻击波', 'pe': '市盈率（动）',
              'float_share': '流通股本（亿）', 'total_share': '总股本（亿）', 'total_assets': '总资产（亿）',
              'liquid_assets': '流动资产（亿）', 'fixed_assets': '固定资产（亿）', 'reserved': '公积金',
              'reserved_pershare': '每股公积金', 'eps': '每股收益', 'bvps': '每股净资产', 'pb': '市净率',
              'undp': '未分配利润', 'per_undp': '每股未分配利润', 'rev_yoy': '收入同比（%）',
                      'profit_yoy': '利润同比（%）', 'gpr': '毛利率（%）', 'npr': '净利润率（%）',
                      'holder_num': '股东人数', 'his_low': '历史最低', 'his_high': '历史最高', 'cost_5pct': '5分位成本',
                      'cost_15pct': '15分位成本', 'cost_50pct': '50分位成本', 'cost_85pct': '85分位成本', 'cost_95pct': '95分位成本',
                      'weight_avg': '加权平均成本', 'winner_rate': '胜率', 'price': '成本价格', 'percent': '价格占比（%）', 'chip_distribute': '筹码分布(价格，占比)'}

class SingleStock(StockBasic):
    def __init__(self,ts_code,back_days) -> None:
        StockBasic.__init__(self)
        self.ts_code = ts_code
        trade_date = self.tushare.get_all_trade_date(start_date=self.tushare.get_date(back_days))
        self.start_date = self.symbol_start_date(ts_code=ts_code,start_date=trade_date[-1])
        self.table_name = self.get_table_name(self.ts_code)
        logger.info(f'获取单只股票数据||{self.table_name}||起始日期：{self.start_date}')

    def get_stock_data(self):
        stock_daily = self.tushare.get_stock_daily(self.ts_code, start_date=self.start_date)
        advanced_info = self.tushare.get_stock_advanced_info(self.ts_code, start_date=self.start_date)
        moneyflow = self.tushare.get_stock_moneyflow(self.ts_code, start_date=self.start_date)
        chip_winrate = self.tushare.get_chip_winrate(self.ts_code, start_date=self.start_date)
        chip_distribute = self.tushare.get_chip_distribution(self.ts_code, start_date=self.start_date)
        sum = stock_daily
        for i in sum:
            sum[i]['trade_date'] = i
            sum[i].update(advanced_info[i])
            sum[i].update(moneyflow[i])
            sum[i].update(chip_winrate[i])
            sum[i]['chip_distribute'] = str(chip_distribute[i])
            sum[i] = self.tushare.reset_dict_key(sum[i], reset_dict)
            del sum[i]['未知']
        
        df = pd.DataFrame.from_dict(list(sum.values()))
        df.to_sql(self.table_name, conn, if_exists='append', index=False)

if __name__ == '__main__':
    # schedule.every().day.at("15:00").do(get_stock_data)
    # while True:
    #     schedule.run_pending()
    #     sleep(1)
    ts_code = input('请输入股票代码：\n')
    back_days = input('请输入回推天数：\n')
    SingleStock(ts_code,back_days).get_stock_data()