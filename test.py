# 从注释转为字典
def get_dict_from_zhushi(str1):
    str1 = str1.replace('\n', '')
    str1 = str1.replace(' ', '')
    l1 = str1.split("'")[1:]
    for index, item in enumerate(l1):
        if index % 2 != 0:
            l1[index] = item.split(',#')[-1]
    res = {}
    for index, item in enumerate(l1):
        if index % 2 == 0:
            res[item] = l1[index + 1]
    return res

if __name__ == "__main__":
    str1 = """'symbol': '000001',  # 股票代码
                          'name': '平安银行',   # 股票名称
                          'area': '深圳',       # 所在地域
                          'industry': '银行',   # 所属行业
                          'list_date': '19910403'}# 上市日期"""
    res = get_dict_from_zhushi(str1)
    print("end")