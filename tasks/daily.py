import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)



from data_api.tushare_api import TushareApi


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
        advanced_info = self.tushare.get_stock_advanced_info(ts_code, trade_date)
        moneyflow = self.tushare.get_stock_moneyflow(ts_code, trade_date)
        chip_winrate = self.tushare.get_chip_winrate(ts_code, trade_date)
        factor = self.tushare.get_factor(ts_code, trade_date)
        sum = {}
        sum.update(stock_daily[ts_code])
        sum.update(advanced_info[ts_code])
        sum.update(moneyflow[ts_code])
        sum.update(chip_winrate[ts_code])
        sum.update(factor[ts_code])
        return sum

    def run(self):
        pass

if __name__ == "__main__":
    daily = Daily()
    sample = daily.get_single_daily('000001.SZ', '20201201')
    print(sample)
    pass