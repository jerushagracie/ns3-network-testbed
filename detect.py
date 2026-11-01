from scapy.all import rdpcap
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

def feats(name):
    pk = rdpcap(name + "-2-2.pcap")
    rows = [{"time": float(p.time), "size": len(p)} for p in pk if p.haslayer("IP")]
    df = pd.DataFrame(rows)
    df["window"] = (df["time"] * 10).astype(int)
    win = df.groupby("window").agg(pkts=("size", "count"), bytes=("size", "sum")).reset_index()
    win["second"] = win["window"] // 10
    sec = win.groupby("second").agg(packet_count=("pkts", "sum"), total_bytes=("bytes", "sum"),
          max_window=("pkts", "max"), avg_window=("pkts", "mean"), min_window=("pkts", "min")).reset_index()
    sec["burstiness"] = sec["max_window"] / sec["avg_window"]
    return sec

def rel(g):
    g = g.copy()
    b = g[(g["second"] >= 2) & (g["second"] <= 5)]
    g["ratio_packets"] = g["packet_count"] / b["packet_count"].mean()
    g["ratio_bytes"] = g["total_bytes"] / b["total_bytes"].mean()
    g["ratio_min"] = g["min_window"] / b["avg_window"].mean()
    g["ratio_max"] = g["max_window"] / b["avg_window"].mean()
    return g

F = ["ratio_packets", "ratio_bytes", "ratio_min", "ratio_max", "burstiness"]
tr = pd.read_csv("lowrate_dataset.csv")
tr = pd.concat([rel(g) for _, g in tr.groupby("scenario")])
model = RandomForestClassifier(n_estimators=100, random_state=42).fit(tr[F], tr["label"])

t = rel(feats("dnodef"))
t = t[(t["second"] >= 2) & (t["second"] <= 19)]
t["pred"] = model.predict(t[F])
print(t[["second", "ratio_packets", "pred"]].to_string(index=False))
flag = t[(t["pred"] == 1) & (t["second"] >= 6)]
if len(flag):
    s = int(flag["second"].iloc[0])
    print("\nFirst flagged second:", s, "-> blockAt =", s + 1)
else:
    print("\nNo attack detected")
