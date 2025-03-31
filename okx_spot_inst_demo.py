import time
import okx.Trade as Trade
import okx.Account as Account
import okx.MarketData as MarketData

# okx现货买卖操作
# OKX spot trading operation
# 作者威xin（可代写）: yiyou888wx
# X / telegram: TraderMaga59800

# 注意主账号和子账号是分开的，模拟交易也是分开的
#Note that the main account and sub account are separate, and the simulated trading is also separate
# API 初始化 #API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"
# from my_key import *  # 可忽略此行 #This line can be ignored

# 获取现货行情
# Obtain contract market information
# 实盘:0 , 模拟盘：1
#Real: 0, simulation: 1
flag = '1'  
marketDataAPI =  MarketData.MarketAPI(flag=flag)
result = marketDataAPI.get_ticker(instId='BTC-USDT')
print('获取现货行情(BTC-USDT):')
print(result)
print()

# 获取指数K线数据
# Obtain index K-line data
# 注意：不要使用"获取指数历史K线数据"接口，否则获取不到当前数据
#Attention: Do not use the "Get Index Historical K-Line Data" interface, otherwise the current data cannot be obtained
result = marketDataAPI.get_index_candlesticks(
    instId="BTC-USDT",
    limit=10
)
# ['ts', 'o', 'h', 'l', 'c', 'confirm']
print('获取指数K线数据(BTC-USDT):')
print(result)
print()

# 查看账户余额
# View account balance
accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)
result = accountAPI.get_account_balance()
print('查看账户余额:')
print(result)
print()

# 买入现货  buy spot
tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)
result = tradeAPI.place_order(
    instId='BTC-USDT',
    tdMode='cash',
    side='buy',
    ordType='market',
    sz="9000"   # 单位是USDT #The unit is USDT
)
print('买入BTC:')
print(result)
print()

# 卖出现货 sell spot
time.sleep(60)
result = tradeAPI.place_order(
    instId='BTC-USDT',
    tdMode='cash',
    side='sell',
    ordType='market',
    sz="0.1"   # 单位是BTC #The unit is BTC
)
print('卖出BTC:')
print(result)
print()
