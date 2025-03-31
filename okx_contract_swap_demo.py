import time
import okx.Trade as Trade
import okx.Account as Account
import okx.MarketData as MarketData

# okx合约开仓平仓操作
# OKX contract opening and closing operations
# 作者威xin（可代写）: yiyou888wx
# X / telegram: TraderMaga59800

# 注意主账号和子账号是分开的，模拟交易也是分开的
# API 初始化 #API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

### ---------------------------------------------------------

# 获取合约行情
# Obtain contract market information
# 实盘:0 , 模拟盘：1
#Real: 0, simulation: 1
flag = '1'  
marketDataAPI =  MarketData.MarketAPI(flag=flag)
result = marketDataAPI.get_ticker(instId='BTC-USDT-SWAP')
print('获取合约行情(BTC-USDT-SWAP):')
print(result)
print()

# 查看账户余额
# View account balance
accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)
result = accountAPI.get_account_balance()
print('查看账户余额:')
print(result)
print()

# 获取用于购买BTC-USDT-SWAP最大可用USDT数量
# Obtain the maximum available USDT quantity for purchasing BTC-USDT-SWAP
result = accountAPI.get_max_avail_size(
    instId="BTC-USDT-SWAP",
    tdMode="isolated"
)
print('获取用于购买BTC-USDT-SWAP最大可用USDT数量:')
print(result)
print()

# 查看持仓信息
# View position information
result = accountAPI.get_positions()
print('查看持仓信息:')
print(result)
print()

### ---------------------------------------------------------

# 查看账户配置（交易模式）
# GET /api/v5/account/config
result = accountAPI.get_account_config()
print('查看账户配置:')
print(result)
print()
# 账户模式 acctLv (Account mode)
# 1：现货模式  Spot mode
# 2：现货和合约模式 Spot and contract models
# 持仓方式 posMode (Position holding method)
# long_short_mode：开平仓模式  可以同时持有多头（买入）和空头（卖出）头寸; The opening and closing mode allows for holding both long (buy) and short (sell) positions simultaneously
# net_mode：买卖模式  基于净头寸; Buy and sell mode based on net position

# 设置账户模式（交易模式） #Set account mode (trading mode)
# POST /api/v5/account/set-account-level
# 这个比较麻烦，官方代码没有实现，我自己(yiyou888wx)实现如下：
#This is quite troublesome as the official code has not been implemented. So I implement it as follows:
Set_Account_Level = "/api/v5/account/set-account-level"
class YiyouAPI(Account.AccountAPI):
    def __init__(self, api_key='-1', api_secret_key='-1', passphrase='-1', use_server_time=None, flag='1',
                 domain='https://www.okx.com', debug=False, proxy=None):
        super().__init__(api_key, api_secret_key, passphrase, use_server_time, flag, domain, debug, proxy)
    def set_account_level(self, acctLv="1"):
        params = {"acctLv": str(acctLv)}
        return self._request_with_params("POST", Set_Account_Level, params)

yiyouAPI = YiyouAPI(apikey, secretkey, passphrase, False, flag)
result = yiyouAPI.set_account_level(acctLv="2")
print('设置账户模式，为现货和合约模式:')
print(result)
print()
result = accountAPI.get_account_config()
print('查看账户配置:')
print(result)
print()


# 获取杠杆倍数
# Obtain leverage ratio
result = accountAPI.get_leverage(
    instId="BTC-USDT-SWAP",
    # 保证金模式: 逐仓 #Margin mode: position by position
    mgnMode="isolated"
)
print('获取杠杆倍数:')
print(result)
print()

# 设置杠杆倍数
# Set leverage ratio
result = accountAPI.set_leverage(
    instId="BTC-USDT-SWAP",
    lever="3",
    mgnMode="isolated",
    posSide="short"
)
print('设置做空杠杆倍数为3:')
print(result)
print()
result = accountAPI.set_leverage(
    instId="BTC-USDT-SWAP",
    lever="4",
    mgnMode="isolated",
    posSide="long"
)
print('设置做多杠杆倍数为4:')
print(result)
print()

# 获取杠杆倍数
# Obtain leverage ratio
result = accountAPI.get_leverage(
    instId="BTC-USDT-SWAP",
    mgnMode="isolated"
)
print('修改后，获取杠杆倍数:')
print(result)
print()

### ---------------------------------------------------------


tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)
# 4倍杠杆做多 （前面设置过）
# Long with 4x leverage (previously set)
result = tradeAPI.place_order(
    instId='BTC-USDT-SWAP',
    tdMode='isolated', # 逐仓模式  #Warehouse by warehouse mode
    # 注意clOrdId不能用下划线 #Note that clOrdId cannot be underlined
    clOrdId='mylong01',
    side='buy',
    posSide="long",
    ordType='market',
    sz="10"  #单位是一张, 即0.01 BTC  #The unit is 0.01 BTC
)
print('4倍杠杆做多:')
print(result)
print()
# 碰到的报错：
# 51000   Parameter clOrdId error 参数错误
# 51010   当前账户模式不支持此操作
# 51169   下单失败，当前合约无持仓，请先取消只减仓设置，再尝试下单
#         Order failed. You don't have any positions in this contract that can be closed.
# 51008   可用余额不足 Order failed. Insufficient USDT balance in account.

time.sleep(60)
# 4倍杠杆做多，减仓
# Long with 4x leverage, reduce position
result = tradeAPI.place_order(
    instId='BTC-USDT-SWAP',
    tdMode='isolated',
    clOrdId='mylong02',
    side='sell',
    posSide="long",
    ordType='market',
    sz="3" 
)
print('4倍杠杆做多，减仓:')
print(result)
print()

time.sleep(60)
# 市价全平
# The market price is completely flat
result = tradeAPI.close_positions(
    instId="BTC-USDT-SWAP",
    mgnMode="isolated",
    posSide="long"
)
print('4倍杠杆做多，市价全平:')
print(result)
print()

time.sleep(60)
# 3倍杠杆做空（前面设置过）
# 3x leverage short selling (previously set)
result = tradeAPI.place_order(
    instId='BTC-USDT-SWAP',
    tdMode='isolated', # 逐仓模式  #Warehouse by warehouse mode
    side='sell',
    posSide="short",
    ordType='market',
    sz="8"
)
print('3倍杠杆做空:')
print(result)
print()

time.sleep(60)
# 3倍杠杆做空减仓
# 3x leverage short selling and reducing positions
result = tradeAPI.place_order(
    instId='BTC-USDT-SWAP',
    tdMode='isolated',
    side='buy',
    posSide="short",
    ordType='market',
    sz="8"
)
print('3倍杠杆做空，减仓:')
print(result)
print('finish')
