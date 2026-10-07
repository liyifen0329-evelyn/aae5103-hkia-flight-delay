"""
AAE5103 Assignment 2 - HKIA flight delay analysis (1-18 June 2023).

Reads the 18 daily departure CSV files under flight_data/depart/ and produces:
  Q1  delay rate and average delay for CX, UO and HX
  Q2  number of delayed flights by hour of the day   -> q2_delayed_by_hour.png
  Q3  boarding gate usage frequency per airline      -> q3_gates.png

Run:  python3 my_work.py     (pandas + matplotlib required)
"""
import pandas as pd


# ==========================================================
#  AAE5103 Assignment 2  —— 我自己的代码
#  每一步写完，双击旁边的 run.command 就能看结果
#  想看某个变量长什么样，就写：print(变量名)
# ==========================================================

fd1 = pd.read_csv("flight_data/depart/2023-06-01-depart.csv")
print(fd1)

import glob
files = sorted(glob.glob("flight_data/depart/2023-06-*-depart.csv"))
print("找到文件数:", len(files))
tables = []
for f in files:
    tables.append(pd.read_csv(f))
big = pd.concat(tables, ignore_index=True)
print(big.shape)


status = big["status"].astype(str)
clean = status.str.replace("(", "", regex=False).str.replace(")", "", regex=False)
extra = clean.str.extract(r"Dep (\d{2}:\d{2}) (\d{2})/(\d{2})/(\d{4})")
planned = pd.to_datetime(big["date"] + " " + big["time"])
actual = pd.to_datetime(big["date"] + " " + status.str.extract(r"Dep (\d{2}:\d{2})")[0],
                        errors="coerce")
has_date = extra[0].notna()
act_str = extra[3] + "-" + extra[2] + "-" + extra[1] + " " + extra[0]
actual.loc[has_date] = pd.to_datetime(act_str[has_date])
big["airline"] = big["no"].astype(str).str[:2]
big["actual"] = actual
big["delay_min"] = (actual - planned).dt.total_seconds() / 60

# 检查
print("总行数:", len(big))
print("Cancelled:", (status == "Cancelled").sum())
print("跨天行数:", has_date.sum())
print(big["delay_min"].describe())
# ============ Q1 —— 三家的延误率和平均延误 ============

THREE = ["CX", "UO", "HX"]
t = big[big["airline"].isin(THREE)].copy()

for a in THREE:
    sub = t[t["airline"] == a]
    cancelled = (sub["status"].astype(str) == "Cancelled").sum()
    flew = sub[sub["delay_min"].notna()]              # 有实际起飞时间的（排除取消）
    delayed = flew[flew["delay_min"] >= 30]           # 延误的（晚 30 分钟以上）

    print(f"--- {a} ---")
    print("  记录数:", len(sub), "| 取消:", cancelled, "| 有起飞:", len(flew))
    print("  延误数(>=30min):", len(delayed))
    print("  延误率: %.2f%%" % (100 * len(delayed) / len(flew)))
    print("  平均延误(全部有起飞): %.2f 分钟" % flew["delay_min"].mean())
    print("  平均延误(仅延误航班): %.2f 分钟" % delayed["delay_min"].mean())
    print("  中位数: %.1f | 最大: %.0f" % (flew["delay_min"].median(), flew["delay_min"].max()))

# ============ Q2 —— 每小时延误航班数 ============
import matplotlib.pyplot as plt

three = big[big["airline"].isin(["CX", "UO", "HX"])].copy()

# 用计划起飞时间的「小时」分箱（0-23）
three["hour"] = three["time"].str[:2].astype(int)

delayed = three[three["delay_min"] >= 30]
counts = delayed.groupby("hour").size().reindex(range(24), fill_value=0)

plt.figure(figsize=(10, 4.5))
plt.bar(counts.index, counts.values, color="#4472c4", edgecolor="white")
plt.xticks(range(24))
plt.xlabel("Hour of the day (scheduled departure)")
plt.ylabel("Number of delayed flights (>= 30 min)")
plt.title("Delayed flights by hour of day - CX, UO, HX combined (1-18 Jun 2023)")
plt.grid(axis="y", linestyle=":", alpha=.4)
plt.tight_layout()
plt.savefig("q2_delayed_by_hour.png", dpi=200)
print("图已保存")
print(counts.to_string())

# ============ Q3 —— 三家登机口使用频次 ============

three = big[big["airline"].isin(["CX", "UO", "HX"])].copy()
print("三家记录:", len(three), "| 没分配登机口的:", three["gate"].isna().sum())

three = three.dropna(subset=["gate"]).copy()
three["gate_str"] = three["gate"].astype(int).astype(str)

COL = {"CX": "#c0392b", "UO": "#2471a3", "HX": "#7d6608"}
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

for ax, a in zip(axes, ["CX", "UO", "HX"]):
    s = three[three["airline"] == a]
    top = s["gate_str"].value_counts().head(10)
    ax.bar(top.index, top.values, color=COL[a], edgecolor="white")
    ax.set_title(f"{a}: {len(s)} flights, {s['gate_str'].nunique()} gates")
    ax.set_xlabel("Gate")
    ax.set_ylabel("Flights assigned")
    ax.grid(axis="y", linestyle=":", alpha=.4)
    ax.tick_params(axis="x", rotation=45)

plt.tight_layout()
plt.savefig("q3_gates.png", dpi=200)
print("图已保存")

