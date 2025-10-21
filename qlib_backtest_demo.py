from pprint import pprint
import qlib
import pandas as pd
from qlib.utils.time import Freq
from qlib.utils import flatten_dict
from qlib.backtest import backtest, executor
from qlib.contrib.evaluate import risk_analysis
from qlib.contrib.strategy import TopkDropoutStrategy

# 初始化 qlib
qlib.init(provider_uri="~/Documents/code/my_develop/qlib_data/cn_data_snapshot", region="cn")

# 读取预测结果
artifact_path = "./mlruns/376922499957687719/a24025d6cdfd42f49d3877e396bef01f/artifacts"
pred = pd.read_pickle(f"{artifact_path}/pred.pkl")

# 设置回测参数
CSI300_BENCH = "SH000300"
FREQ = "day"

# 提取预测分数作为交易信号
pred_score = pred['score']

STRATEGY_CONFIG = {
    "topk": 50,
    "n_drop": 5,
    "signal": pred_score,
}

EXECUTOR_CONFIG = {
    "time_per_step": "day",
    "generate_portfolio_metrics": True,
}

backtest_config = {
    "start_time": "2017-01-01",
    "end_time": "2020-08-01",
    "account": 100000000,
    "benchmark": CSI300_BENCH,
    "exchange_kwargs": {
        "freq": FREQ,
        "limit_threshold": 0.095,
        "deal_price": "close",
        "open_cost": 0.0005,
        "close_cost": 0.0015,
        "min_cost": 5,
    },
}

def main():
    # 创建策略和执行器对象
    strategy_obj = TopkDropoutStrategy(**STRATEGY_CONFIG)
    executor_obj = executor.SimulatorExecutor(**EXECUTOR_CONFIG)

    # 运行回测
    portfolio_metric_dict, indicator_dict = backtest(executor=executor_obj, strategy=strategy_obj, **backtest_config)
    analysis_freq = "{0}{1}".format(*Freq.parse(FREQ))

    # 获取回测结果
    report_normal, positions_normal = portfolio_metric_dict.get(analysis_freq)

    # 分析结果
    analysis = dict()
    analysis["excess_return_without_cost"] = risk_analysis(
        report_normal["return"] - report_normal["bench"], freq=analysis_freq
    )
    analysis["excess_return_with_cost"] = risk_analysis(
        report_normal["return"] - report_normal["bench"] - report_normal["cost"], freq=analysis_freq
    )

    analysis_df = pd.concat(analysis)  # type: pd.DataFrame

    # 打印结果
    pprint(f"The following are analysis results of benchmark return({analysis_freq}).")
    pprint(risk_analysis(report_normal["bench"], freq=analysis_freq))

    pprint(f"The following are analysis results of the excess return without cost({analysis_freq}).")
    pprint(analysis["excess_return_without_cost"])

    pprint(f"The following are analysis results of the excess return with cost({analysis_freq}).")
    pprint(analysis["excess_return_with_cost"])


if __name__ == '__main__':
    main()
    