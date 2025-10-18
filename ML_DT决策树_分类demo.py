# 决策树DT(Decision Tree) 分类模型 classification model
# 预测次日涨跌

import numpy as np, pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import roc_auc_score

X = pd.DataFrame(np.random.randn(1000, 10))
# 人为构造信号，否则都是抛硬币没什么用
signal = (X[0] > 0.8) & (X[1] < -0.5) | (X[2]**2 + X[3] > 2.5)
y = (signal + 0.05*np.random.randn(1000) > 0.5).astype(int)
print("构建数据完成 Finish build data.")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, stratify=y, random_state=42)

param = dict(
    max_depth=[3,5,7,9],
    min_samples_split=[2,5,10],
    min_samples_leaf=[1,2,5],
    criterion=['gini','entropy']
)
clf = GridSearchCV(
    DecisionTreeClassifier(random_state=42),
    param, cv=5, scoring='roc_auc', n_jobs=-1
)
'''
上面的就相当于多重循环，每一次如下：
clf = DecisionTreeClassifier(
    max_depth=md,
    min_samples_split=mss,
    min_samples_leaf=msl,
    criterion=crit,
    random_state=42
)
'''
print("开始训练 start trainning.")
clf.fit(X_train, y_train)
print("结束训练 finish trainning.\n")

print('最佳参数:', clf.best_params_)
print('CV AUC :', clf.best_score_.round(3))
print('测试AUC:', roc_auc_score(y_test, clf.predict_proba(X_test)[:,1]).round(3))
