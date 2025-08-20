'''
先获取概念板块,对应的股票, 然后:
最近5年roe均大于当年的平均水平, 最近一年roe排名前30%, 按照板块+roe降序排序
输出: 股票代码,股票名,板块名, 股价, 最近5年的roe, 板块平均roe, 市盈率

https://www.joinquant.com/view/community/detail/d69f30e5adbf3d97a6c901a535e91574
'''

# ====== 第1部分：读取数据与筛板块 ======
import json, pandas as pd
from jqdata import *
from datetime import datetime
# qmt_概念板块.json  在QQ群里
with open('qmt_概念板块.json', 'r', encoding='utf-8') as f:
    sectors = json.load(f)

keyword = "人工智能"  #人形机器人
result = {k: v for k, v in sectors.items() if keyword in k}

print("【找到的板块】:", list(result.keys()))
print("【去重后的股票总数】:", len({c for v in result.values() for c in v}))

def to_jq_code(c):
    return c.replace('.SH','.XSHG').replace('.SZ','.XSHE')

stocks = sorted({
    to_jq_code(c) for v in result.values() for c in v
    if c.startswith(('60','00'))
})

# ====== 第2部分：获取最近5年财务数据并过滤 ======
y0 = datetime.today().year
years = list(range(y0-5, y0))  # y0-5 到 y0-1

q = query(valuation.code, valuation.pe_ratio, indicator.roe).filter(valuation.code.in_(stocks))
df = pd.concat([get_fundamentals(q, statDate=y).assign(year=y) for y in years], ignore_index=True)

# 当年样本平均ROE，并标记是否大于平均
df['roe_avg_year'] = df.groupby('year')['roe'].transform('mean')
df['gt_avg'] = df['roe'] > df['roe_avg_year']

# 条件：最近5年ROE均大于当年平均
flag_5y = df.groupby('code')['gt_avg'].all()
df = df[df.code.isin(flag_5y[flag_5y].index)].copy()

# 最近一年（用于排名与板块均值）
last = df[df.year == y0-1].copy()

# ====== 第3部分：多对多映射并“拆行” ======
rel_rows = []
for sec_name, codes in result.items():
    for c in codes:
        if c.startswith(('60','00')):
            rel_rows.append((to_jq_code(c), sec_name))
rel = pd.DataFrame(rel_rows, columns=['code', 'sector']).drop_duplicates()

# 将 last 拆成每行一个板块
last_exploded = last.merge(rel, on='code', how='inner')

# 板块平均ROE/PE（最近一年），兼容旧版 pandas 的写法
sector_summary = (last_exploded.groupby('sector')
                  .agg({'pe_ratio':'mean','roe':'mean','code':pd.Series.nunique})
                  .reset_index()
                  .rename(columns={'pe_ratio':'avg_pe','roe':'avg_roe','code':'n'}))

# 映射到明细
sector_avg_roe_map = dict(zip(sector_summary['sector'], sector_summary['avg_roe']))
sector_avg_pe_map  = dict(zip(sector_summary['sector'], sector_summary['avg_pe']))
last_exploded['sector_avg_roe'] = last_exploded['sector'].map(sector_avg_roe_map)
last_exploded['sector_avg_pe']  = last_exploded['sector'].map(sector_avg_pe_map)

# ====== 第4部分：取最近一年ROE前30%（按股票，不按板块行） ======
cut = last['roe'].quantile(0.7)
top_codes = set(last[last['roe'] >= cut]['code'])
res = last_exploded[last_exploded['code'].isin(top_codes)].copy()

# ====== 第5部分：补充“最近5年ROE列表”、名称与现价 ======
roe_hist = (df.pivot_table(index='code', columns='year', values='roe')
              .reindex(columns=years))
def _to_list(s):
    vals = []
    for x in s.values:
        if pd.isna(x):
            vals.append(None)
        else:
            vals.append(round(float(x), 4))
    return vals
roe_hist_list = roe_hist.apply(_to_list, axis=1).to_dict()
res['roe_5y'] = res['code'].map(roe_hist_list)

names = get_all_securities(['stock']).display_name.to_dict()
res['name'] = res['code'].map(names)

res['price'] = res['code'].apply(
    lambda x: float(get_price(x, count=1, end_date=datetime.today()).close[0])
)

# ====== 第6部分：分部分输出 ======
# 6.1 板块层面汇总（平均估值、平均ROE、样本数）
sector_summary['avg_pe'] = sector_summary['avg_pe'].round(2)
sector_summary['avg_roe'] = sector_summary['avg_roe'].round(2)
sector_summary = sector_summary.sort_values(['avg_pe','sector']).reset_index(drop=True)

print("\n【板块汇总：平均估值(PE) / 平均ROE / 样本股票数】")
print(sector_summary)

# 6.2 明细结果
res = res.sort_values(['sector','roe'], ascending=[True, False]).reset_index(drop=True)

# 数值字段统一保留两位小数
res['price'] = res['price'].round(2)
res['sector_avg_roe'] = res['sector_avg_roe'].round(2)
res['pe_ratio'] = res['pe_ratio'].round(2)
# roe_5y 是列表，需要单独处理
res['roe_5y'] = res['roe_5y'].apply(lambda lst: [None if v is None else round(v,2) for v in lst])

final_cols = ['code','name','sector','price','roe_5y','sector_avg_roe','pe_ratio']
print("\n【最终结果（ROE前30%样本，按板块+最近一年ROE降序）】")

res[final_cols]
