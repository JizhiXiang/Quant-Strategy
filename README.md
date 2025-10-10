# Quant Strategy 量化策略  
qmt、ptrade、okx、bnb、joinquant聚宽  
[点这里readme](README.md) 查看格式更好

这是一个量化代码合集，目前是以qmt、okx、聚宽为主，逐步完善  
麻烦点个**小星星**支持一下哦~  
Please give a **star** to support it.  

## 内容介绍
|  平台  | 说明 | 文件 | 外部链接 | 
|:-------|:-------:|-------:|-------:|
| **聚宽**  | 年均18%，44行代码  | [joinquant_rsrs因子_年均18%收益.py](joinquant_rsrs因子_年均18%收益.py)  | [点击跳转](https://www.joinquant.com/view/community/detail/4b45a0d76897c3463b394a1ef554041a) |
| **聚宽**  | 网格交易，适合震荡  | [joinquant_网格交易_v1.py](joinquant_网格交易_v1.py)  | [点击跳转](https://www.joinquant.com/view/community/detail/fc1595a15fabbfea7bd85d033ba3dbbe) |
| **聚宽**  | macd不一致研究  | [joinquant_计算macd值与同花顺不一致原因探索.py](joinquant_计算macd值与同花顺不一致原因探索.py)  | [点击跳转](https://www.joinquant.com/view/community/detail/6d7405065eaabd64d156ca52b6ed548b) |
| **聚宽**  | 价值投资 选股  | [joinquant_价值投资-选股策略.py](joinquant_价值投资-选股策略.py)  | [点击跳转](https://www.joinquant.com/view/community/detail/3ebb210833ad51d08e225b44dcfc8188) |
| **聚宽**  | 先获取概念板块,对应的股票；最近5年roe均大于当年的平均水平, 最近一年roe排名前30%, 按照板块+roe降序排序  | [joinquant_概念板块+基本面选股.py](joinquant_概念板块+基本面选股.py)  | [点击跳转](https://www.joinquant.com/view/community/detail/d69f30e5adbf3d97a6c901a535e91574) |
| **聚宽**  | 探索指数背后的市盈率PE  | [joinquant_手动计算板块指数的PE.py](joinquant_手动计算板块指数的PE.py)  | [点击跳转](https://www.joinquant.com/view/community/detail/672f025e00eb79ad69458f8ae0dc9f07) |
| **聚宽**  | 在PE低的时候买入,在高的时候卖出  | [joinquant_上证50利用动态PE增强模型.py](joinquant_上证50利用动态PE增强模型.py)  | [点击跳转](https://www.joinquant.com/view/community/detail/77f4163b263ce4ada2e2bd0a42da12fc) |
| ----  |  --------  | --------  | --------  |
| **qmt**  |  macd策略，实时交易  | [qmt_macd策略.py](qmt_macd策略.py)  | [点击跳转](https://blog.csdn.net/2401_82851462/article/details/146592641) |
| **qmt**  |  龙头跟随策略，实时交易  | [qmt_龙头跟随_v1.py](qmt_龙头跟随_v1.py)  |暂无 |
| **miniQmt**  |  眼哥版本均线策略  | [miniqmt_均线策略_v1.py](miniqmt_均线策略_v1.py)  | 暂无 |
| **miniQmt**  |  保存概念板块对应的股票  | [miniqmt_概念板块.py](miniqmt_概念板块.py)  | [点击跳转](https://blog.csdn.net/2401_82851462/article/details/150526288) |
| ----  |  --------  | --------  | --------  |
| **okx**  |  okx现货交易代码  | [okx_spot_inst_demo.py](okx_spot_inst_demo.py)  | [点击跳转](https://blog.csdn.net/2401_82851462/article/details/146811185) |
| **okx**  |  okx合约交易代码  | [okx_contract_swap_demo.py](okx_contract_swap_demo.py)  | [点击跳转](https://blog.csdn.net/2401_82851462/article/details/146639685) |
| ----  |  --------  | --------  | --------  |
| **yfinance库**  |  同时支持A股和BTC等数据,多周期均线策略  | [yfinace_多标的多均线_v1.py](yfinace_多标的多均线_v1.py)  | 暂无 |


## 技术博客详情
| 类型 | 链接 | 说明 |
|:-------|:-------:|-------:|
| **ML4T**  | [ML4T - 第7章第1节 A - 简单线性回归Simple Regression](https://blog.csdn.net/2401_82851462/article/details/151797538)   | ML4T（machine-learning-for-trading）  |
| **ML4T**  | [ML4T - 第7章第1节 B - 多变量线性回归Multiple Regression](https://blog.csdn.net/2401_82851462/article/details/151800340)   |    |
| **ML4T**  | [ML4T - 第7章第1节 C - 随机梯度下降回归 Stochastic Gradient Descent Regression (SGDRegressor)](https://blog.csdn.net/2401_82851462/article/details/151835632)   |    |
| **ML4T**  | [ML4T - 第7章第2节 A - 五因子 Fama-French 模型 (Five Fama-French factors)](https://blog.csdn.net/2401_82851462/article/details/152028438)   |    |
| **ML4T**  | [ML4T - 第7章第2节 B - Fama–MacBeth经典两步法(Fama–MacBeth classic two-step method)](https://blog.csdn.net/2401_82851462/article/details/152030237)   |    |
| **ML4T**  | [ML4T - 第7章第3节 数据准备(preparing the model data)](https://blog.csdn.net/2401_82851462/article/details/152088331)   |    |
| **ML4T**  | [ML4T - Quandl Wiki数据下载和处理(Quandl Wiki Prices)](https://blog.csdn.net/2401_82851462/article/details/152044155)   |    |
| **ML4T**  | [ML4T - 第7章第4节 线性回归统计 Linear Regression for Statistics](https://blog.csdn.net/2401_82851462/article/details/152218052)   |    |
| **ML4T**  | [ML4T - 第7章第5节 用线性回归预测股票回报Prediction stock returns with linear regression](https://blog.csdn.net/2401_82851462/article/details/152312641)   |    |
| **ML4T**  | [ML4T - 第7章第6节 使用Alphalens进行分析 Alphalens Analysis](https://blog.csdn.net/2401_82851462/article/details/152330419)   |    |
| **ML4T**  | [ML4T - 第7章第7节 逻辑回归拟合宏观数据Logistic Regression with Macro Data](https://blog.csdn.net/2401_82851462/article/details/152361155)   |    |
| **ML4T**  | [ML4T - 第7章第8节 利用LR预测股票价格走势Predicting stock price moves with Logistic Regression](https://blog.csdn.net/2401_82851462/article/details/152363089)   |    |
| **ML4T**  | [ML4T - 第8章第0节 数据准备Data prep](https://blog.csdn.net/2401_82851462/article/details/152369143)   |    |
| **ML4T**  | [ML4T - 第8章第1节 蒙特卡洛估计夏普率 Monte Carlo Estimation of Sharpe Ratio](https://blog.csdn.net/2401_82851462/article/details/152370892)   |    |
| ----  |  --------  | --------  |
| **Freqtrade**  |  [Freqtrade - 入门及手动安装记录](https://blog.csdn.net/2401_82851462/article/details/152408528)  | Freqtrade交易机器人 |
| **Freqtrade**  |  [Freqtrade - 快速开始Quick Start](https://blog.csdn.net/2401_82851462/article/details/152457733)  |   |
| **Freqtrade**  |  [Freqtrade - Basics 基础知识](https://blog.csdn.net/2401_82851462/article/details/152449171)  |   |
| **Freqtrade**  |  [Freqtrade - Configuration 所有配置大全](https://blog.csdn.net/2401_82851462/article/details/152509134)  |   |
| **Freqtrade**  |  [Freqtrade - Strategy Quickstart 策略快速入门](https://blog.csdn.net/2401_82851462/article/details/152551811)  |   |


## 关于作者
| 平台 | 链接 | 说明 |
|:-------|:-------:|-------:|
| 微信  | yiyou888wx   | 备注GitHub  |
| 小红书  | 搜"本杰明 李耳"   | 图文解说  |
| 微信群  | 暂无链接   | 技术交流(➕V拉你)  |
| csdn博客  | [点击跳转](https://blog.csdn.net/2401_82851462)   | 博客发布  |
| joinquant聚宽  | [点击跳转](https://www.joinquant.com/view/community/detail/2e31e2d643c391e9eeed79e4d107c0fd)   | 可复制回测  |
| QQ群  | 983459113   | 资料下载  |
| X/telegram  | MangoQuant   | Foreign users  |

注：如果有不错的远程quant工作，可以联系我，感谢~  
Note: If there are any good remote quantitative analyst jobs, feel free to contact me. Thank you  

## 其他 
量化优势：对抗人性、不用盯盘、数据分析  
量化优势显而易见，也是将来发展的趋势，比别人多一条路总是好的。  
有基础的可能看懂我的源码，运行调试修改也比较方便，要是有不太懂的可以问问AI。 



