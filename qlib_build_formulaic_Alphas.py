# 参考：https://qlib.readthedocs.io/en/latest/advanced/alpha.html

import qlib
from qlib.data.dataset.loader import QlibDataLoader

qlib.init(provider_uri="~/Documents/code/my_develop/qlib_data/cn_data_snapshot", region="cn")

MACD_EXP = '(EMA($close, 12) - EMA($close, 26))/$close - EMA((EMA($close, 12) - EMA($close, 26))/$close, 9)/$close'
fields = [MACD_EXP, '$close', 'Mean($close, 3)', '$high-$low']
names = ['MACD', 'close', 'close_mean3', 'diff']

labels = ['Ref($close, -2)/Ref($close, -1) - 1', 'Ref($close, -5)/Ref($close, -1) - 1'] # label
# 注意：label中Ref($close, -2)是往将来看，用来计算标签的。 MACD中EMA($close, 12)是往历史看，不能用未来函数。
label_names = ['LABEL0', 'LABEL1']
data_loader_config = {
    "feature": (fields, names),
    "label": (labels, label_names)
}
data_loader = QlibDataLoader(config=data_loader_config)
df = data_loader.load(instruments=["SH000905"], start_time='2018-01-01', end_time='2018-02-01')
print(df)
