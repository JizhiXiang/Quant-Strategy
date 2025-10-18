"""
决策树排序模型（Decision Tree Ranking）
1. 造数据：10 个因子 + 人为非线性信号
2. 将连续收益率 -> 排序值（rank 0~1）
3. 网格搜索最佳树参数
4. 输出验证集 Rank IC 与回归指标
"""
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeRegressor, plot_tree
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from scipy.stats import spearmanr

# ---------- 参数区 ----------
RANDOM_STATE = 42
MAX_DEPTH    = [3, 5, 7, 9]
MIN_SPLIT    = [2, 5, 10]
MIN_LEAF     = [1, 2, 5]
CRITERION    = ['squared_error', 'absolute_error']
# ------------------------------

# 1. 造数据：1000 样本，10 因子
X = pd.DataFrame(np.random.randn(1000, 10))
signal = (X[0] > 0.8) & (X[1] < -0.5) | (X[2]**2 + X[3] > 2.5)
ret = signal + 0.3 * np.random.randn(1000)          # 原始连续收益
y = ret.rank(pct=True).values                       # 排序目标 ∈ [0,1]；把原始收益率映射成当日截面内的排序百分位
print("构建数据完成，排序目标已生成。")

# 2. 训练/测试划分
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=RANDOM_STATE)

# 3. 网格搜索
param_grid = dict(
    max_depth=MAX_DEPTH,
    min_samples_split=MIN_SPLIT,
    min_samples_leaf=MIN_LEAF,
    criterion=CRITERION
)
model = GridSearchCV(
    DecisionTreeRegressor(random_state=RANDOM_STATE),
    param_grid,
    cv=5,
    scoring='neg_mean_squared_error',
    n_jobs=-1
)
model.fit(X_train, y_train)
best = model.best_estimator_

# 4. 评估
pred = best.predict(X_test)
rank_ic = spearmanr(pred, y_test)[0]

print("最佳参数 :", model.best_params_)
print("验证 MSE :", mean_squared_error(y_test, pred).round(6))
print("验证 R²   :", r2_score(y_test, pred).round(3))
print("验证 Rank IC:", round(rank_ic, 4))

# # 5. 可视化树（可选）
# import matplotlib.pyplot as plt
# plt.figure(figsize=(18, 8))
# plot_tree(best, filled=True, feature_names=X.columns, rounded=True, fontsize=8)
# plt.title("Decision Tree Ranking Model")
# plt.show()
