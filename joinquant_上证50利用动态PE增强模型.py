# 注意，这里的代码需要在聚宽环境下运行
# https://www.joinquant.com/view/community/detail/77f4163b263ce4ada2e2bd0a42da12fc


from jqdata import *
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt

############################################
# 1) 按成分股权重计算当期指数PE
############################################
def get_index_pe(index_code, date):
    """
    根据指数成分股权重计算整体市盈率 PE = (权重加权总市值) / (权重加权净利润)
    :param index_code: 指数代码，例如 '000016.XSHG' (上证50)
    :param date:      日期字符串 'YYYY-MM-DD'（将取该日可用的最新基本面）
    :return:          PE (float) 或 None
    """
    # 成分股权重（%）
    weights = get_index_weights(index_id=index_code, date=date)
    if weights is None or len(weights)==0:
        return None
    weights = weights.copy()
    weights.index.name = 'code'
    weights = weights[['weight']]

    stocks = list(weights.index)

    # 获取市值与净利润（注意单位）
    q = query(
        valuation.code,
        valuation.market_cap,   # 总市值(亿)
        income.net_profit       # 净利润(元)
    ).filter(valuation.code.in_(stocks))

    df = get_fundamentals(q, date=date)
    if df is None or len(df)==0:
        return None

    # 合并权重
    df = df.merge(weights, on='code', how='inner')

    # 单位换算 + 权重转小数
    df['market_cap'] = df['market_cap'] * 1e8   # 亿元 -> 元
    df['weight']     = df['weight'] / 100.0

    # 按权重加总
    total_mv     = (df['market_cap'] * df['weight']).sum()
    total_profit = (df['net_profit'] * df['weight']).sum()

    if pd.isna(total_profit) or total_profit <= 0:
        return None

    return float(total_mv / total_profit)


def get_monthly_pe(index_code, start_date, end_date):
    """
    每月1号（往前推1天，避免“未来函数”）计算指数PE
    返回：按日期索引的 DataFrame: ['pe']
    """
    dates = pd.date_range(start_date, end_date, freq="MS")  # 每月首日
    rows = []
    for d in dates:
        d_str = (d - dt.timedelta(days=1)).strftime("%Y-%m-%d")  # 前一天
        try:
            pe = get_index_pe(index_code, d_str)
            if pe is not None and np.isfinite(pe):
                rows.append((d_str, pe))
        except Exception as e:
            # 可按需打印日志
            # print("PE计算失败:", d_str, e)
            continue
    if not rows:
        return pd.DataFrame(columns=['pe'])
    return pd.DataFrame(rows, columns=['date','pe']).set_index('date').sort_index()


############################################
# 2) 工具函数：获取指数日线收盘价
############################################
def get_index_close_series(index_code, start_date, end_date):
    """
    返回指数的日频收盘价 Series（索引为交易日）
    """
    px = get_price(index_code, start_date=start_date, end_date=end_date,
                   frequency='daily', fields=['close'], panel=False, skip_paused=True, fq='pre')
    px = px[['close']].rename(columns={'close':'close'}).dropna()
    return px['close']


