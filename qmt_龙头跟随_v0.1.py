#encoding:gbk
import datetime
import numpy as np
import pandas as pd

# 《龙头跟随策略 v0.1》
# Leader-Follower Strategy  v0.1
# 大qmt量化交易
'''
假设：股票1先涨起来，股票2、3经常跟着股票1涨。
交易逻辑：代码实时监控股票1，操作股票2、3乘着还没涨就买入。

量化优势：能快速监控、快速买入
难点：首先要保证股票1和2、3有强相关性；并且有几秒到十几秒的时间差
'''
# 本代码实现：
# 多股票跟随龙头自动买入
# 短时间不重复买入


class a():
	pass

A = a()


def init(C):
	# 设置股票代码，(60开头)上海SH结尾，(00、30开头)深圳SZ结尾
	# 龙头股票
	A.stock_leader = '000001.SH'
	# 跟随股票，可以多个
	A.stock_followers = ['000333.SZ', '600160.SH']
	# 填写自己的账号
	A.account = 'xxxxxx'
	# 每个符合条件的跟随股票购买数量
	A.volume = 100
	# 1小时(3600秒)内不重复下单
	A.trade_time = 3600
	
    # 监控逻辑
	# 时间周期，多少秒内的涨幅（这个很重要），需要是3的倍数
	A.jk_time = 12
	# 龙头涨幅
	# 注意：这里的涨幅计算公式为：(price_now-price_before)/price_before，仅和监控时长内的价格有关，和昨天收盘价无关
	A.leader_zf = '3.0%'  # 当龙头股12秒内涨幅超过3%时会触发跟随股的逻辑
	# 跟随股票的涨幅范围，满足条件的才买入。防止已经涨起来了，就没必要买了
	A.follower_low = '0.5%'
	A.follower_high = '2.0%'
	
    
	A.period = 'tick'
	# 账号、资金情况
	account = get_trade_detail_data(A.account, 'STOCK', 'account')
	if len(account)==0:
		print(f'账号{A.account} 未登录 请检查')
		return
	account = account[0]
	# 可用资金
	available_cash = int(account.m_dAvailable)
	# 总资金
	total_cash = int(account.m_dBalance)
	print('【【账户信息】】')
	print(f'账户:{A.account},  总资金:{total_cash}, 可用资金:{available_cash}')

	# 初始化上次成交时间为 None
	A.last_trade_time_dict = {k:None for k in A.stock_followers}


def handlebar(C):
    """主循环：每根 tick 触发一次"""
    # 只处理最新数据
    if not C.is_last_bar():
        return

    now = datetime.datetime.now()
    now_time = now.strftime('%H%M%S')

    # 跳过非交易时间
    if now_time < '093000' or now_time > '150000' or \
       ('113000' < now_time < '130000'):
        print('非交易时间，不处理')
        return

    # 计算需要拉取的 tick 条数
    cout_jk = int(A.jk_time / 3) + 1

    # 拉取实时价格
    stock_detail_df = C.get_market_data_ex(
        ['lastPrice'],
        [A.stock_leader] + A.stock_followers,
        A.period,
        count=cout_jk
    )
    if stock_detail_df is None:
        return

    # 计算龙头股 12 秒涨幅
    leader_prices = stock_detail_df[A.stock_leader]['lastPrice']
    if len(leader_prices) < 2:
        return
    leader_zf = (leader_prices.iloc[-1] - leader_prices.iloc[0]) / leader_prices.iloc[0]

    if leader_zf <= float(A.leader_zf.strip('%')) / 100:
        print(f'龙头股 {A.stock_leader} 12 秒内涨幅 {leader_zf*100:.2f}% 未触发跟随')
        return   # 未触发
    else:
        print(f'龙头股 {A.stock_leader} 12 秒内涨幅 {leader_zf*100:.2f}% 触发跟随')

    # 对每一只跟随股判断是否可买
    for follower in A.stock_followers:
        # 防重：上次成交时间
        last_trade_time = A.last_trade_time_dict[follower]

        if last_trade_time is not None and \
           (now - last_trade_time).total_seconds() < A.trade_time:
            print(f'{follower} 一小时内已交易，跳过')
            continue

        # 计算跟随股 12 秒涨幅
        follower_prices = stock_detail_df[follower]['lastPrice']
        if len(follower_prices) < 2:
            continue
        follower_zf = (follower_prices.iloc[-1] - follower_prices.iloc[0]) / follower_prices.iloc[0]

        low  = float(A.follower_low.strip('%'))  / 100
        high = float(A.follower_high.strip('%')) / 100

        if low <= follower_zf <= high:
            print(f'买入 {follower} 数量 {A.volume}')
            passorder(23, 1101, A.account, follower, 14, -1, A.volume, 2, C)
            # 更新最后成交时间
            A.last_trade_time_dict[follower] = now
        else:
            print(f'{follower} 涨幅 {follower_zf*100:.2f}% 不在区间，不买入')
