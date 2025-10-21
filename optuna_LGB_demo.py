import optuna

print("======================1.Optuna 简单介绍======================")

# 定义目标函数
def objective(trial):
    x = trial.suggest_float('x', -10, 10)  # 搜索范围
    return (x - 2) ** 2  # 最小化目标

# 创建 study 对象并开始优化
study = optuna.create_study(direction='minimize')
study.optimize(objective, n_trials=30)

# 输出最优参数
print("最优参数:", study.best_params)
print("最优值:", study.best_value)



print("======================2.Optuna+LightGBM应用实例======================")
import optuna
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from lightgbm import LGBMClassifier
from sklearn.metrics import accuracy_score

# 加载数据
X, y = load_breast_cancer(return_X_y=True)
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# 定义目标函数
def objective(trial):
    params = {
        'objective': 'binary',
        'metric': 'binary_logloss',
        'boosting_type': 'gbdt',
        'num_leaves': trial.suggest_int('num_leaves', 10, 100),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
        'feature_fraction': trial.suggest_float('feature_fraction', 0.5, 1.0),
        'bagging_fraction': trial.suggest_float('bagging_fraction', 0.5, 1.0),
        'bagging_freq': trial.suggest_int('bagging_freq', 1, 7),
        'min_child_samples': trial.suggest_int('min_child_samples', 5, 30),
    }

    model = LGBMClassifier(**params, verbose=-1)
    model.fit(X_train, y_train)
    preds = model.predict(X_val)
    return accuracy_score(y_val, preds)

# 创建 study 并优化
study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=30)

print("最佳参数:", study.best_params)
print("最佳准确率:", study.best_value)