############################################
# 3) 生成策略信号（24个月滚动分位：15/85）
############################################
def build_signals_from_pe(pe_df, lookback_months=24, low_pct=15, high_pct=85):
    """
    输入：月频 PE（index: 月份对应的观测日期（取每月1号前1日））
    逻辑：
      - 计算滚动窗口（近24个月）的15/85分位
      - 若当月PE <= p15: 设定目标持仓=1（满仓）
      - 若当月PE >= p85: 设定目标持仓=0（空仓）
      - 否则：保持上期目标持仓不变
    输出：月频 DataFrame ['pe','p15','p85','pos']
    """
    df = pe_df.copy()
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    df['p15'] = df['pe'].rolling(lookback_months, min_periods=max(12, lookback_months//3))\
                        .apply(lambda x: np.nanpercentile(x, low_pct), raw=True)
    df['p85'] = df['pe'].rolling(lookback_months, min_periods=max(12, lookback_months//3))\
                        .apply(lambda x: np.nanpercentile(x, high_pct), raw=True)

    # 生成目标持仓（0或1）
    pos = []
    last_pos = 0
    for dt_i, row in df.iterrows():
        pe   = row['pe']
        p15  = row['p15']
        p85  = row['p85']
        new_pos = last_pos
        if np.isfinite(pe) and np.isfinite(p15) and np.isfinite(p85):
            if pe <= p15:
                new_pos = 1
            elif pe >= p85:
                new_pos = 0
        pos.append(new_pos)
        last_pos = new_pos
    df['pos'] = pos
    return df[['pe','p15','p85','pos']]


############################################
# 4) 将月频信号映射到日频，进行回测
############################################
def backtest_long_flat(index_code, start_date, end_date,
                       pe_month_df, cost_per_trade=0.0005):
    """
    :param index_code: 指数代码
    :param start_date, end_date: 回测区间
    :param pe_month_df: 月频包含 ['pos'] 的 DataFrame（信号）
    :param cost_per_trade: 单边交易成本（默认0.0005=5bp），换仓日收取一次
    :return: 回测结果 DataFrame（含策略和基准累计净值）、绩效字典
    """
    # 指数日线
    close = get_index_close_series(index_code, start_date, end_date)
    ret = close.pct_change().fillna(0.0)
    ret.name = 'idx_ret'

    # 将月频信号对齐到日频，并“次一交易日生效”
    daily_pos = pe_month_df['pos'].copy()
    daily_pos.index = pd.to_datetime(daily_pos.index)
    # 用日频交易日日历重采样并前向填充
    pos_daily = daily_pos.reindex(ret.index, method='ffill').fillna(0)
    # 为避免未来函数：当日信号次一交易日生效
    pos_eff = pos_daily.shift(1).fillna(0)

    # 策略日收益
    strat_ret = pos_eff * ret

    # 交易成本：当“目标生效持仓”发生变化的当天扣一次单边成本
    # 注意：这里的成本是对净值直接扣减，不是对收益率做乘法
    trade_flag = (pos_eff != pos_eff.shift(1)).astype(int).fillna(0)
    # 忽略首日的“建仓”成本也可按需选择；这里默认计入成本
    strat_ret = strat_ret - trade_flag * cost_per_trade

    # 累计净值
    bench_nav = (1 + ret).cumprod()
    strat_nav = (1 + strat_ret).cumprod()
    out = pd.DataFrame({
        'bench_nav': bench_nav,
        'strat_nav': strat_nav,
        'position': pos_eff
    })

    # 绩效指标
    def max_drawdown(nav):
        cummax = nav.cummax()
        dd = nav / cummax - 1
        return dd.min()

    ann_factor = 252
    strat_ann_ret   = (strat_nav.iloc[-1])**(ann_factor/len(out)) - 1
    bench_ann_ret   = (bench_nav.iloc[-1])**(ann_factor/len(out)) - 1
    strat_ann_vol   = strat_ret.std() * np.sqrt(ann_factor)
    bench_ann_vol   = ret.std() * np.sqrt(ann_factor)
    strat_sharpe    = strat_ann_ret / strat_ann_vol if strat_ann_vol>0 else np.nan
    bench_sharpe    = bench_ann_ret / bench_ann_vol if bench_ann_vol>0 else np.nan
    strat_mdd       = max_drawdown(strat_nav)
    bench_mdd       = max_drawdown(bench_nav)

    stats = {
        '策略年化收益': strat_ann_ret,
        '基准年化收益': bench_ann_ret,
        '策略年化波动': strat_ann_vol,
        '基准年化波动': bench_ann_vol,
        '策略夏普比': strat_sharpe,
        '基准夏普比': bench_sharpe,
        '策略最大回撤': strat_mdd,
        '基准最大回撤': bench_mdd,
        '交易次数(含首日建仓)': int(trade_flag.sum())
    }
    return out, stats


############################################
# 5) 统一跑一遍 + 画图
############################################
def run_pipeline(index_code="000016.XSHG",
                 start_date="2011-01-01",
                 end_date=None,
                 lookback_months=36, low_pct=15, high_pct=85,
                 cost_per_trade=0.0005,
                 show_pe_panel=False):
    if end_date is None:
        end_date = dt.date.today().strftime("%Y-%m-%d")

    # 计算月频PE
    pe_df = get_monthly_pe(index_code, start_date, end_date)
    if pe_df is None or pe_df.empty:
        raise ValueError("未能计算到任何PE数据，请检查时间区间或基础数据可用性。")

    # 生成月频信号
    sig_df = build_signals_from_pe(pe_df, lookback_months, low_pct, high_pct)

    # 回测
    result_df, stats = backtest_long_flat(index_code, start_date, end_date, sig_df, cost_per_trade)

    # 打印绩效
    print("========== 绩效指标 ==========")
    for k, v in stats.items():
        if '回撤' in k:
            print(f"{k}: {v:.2%}")
        elif '次数' in k:
            print(f"{k}: {v}")
        else:
            print(f"{k}: {v:.2%}")

    # 画图：策略 vs 上证50（基准）
    plt.figure(figsize=(10, 5))
    plt.plot(result_df.index, result_df['bench_nav'], label='上证50-买入持有')
    plt.plot(result_df.index, result_df['strat_nav'], label='策略净值（PE 15/85%）')
    plt.title(f"{index_code} 策略 vs 基准 累计净值")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # 可选：展示PE与分位及持仓（辅助面板）
    if show_pe_panel:
        # 将月频对齐到日频以便更平滑显示（仅用于可视化）
        pe_daily = sig_df[['pe','p15','p85','pos']].reindex(result_df.index, method='ffill')
        fig, ax1 = plt.subplots(figsize=(10, 4))
        ax1.plot(pe_daily.index, pe_daily['pe'], label='PE')
        ax1.plot(pe_daily.index, pe_daily['p15'], label='P15', linestyle='--')
        ax1.plot(pe_daily.index, pe_daily['p85'], label='P85', linestyle='--')
        ax1.set_ylabel('PE')
        ax1.grid(True)
        ax2 = ax1.twinx()
        ax2.plot(pe_daily.index, pe_daily['pos'], label='仓位(右)', alpha=0.3)
        ax2.set_ylim(-0.05, 1.05)
        ax2.set_ylabel('仓位')
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines+lines2, labels+labels2, loc='upper left')
        plt.title("月频PE与分位及仓位")
        plt.tight_layout()
        plt.show()

    return pe_df, sig_df, result_df, stats


# ================== 主函数运行 ==================

index_code = "000016.XSHG"  # 上证50
start_date = "2011-01-01"   # 建议>=2011，保证滚动窗口有足够历史
end_date   = dt.date.today().strftime("%Y-%m-%d")

# 最近2年（24个月）动态PE阈值，15%低买、85%高卖
pe_df, sig_df, result_df, stats = run_pipeline(
    index_code=index_code,
    start_date=start_date,
    end_date=end_date,
    lookback_months=24,
    low_pct=15,
    high_pct=85,
    cost_per_trade=0.0005,   # 可按券商费率调整
    show_pe_panel=True       # 如需看PE与仓位面板改为True
)
