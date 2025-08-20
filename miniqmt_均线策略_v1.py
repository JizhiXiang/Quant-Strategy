import time
import datetime
from xtquant import xtdata
# 源代码地址：https://github.com/JizhiXiang/Quant-Strategy
# 参考眼哥均线策略 【15m、120m】【99、128、225】

# 配置
FREQ = "15m"    # 15分钟K线  # 经测试，有时候qmt获取15m有bug，此时切换到1d、5m等，再重试15m
MA_LIST = [99, 128, 225]  # 均线列表
STOCK_CODE = "000001.SH"  # 股票代码
ONLY_TRADING_TIME = False  # 仅交易时间监控, True 仅在交易时间监控, False 24 小时监控

COUNT = 300
INTERVAL = 15*60

# 下载历史
def download_history(stock, period, days=300):
    end = datetime.date.today()
    start = end - datetime.timedelta(days=days)
    xtdata.download_history_data(stock_code=stock, period=period,
                               start_time=start.strftime('%Y%m%d'),
                               end_time=end.strftime('%Y%m%d'))

# 获取股票名称
def get_stock_name(stock: str):
    try:
        d = xtdata.get_instrument_detail(stock)
        return d.get('InstrumentName', '未知股票') if d else '未知股票'
    except:
        pass
    return '未知股票'

# 判断交易时间
def is_trade_time():
    now = datetime.datetime.now()
    if now.weekday() >= 5:
        return False
    t = now.time()
    return (datetime.time(9,30) <= t <= datetime.time(11,30)) or \
           (datetime.time(13,0) <= t <= datetime.time(15,0))

# 获取均线状态
def get_ma_status(code, freq, ma_list):
    bars = xtdata.get_market_data_ex(field_list=["close"], stock_list=[code],
                                  period=freq, count=COUNT)
    if code not in bars or bars[code].empty:
        return None, None, None
    closes = bars[code]['close']
    if len(closes) < max(ma_list):
        return None, None, None
    latest_price = closes.iloc[-1]
    result = {}
    ma_values = {}
    for ma in ma_list:
        if len(closes) >= ma:
            ma_val = closes.iloc[-ma:].mean()
            diff_pct = (latest_price - ma_val) / ma_val * 100
            result[ma] = diff_pct
            ma_values[ma] = ma_val
    return result, latest_price, ma_values

# ========== 主程序 ==========
if __name__ == "__main__":
    xtdata.enable_hello = False
    print("开始启动...")
    # 订阅实时 K 线
    xtdata.subscribe_quote(STOCK_CODE, period=FREQ, count=300)
    # 下载历史
    download_history(STOCK_CODE, FREQ, days=300)
    stock_name = get_stock_name(STOCK_CODE)

    while True:
        if is_trade_time() or not ONLY_TRADING_TIME:
            ma_status, latest_price, ma_values = get_ma_status(STOCK_CODE, FREQ, MA_LIST)
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n{'='*50}\n{ts} {stock_name}({STOCK_CODE})")
            if ma_status and latest_price is not None:
                print(f"当前价格: {latest_price:.2f}")
                for ma, pct in ma_status.items():
                    pos = "上方" if pct > 0 else "下方"
                    print(f"相对{FREQ[:-1]}-{ma}均线在{pos} {abs(pct):.2f}% (均线价格: {ma_values[ma]:.2f})")
            else:
                print(f"均线数据不足")
            print(f"{'='*50}\n")
        time.sleep(INTERVAL)
