import qlib
from qlib.contrib.data.handler import Alpha360

def main():
    # 1. 初始化（路径换成自己的）
    qlib.init(provider_uri="~/Documents/code/my_develop/qlib_data/cn_data_snapshot", region="cn")

    # 2. 只选取 1 只股票、2 个月数据，这样速度快很多
    handler = Alpha360(
        instruments=["SH000905"],       
        start_time="2018-01-01",
        end_time="2018-03-01", 
        freq="day",
        fit_start_time="2018-01-01",    
        fit_end_time="2018-03-01",
    )

    # 3. 取出 feature（158 维）和 label
    features = handler.fetch(col_set="feature")
    labels   = handler.fetch(col_set="label")

    # 4. 看看因子名
    print("Alpha360 因子名（共 %d 个）：" % len(features.columns))
    print(features.columns.tolist())

    # 5. 前5行看长什么样
    print("\n前 5 行 feature：")
    print(features.head())

    print("\n前 5 行 label：")
    print(labels.head())

if __name__ == "__main__":
    main()