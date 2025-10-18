# 合并后的完整脚本：训练模型 + 计算 IC 指标
# reference: https://qlib.readthedocs.io/en/latest/component/model.html

import qlib
import pandas as pd
from qlib.contrib.model.gbdt import LGBModel
from qlib.contrib.data.handler import Alpha158
from qlib.utils import init_instance_by_config, flatten_dict
from qlib.workflow import R
from qlib.workflow.record_temp import SignalRecord, PortAnaRecord
from qlib.contrib.eva.alpha import calc_ic

# 初始化 Qlib 数据路径
qlib.init(provider_uri="~/Documents/code/my_develop/qlib_data/cn_data_snapshot", region="cn")

market = "csi300"
benchmark = "SH000300"

# 数据处理器配置
data_handler_config = {
    "start_time": "2008-01-01",
    "end_time": "2020-08-01",
    "fit_start_time": "2008-01-01",
    "fit_end_time": "2014-12-31",
    "instruments": market,
}

# 任务配置：模型 + 数据集
task = {
    "model": {
        "class": "LGBModel",
        "module_path": "qlib.contrib.model.gbdt",
        "kwargs": {
            "loss": "mse",
            "colsample_bytree": 0.8879,
            "learning_rate": 0.0421,
            "subsample": 0.8789,
            "lambda_l1": 205.6999,
            "lambda_l2": 580.9768,
            "max_depth": 8,
            "num_leaves": 210,
            "num_threads": 20,
        },
    },
    "dataset": {
        "class": "DatasetH",
        "module_path": "qlib.data.dataset",
        "kwargs": {
            "handler": {
                "class": "Alpha158",
                "module_path": "qlib.contrib.data.handler",
                "kwargs": data_handler_config,
            },
            "segments": {
                "train": ("2008-01-01", "2014-12-31"),
                "valid": ("2015-01-01", "2016-12-31"),
                "test": ("2017-01-01", "2020-08-01"),
            },
        },
    },
}

def main():
    print("【Step 1】初始化模型和数据集...")
    model = init_instance_by_config(task["model"])
    dataset = init_instance_by_config(task["dataset"])

    print("【Step 2】启动实验并训练模型...")
    with R.start(experiment_name="workflow"):
        R.log_params(**flatten_dict(task))
        model.fit(dataset)

        print("【Step 3】生成预测信号...")
        recorder = R.get_recorder()
        sr = SignalRecord(model, dataset, recorder)
        sr.generate()

        print("【Step 4】获取当前实验的 recorder_id，用于后续读取结果...")
        recorder_id = recorder.id
        print(f"当前实验的 recorder_id 为：{recorder_id}")

    # 使用 recorder_id 读取预测结果
    print("【Step 5】读取预测结果并计算 IC...")
    recorder = R.get_recorder(experiment_name="workflow", recorder_id=recorder_id)
    print("已保存的 artifacts：", recorder.list_artifacts())

    # 获取 artifact 路径
    artifact_path = recorder.artifact_uri.replace("file://", "")
    pred = pd.read_pickle(f"{artifact_path}/pred.pkl")
    label = pd.read_pickle(f"{artifact_path}/label.pkl")

    print("预测结果（前5行）：")
    print(pred.head())
    print("预测结果（后5行）：")
    print(pred.tail())
    print("预测结果时间范围：", pred.index.get_level_values('datetime').unique())

    print("标签结果（前5行）：")
    print(label.head())
    print("标签结果（后5行）：")
    print(label.tail())

    # 计算 IC
    ic = calc_ic(pred['score'], label['LABEL0'])

    print("【Step 6】IC 指标统计：")
    print("IC 均值：", ic[0].mean())
    print("IC 标准差：", ic[0].std())
    print("IC 绝对值均值：", ic[0].abs().mean())
    print("Rank IC 均值：", ic[1].mean())
    print("Rank IC 标准差：", ic[1].std())
    print("Rank IC 绝对值均值：", ic[1].abs().mean())

if __name__ == '__main__':
    main()