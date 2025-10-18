# 决策树DT（Decision Tree）回归模型 regression model
# 预测次日收益率（连续值）

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# ---------- 参数区 ----------
RANDOM_STATE = 42
MAX_DEPTH    = [3, 5, 7, 9]
MIN_SPLIT    = [2, 5, 10]
MIN_LEAF     = [1, 2, 5]
CRITERION    = ['squared_error', 'absolute_error']   # 1.0 之后的新名字
# ------------------------------

# 1. 造数据：10个因子，人为构造非线性信号
X = pd.DataFrame(np.random.randn(1000, 10))
signal = (X[0] > 0.8) & (X[1] < -0.5) | (X[2]**2 + X[3] > 2.5)
y = signal + 0.5*np.random.randn(1000)               # 连续型目标变量
print("构建数据完成 Finish build data.")

# 2. 训练/测试划分
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=RANDOM_STATE)

# 3. 网格搜索
param = dict(
    max_depth=MAX_DEPTH,
    min_samples_split=MIN_SPLIT,
    min_samples_leaf=MIN_LEAF,
    criterion=CRITERION
)
reg = GridSearchCV(
    DecisionTreeRegressor(random_state=RANDOM_STATE),
    param, cv=5, scoring='neg_mean_squared_error', n_jobs=-1
)

print("开始训练 start training.")
reg.fit(X_train, y_train)
print("结束训练 finish training.\n")

# 4. 评估
best = reg.best_estimator_
pred = best.predict(X_test)

print('最佳参数:', reg.best_params_)
print('CV MSE :', (-reg.best_score_).round(6))
print('测试MSE:', mean_squared_error(y_test, pred).round(6))
print('测试R²  :', r2_score(y_test, pred).round(3))