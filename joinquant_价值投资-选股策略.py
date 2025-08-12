from jqdata import *
import pandas as pd
from datetime import datetime

# 让 Pandas 在 Jupyter 中完整显示，不省略
pd.set_option('display.max_rows', None)      # 显示所有行
pd.set_option('display.max_columns', None)   # 显示所有列
pd.set_option('display.width', None)         # 不限制每行宽度
pd.set_option('display.max_colwidth', 1000)  # 列内容不省略


# 股票池：60（沪市）或00（深市主板）开头
all_stocks = list(get_all_securities(['stock']).index)
symbols = [code for code in all_stocks if code.startswith('60') or code.startswith('00')]

# 获取近三年财务数据（按年度 statDate）
current_year = datetime.today().year
q = query(
    valuation.code,
    income.net_profit,
    indicator.roe
).filter(
    valuation.code.in_(symbols)
)

fundamentals_list = []
for y in range(current_year - 3, current_year):
    df = get_fundamentals(q, statDate=y)
    df['year'] = y
    fundamentals_list.append(df)

fundamentals_all = pd.concat(fundamentals_list)

# 近三年净利润均为正
pos_profit = fundamentals_all.groupby('code')['net_profit'].apply(lambda x: (x > 0).all())
pos_profit_codes = pos_profit[pos_profit].index.tolist()

# 取最近一年的 ROE 数据
latest_fund = fundamentals_all[fundamentals_all['year'] == current_year - 1]
latest_fund = latest_fund[latest_fund['code'].isin(pos_profit_codes)]

# 获取股票所属申万一级行业
industry_map = {}
for code in latest_fund['code']:
    try:
        info = get_industry(code)
        industry_map[code] = info[code]['sw_l1']['industry_name']
    except:
        industry_map[code] = None
industry_df = pd.DataFrame(list(industry_map.items()), columns=['code', 'industry_name'])

# 合并行业信息
merged = latest_fund.merge(industry_df, on='code', how='left')

# 按行业计算平均 ROE
industry_avg = merged.groupby('industry_name')['roe'].mean().reset_index()
industry_avg.columns = ['industry_name', 'roe_ind_avg']

merged = merged.merge(industry_avg, on='industry_name', how='left')

# 筛选 ROE 高于板块平均
res = merged[merged['roe'] > merged['roe_ind_avg']].copy()

# 加股票中文名
name_map = get_all_securities(['stock']).display_name.to_dict()
res['name'] = res['code'].map(name_map)

# 调整列顺序
res = res[['code', 'name', 'net_profit', 'roe', 'roe_ind_avg', 'industry_name']]

# 排序
res = res.sort_values(by='roe', ascending=False).reset_index(drop=True)

# 在 Jupyter 中直接显示完整表格
res
