import qlib
from qlib.data import D

qlib.init(provider_uri="/Users/test1/Documents/code/my_develop/qlib_data/cn_data_snapshot", region="cn")

symbol = "SH000905"
df = D.features(
    instruments=[symbol],
    fields=["$open", "$close", "$low", "$high", "$volume"],
    start_time="2010-01-01",
    end_time="2025-01-01"
)

if df.empty:
    print(f"没有找到 {symbol} 的数据，请检查代码或时间范围。")
else:
    print(f"{symbol} 数据共 {len(df)} 条记录。")
    print(df.head())
    print(df.tail())
    df.to_csv(f"{symbol}_data.csv", encoding="utf-8-sig")
    print("保存成功！")
    