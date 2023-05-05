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
'mysql+pymysql://root:543049601a@192.168.61.158:33063/tushare')

reset_dict = {'trade_date': '交易日期', 'buy_sm_vol': '小单买入量（手）',
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




class Daily(StockBasic):
    def __init__(self):
        StockBasic.__init__(self)
        
    def get_single_daily_normal(self, ts_code, trade_date):
        stock_daily = self.tushare.get_stock_daily(ts_code, trade_date)
        advanced_info = self.tushare.get_stock_advanced_info(
            ts_code, trade_date)
        moneyflow = self.tushare.get_stock_moneyflow(ts_code, trade_date)
        chip_winrate = self.tushare.get_chip_winrate(ts_code, trade_date)
        chip_distribute = self.tushare.get_chip_distribution(
            ts_code, trade_date)[self.now_date]
        # factor = self.tushare.get_factor(ts_code, trade_date)

        sum = {}
        sum.update(stock_daily[ts_code])
        sum.update(advanced_info[ts_code])
        sum.update(moneyflow[ts_code])
        sum.update(chip_winrate[ts_code])
        # sum.update(factor[ts_code])
        sum = self.tushare.reset_dict_key(sum, reset_dict)
        sum['筹码分布(价格，占比)'] = str(chip_distribute)
        del sum['未知']
        return sum


daily = Daily()

# 获取当天的数据（每日定时19点获取）
@logger.catch
def run_normal(code,date=None):
    if date:
        trade_time = date
    else:
        trade_time = daily.get_now_date()
    table_name = daily.get_table_name(code)
    df = pd.DataFrame.from_dict([daily.get_single_daily_normal(code, trade_time)])
    df.to_sql(table_name, conn, if_exists='append', index=False)
    logger.info('{}||时间：{}||更新完成'.format(table_name, trade_time))

def daily_task():
    if daily.check_trade_date():
        p = Pool(3)
        for code in daily.all_ts_code:
            p.apply_async(run_normal, args=(code,))
        p.close()
        p.join()

def handle_task(date):
    p = Pool(3)
    for code in daily.all_ts_code:
        p.apply_async(run_normal, args=(code, date))
    p.close()
    p.join()

def run_first(ts_code,table_name):

    print('开始初始化{}的表'.format(ts_code))
    conn = create_engine(
'mysql+pymysql://root:543049601a@192.168.61.158:33063/tushare')
    mock_data = {'交易日期': '19900101', '涨跌幅': -1.3, '收盘价': 12.12, '涨跌额': -0.16, 
                    '开盘价': 12.25, '最高价': 12.25, '最低价': 11.99, '昨收价': 12.28, '成交量比': 0.9, 
                    '换手率': 0.51, '振幅': 2.12, '成交量': 991260.0, '成交额': 119755.57, '卖出量': 494426.0, 
                    '买入量': 496834.0, '强弱指数': -1.63, '活跃度': 4544.0, '笔换手': 0.0, '攻击波': 1.08, 
                    '市盈率（动）': 4.03, '流通股本（亿）': 194.06, '总股本（亿）': 194.06, '总资产（亿）': 54558.97, 
                    '流动资产（亿）': 0.0, '固定资产（亿）': 106.81, '公积金': 807.56, '每股公积金': 4.16, '每股收益': 0.65, 
                    '每股净资产': 19.42, '市净率': 0.62, '未分配利润': 1988.26, '每股未分配利润': 10.25, '收入同比（%）': -2.4, 
                    '利润同比（%）': 13.63, '毛利率（%）': 40.73, '净利润率（%）': 32.38, '股东人数': 506867, '小单买入量（手）': 286971, 
                    '小单买入金额（万元）': 34654.51, '小单卖出量（手）': 196225, '小单卖出金额（万元）': 23717.76, 
                    '中单买入量（手）': 320683, '中单买入金额（万元）': 38725.2, '中单卖出量（手）': 303389, '中单卖出金额（万元）': 36670.68, 
                    '大单买入量（手）': 257749, '大单买入金额（万元）': 31160.33, '大单卖出量（手）': 305641, '大单卖出金额（万元）': 36926.51, 
                    '特大单买入量（手）': 125858, '特大单买入金额（万元）': 15215.53, '特大单卖出量（手）': 186005, 
                    '特大单卖出金额（万元）': 22440.62, '净流入量（手）': -93510, '净流入额（万元）': -11203.89, '历史最低': 0.31, 
                    '历史最高': 24.79, '5分位成本': 8.23, '15分位成本': 11.83, '50分位成本': 13.03, '85分位成本': 17.59, '95分位成本': 21.91, 
                    '加权平均成本': 13.92, '胜率': 20.14, '成本价格': 24.79, '价格占比（%）': 0.05, '筹码分布(价格，占比)': '[[0.31, 0.04],[0.55,0.04]]'}
    a = pd.DataFrame.from_dict([mock_data])
    a.to_sql(table_name, conn, if_exists='replace', index=False)


if __name__ == "__main__":
    schedule.every().day.at("19:00").do(daily_task)
    task_no = int(input("请输入任务编号：1：每日任务，2：手动任务"))
    if task_no == 1:
        while True:
            schedule.run_pending()
            sleep(1)
    elif task_no == 2:
        date = input("请输入日期：")
        handle_task(date)
