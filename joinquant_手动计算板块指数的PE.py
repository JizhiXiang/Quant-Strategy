# https://www.joinquant.com/view/community/detail/672f025e00eb79ad69458f8ae0dc9f07
# 注意，这里的代码需要在聚宽环境下运行


### 简单版本
from jqdata import *

def get_index_pe(index_code, date):
    """
    根据指数成分股计算整体市盈率 PE
    :param index_code: 指数代码，例如 '000300.XSHG' (沪深300)
    :param date: 查询日期，例如 '2025-08-15'
    :return: 指数整体市盈率 PE
    """
    # 1. 获取成分股列表
    stocks = get_index_stocks(index_code, date=date)
    if not stocks:
        print(f"{index_code} 在 {date} 无成分股数据")
        return None
    
    # 2. 获取成分股市值和净利润
    q = query(
        valuation.code,
        valuation.market_cap,      # 总市值(亿元)
        income.net_profit       # 净利润(元)
    ).filter(valuation.code.in_(stocks))
    
    df = get_fundamentals(q, date=date)
    if df.empty:
        print(f"在 {date} 没有查到成分股数据")
        return None
    
    # 3. 计算总市值和总净利润
    total_mv = df['market_cap'].sum() * 1e8    # 亿 → 元
    total_profit = df['net_profit'].sum()
    
    if total_profit <= 0:
        print(f"{index_code} 在 {date} 总净利润为负，无法计算PE")
        return None
    
    pe = total_mv / total_profit
    print(f"{index_code} 在 {date} 的整体市盈率 PE 为: {pe:.2f}")
    return pe


# 示例：计算沪深300在 2025-06-30 的PE
pe = get_index_pe('000300.XSHG', '2025-06-30')





#### 加权计算版本
from jqdata import *
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
def get_index_pe(index_code, date):
    """
    根据指数成分股权重计算整体市盈率 PE
    """
    # 成分股权重（%）
    weights = get_index_weights(index_id=index_code, date=date)
    if weights.empty:
        return None
    
    stocks = list(weights.index)
    
    # 获取市值和净利润
    q = query(
        valuation.code,
        valuation.market_cap,   # 总市值(亿)
        income.net_profit       # 净利润(元)
    ).filter(valuation.code.in_(stocks))
    
    df = get_fundamentals(q, date=date)
    if df.empty:
        return None
    
    # 合并权重
    df = df.merge(weights[['weight']], left_on='code', right_index=True, how='inner')
    
    # 市值、利润加权
    df['market_cap'] = df['market_cap'] * 1e8  # 转元
    df['weight'] = df['weight'] / 100          # 百分比转小数
    
    total_mv = (df['market_cap'] * df['weight']).sum()
    total_profit = (df['net_profit'] * df['weight']).sum()
    
    if total_profit <= 0:
        return None
    
    return total_mv / total_profit


def get_monthly_pe(index_code, start_date, end_date):
    """
    每月1号计算指数PE
    """
    dates = pd.date_range(start_date, end_date, freq="MS")  # 每月首日
    pe_list = []
    for d in dates:
        d_str = d.strftime("%Y-%m-%d")
        try:
            pe = get_index_pe(index_code, d_str)
            if pe is not None:
                pe_list.append((d_str, pe))
        except:
            continue
    return pd.DataFrame(pe_list, columns=['date','pe']).set_index('date')


def plot_index_pe(index_code, pe_df):
    """
    绘制指数价格 vs PE
    """
    # 获取指数价格
    price_df = get_price(index_code, start_date=pe_df.index[0], 
                         end_date=pe_df.index[-1], frequency='1d', fields=['close'])
    price_df = price_df.resample('MS').first()  # 每月首日价格
    
    # 对齐
    df = pe_df.join(price_df, how='inner')
    
    # 画图
    fig, ax1 = plt.subplots(figsize=(12,6))
    
    ax1.set_ylabel('Index Price', color='b')
    ax1.plot(df.index, df['close'], 'b-', label='Index Price')
    ax1.tick_params(axis='y', labelcolor='b')
    
    ax2 = ax1.twinx()
    ax2.set_ylabel('PE', color='r')
    ax2.plot(df.index, df['pe'], 'r-', label='PE')
    ax2.tick_params(axis='y', labelcolor='r')
    
    plt.title(f"{index_code} Price vs PE")
    plt.show()


# ================== 示例 ==================
index_code = "000300.XSHG"  # 沪深300
start_date = "2005-04-08"   # 沪深300成立日期
end_date = dt.date.today().strftime("%Y-%m-%d")

pe_df = get_monthly_pe(index_code, start_date, end_date)
plot_index_pe(index_code, pe_df)