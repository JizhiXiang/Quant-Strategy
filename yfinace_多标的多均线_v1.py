import time, yfinance as yf, pandas as pd

tickers = ["510210.SS", "513500.SS", "159920.SZ", "518880.SS", "501018.SS", "159985.SZ", "BTC-USD", "ETH-USD", "SOL-USD"]
mas = [5, 10, 20, 30, 60, 120]
periods = [("1y", "1d", "日K"), ("5y", "1wk", "周K"), ("max", "1mo", "月K")]
rows = []

for i, t in enumerate(tickers, 1):
    try: name = yf.Ticker(t).info.get("shortName", "")
    except: name = ""
    print(f"[{i}/{len(tickers)}] {t} {name}")
    for per, inter, label in periods:
        time.sleep(0.5)
        df = yf.Ticker(t).history(period=per, interval=inter)
        if df.empty or len(df) < max(mas):
            print(f"  ⚠ {label} 数据不足")
            continue
        close = df['Close'].iloc[-1]
        row = {"Ticker": t, "Name": name, "周期": label, "Close": round(close, 2)}
        for m in mas:
            ma = df['Close'].rolling(m).mean().iloc[-1]
            diff = (close - ma) / ma * 100
            row[f"MA{m}"] = round(ma, 2)
            row[f"Diff{m}%"] = round(diff, 2)
            row[f"Above{m}"] = "✅" if close > ma else "❌"
        rows.append(row)

pd.DataFrame(rows).to_excel("ma_check.xlsx", index=False)
print("✅ 完成，已保存 ma_check.xlsx")
