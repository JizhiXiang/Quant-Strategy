#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Stefan Jansen'  # https://github.com/stefan-jansen/machine-learning-for-trading/blob/main/08_ml4t_workflow/00_data/data_prep.py
__modified_author__ = 'MangoQuant'  # https://blog.csdn.net/2401_82851462

from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

pd.set_option('display.expand_frame_repr', False)
np.random.seed(42)

# PROJECT_DIR = Path('..', '..')
PROJECT_DIR = Path('.')

DATA_DIR = PROJECT_DIR / 'data'


def get_backtest_data(predictions='lasso/predictions'):
    """Combine chapter 7 lr/lasso/ridge regression predictions
        with adjusted OHLCV Quandl Wiki data"""
    # 获取 Quandl 调整后行情
    with pd.HDFStore(DATA_DIR / 'assets.h5') as store:
        prices = (store['quandl/wiki/prices']
                  .filter(like='adj')
                  .rename(columns=lambda x: x.replace('adj_', ''))
                  .swaplevel(axis=0))

    # 获取 Lasso 预测值
    # with pd.HDFStore(PROJECT_DIR / '07_linear_models/data.h5') as store:
    with pd.HDFStore(PROJECT_DIR / 'data.h5') as store:
        print(store.info())
        predictions = store[predictions]

    # 用 Spearman 秩相关系数 衡量“预测值”与“真实值”的单调性，挑整体表现最好的 alpha。
    best_alpha = predictions.groupby('alpha').apply(lambda x: spearmanr(x.actuals, x.predicted)[0]).idxmax()
    predictions = predictions[predictions.alpha == best_alpha]

    # 统一索引名 & 确定时间窗口
    predictions.index.names = ['ticker', 'date']
    tickers = predictions.index.get_level_values('ticker').unique()
    start = predictions.index.get_level_values('date').min().strftime('%Y-%m-%d')
    stop = (predictions.index.get_level_values('date').max() + pd.DateOffset(1)).strftime('%Y-%m-%d')
    
    # 对齐行情 & 预测
    idx = pd.IndexSlice
    prices = prices.sort_index().loc[idx[tickers, start:stop], :]
    predictions = predictions.loc[predictions.alpha == best_alpha, ['predicted']]
    return predictions.join(prices, how='right')


df = get_backtest_data('lasso/predictions')
print(df.info())
# df.to_hdf('backtest.h5', 'data')
df.to_hdf('08_backtest.h5', 'data')
print("08_backtest.h5 saved")
