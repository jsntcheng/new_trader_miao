from data_api.tushare_api import TushareApi
import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)


class Daily(object):
    def __init__(self):
        self.tushare = TushareApi()
        self.now_date = self.get_now_date()
        self.yes_date = self.get_yes_date()
        self.trade_dates = self.get_trade_date()
        self.all_ts_code = self.get_all_ts_code()

    def get_now_date(self):
        return self.tushare.get_date()

    def get_yes_date(self):
        return self.tushare.get_date(1)

    def get_trade_date(self):
        return self.tushare.get_all_trade_date(self.yes_date, self.now_date)

    def get_all_ts_code(self):
        return self.tushare.get_all_stock_ts_code()

    def get_single_daily(self, ts_code, trade_date):
        stock_daily = self.tushare.get_stock_daily(ts_code, trade_date)
        advanced_info = self.tushare.get_stock_advanced_info(
            ts_code, trade_date)
        moneyflow = self.tushare.get_stock_moneyflow(ts_code, trade_date)
        chip_winrate = self.tushare.get_chip_winrate(ts_code, trade_date)
        factor = self.tushare.get_factor(ts_code, trade_date)
        sum = {}
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
                      'weight_avg': '加权平均成本', 'winner_rate': '胜率', 'price': '成本价格', 'percent': '价格占比（%）'}
        sum.update(stock_daily[ts_code])
        sum.update(advanced_info[ts_code])
        sum.update(moneyflow[ts_code])
        sum.update(chip_winrate[ts_code])
        sum.update(factor[ts_code])
        sum = self.tushare.reset_dict_key(sum, reset_dict)
        return sum

    def run(self):
        pass


if __name__ == "__main__":
    daily = Daily()
    sample = daily.get_single_daily('000001.SZ', '20201201')
    print(sample)
    pass
