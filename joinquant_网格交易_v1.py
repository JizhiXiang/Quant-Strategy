# 导入函数库
from jqdata import *

# 初始化函数，设定基准等等
def initialize(context):
    # 设定沪深300作为基准
    set_benchmark('000300.XSHG')
    # 开启动态复权模式(真实价格)
    set_option('use_real_price', True)
    # 输出内容到日志 log.info()
    log.info('初始函数开始运行且全局只运行一次')
    g.security = '000300.XSHG'

    # 设置网格参数
    g.grid_interval = 0.03  # 网格间距：3%
    g.grid_num = 5         # 网格数量：中间上下各5层
    g.base_price = None     # 后续初始化
    g.position_ratio = 0.2  # 每格仓位变动比例
    # 是否已初始化网格
    g.inited = False

    ### 股票相关设定 ###
    # 股票类每笔交易时的手续费是：买入时佣金万分之三，卖出时佣金万分之三加千分之一印花税, 每笔交易佣金最低扣5块钱
    set_order_cost(OrderCost(close_tax=0.001, open_commission=0.0003, close_commission=0.0003, min_commission=5), type='stock')
    run_daily(market_open, time='open', reference_security='000300.XSHG')


## 开盘时运行函数
def market_open(context):
    price = get_current_data()[g.security].last_price
    
    # 初始化网格价格和初始持仓
    if not g.inited:
        g.base_price = price
        g.buy_grid = [g.base_price * (1 - g.grid_interval * i) for i in range(1, g.grid_num + 1)]
        g.sell_grid = [g.base_price * (1 + g.grid_interval * i) for i in range(1, g.grid_num + 1)]
        g.init_cash = context.portfolio.available_cash
        g.position_value_per_grid = g.init_cash * g.position_ratio
        log.info(f"初始化完成，当前价格：{price}")
        g.inited = True
        return
    
    current_position = context.portfolio.positions[g.security].value
    available_cash = context.portfolio.available_cash
    
    # 买入逻辑：当前价格低于某个买入网格且有资金
    for grid_price in g.buy_grid:
        if price <= grid_price and available_cash >= g.position_value_per_grid:
            amount = g.position_value_per_grid // price
            order(g.security, amount)
            log.info(f"低价买入：价格 {price:.2f} <= 网格 {grid_price:.2f}, 买入 {amount} 股")
            break  # 每次只触发一格操作
    
    # 卖出逻辑：当前价格高于某个卖出网格且有仓位
    for grid_price in g.sell_grid:
        if price >= grid_price and current_position > 0:
            amount = g.position_value_per_grid // price
            hold_amount = context.portfolio.positions[g.security].total_amount
            order(g.security, -min(amount, hold_amount))
            log.info(f"高价卖出：价格 {price:.2f} >= 网格 {grid_price:.2f}, 卖出 {amount} 股")
            break  # 每次只触发一格操作

