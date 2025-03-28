#encoding:gbk
import talib
import datetime
import numpy as np

# 《macd指标》
# qmt量化交易
# 金叉买入，死叉卖出
# 短时间内不重复下单
# 作者威♥: yiyou888wx
# (可开户、代写)
# 量化优势：对抗人性、不用盯盘

class a():
	pass

A = a()

def init(C):
	# 设置股票代码，上海SH结尾，深圳SZ结尾
	A.stock = '000333.SZ'
	# 填写自己的账号
	A.account = '39001785'
	# 设置每次交易的股票数量
	A.volume = 100
	# 设置k线周期
	A.period = '1h'
	# 1小时(3600秒)内不重复下单
	A.trade_time = 3600
	# macd参数配置
	# 分别是短周期、长周期、移动平均周期
	A.param1,A.param2,A.param3 = 12, 26, 9

    # 代码自动下载有用的历史数据，这样无需手动下载
	end = datetime.date.today()
	# 根据你的周期来，days可需改
	start = end - datetime.timedelta(days=10)
	start = start.strftime('%Y%m%d')
	end = end.strftime('%Y%m%d')
	download_history_data(A.stock, A.period, start, end)
	
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
	A.last_trade_time = None


def handlebar(C):
	# 只处理最新数据传来的时候
	if not C.is_last_bar():
		return

	now = datetime.datetime.now()
	now_time = now.strftime('%H%M%S')
	#跳过非交易时间
	if now_time < '093000' or now_time > "150000":
		return

	stock_data_df = C.get_market_data(['close'],[A.stock], A.period, count=50)
	stock_data_closes = np.array(stock_data_df['close'])
	#print(f'stock_data_closes:{stock_data_closes[-5:]}')
	print(f'股票：{A.stock}，当前价格：{stock_data_closes[-1]:.2f}')
	
	# 数据太少 报错！
	if len(stock_data_closes)<50: 
		print('【错误】k线数据不足，无法计算！')
		return
	dif, dea, macd = talib.MACD(stock_data_closes, fastperiod=A.param1, 
								slowperiod=A.param2, signalperiod=A.param3)
	#print(f'macd: {macd[-5:]}')
	
	# 当前时间
	current_time = datetime.datetime.now()

	# 金叉
	if macd[-2]<0 and macd[-1]>=0:
		print(f'进入金叉状态')
		# 如果 last_trade_time 为 None，或者距离上次成交时间超过1小时
		if A.last_trade_time is None or (current_time - A.last_trade_time).total_seconds() > A.trade_time:
			print(f'买入{A.stock}股票，数量：{A.volume}，请保证资金充足!')
			passorder(23,1101,A.account,A.stock,14,-1,A.volume,2,C)
			
			# 记录当前时间
			A.last_trade_time = current_time
		else:
			print(f'一小时内有过交易，不再处理')
		
	# 死叉
	if macd[-2]>0 and macd[-1]<=0:
		print(f'进入死叉状态')
		# 如果 last_trade_time 为 None，或者距离上次成交时间超过1小时
		if A.last_trade_time is None or (current_time - A.last_trade_time).total_seconds() > A.trade_time:
			print(f'卖出{A.stock}股票，数量：{A.volume}，请保证有持仓!')
			passorder(24,1101,A.account,A.stock,14,-1,A.volume,2,C)
			
			# 记录当前时间
			A.last_trade_time = current_time
		else:
			print(f'一小时内有过交易，不再处理')
		