
# 这里仅为源代码展示，若复制需要从以下url进入
# https://www.joinquant.com/view/community/detail/6d7405065eaabd64d156ca52b6ed548b

# 一般人用talib来计算macd
import talib

class G:pass
g = G()

g.security = '000333.XSHE'
df = get_price(g.security, end_date='2025-05-21', count=50, frequency='daily', fields=['close'])
closes = df['close'].values
print(f'closes:{closes}')

dif, dea, macd = talib.MACD(closes, 12, 26, 9)
print('DIF:', dif[-10:])
print('DEA:', dea[-10:])
print('MACD:', macd[-10:])




# 研究差异（原创）
'''
我们可以根据以下几点，来判断：

a.数据是否对上
closes收盘价和通达信上面显示的收盘价是否一致

b.参数是否相同
macd需要设置3个参数，要保证和通达信参数一致。比如这里均为12, 26, 9

c.用talib计算出来的macd值需要乘以2
也就是 (dif - dea) * 2，否则永远对不上

d.数据量要稍大一点【核心关键】
由于EMA初始化方式不同，talib和通达信在初期几天（尤其是前 30 天左右），MACD 指标差异明显，随着数据长度增长会逐渐收敛。
所以，我们可以设置数量设置大一点，比如为200
'''



# 改进之后
df = get_price(g.security, end_date='2025-05-21', count=200, frequency='daily', fields=['close'])
closes = df['close'].values
dif, dea, macd = talib.MACD(closes, 12, 26, 9)
# 通达信的 MACD 是 (dif - dea) * 2
macd_tdx = (dif - dea) * 2
# 最后对比末尾部分值
print(dif[-10:])
print(dea[-10:])
print(macd_tdx[-10:])

# 到此，结果完全一致，对上了！




# 手动实现macd（不依赖talib库）也能对上
import numpy as np

def ema_tdx(data, period):
    """通达信风格的EMA，初始值为第一个价格"""
    ema = np.zeros_like(data)
    alpha = 2 / (period + 1)
    ema[0] = data[0]
    for i in range(1, len(data)):
        ema[i] = alpha * data[i] + (1 - alpha) * ema[i - 1]
    return ema

def macd_tdx(close, short=12, long=26, mid=9):
    """通达信风格的MACD计算"""
    ema_short = ema_tdx(close, short)
    ema_long = ema_tdx(close, long)
    dif = ema_short - ema_long
    dea = ema_tdx(dif, mid)
    macd = 2 * (dif - dea)
    return dif, dea, macd

# 使用通达信风格计算 MACD
dif, dea, macd = macd_tdx(closes)

# 打印最近几天的结果
print('DIF:', dif[-10:])
print('DEA:', dea[-10:])
print('MACD:', macd[-10:])
