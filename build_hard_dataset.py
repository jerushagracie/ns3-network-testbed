from scapy.all import rdpcap
import pandas as pd

scenarios = [("h1",8),("h2",8),("h3",8),("h4",8),("h5",8),
             ("h6",8),("h7",100),("h8",100),("h9",100),("h10",7)]

all_rows = []
for name, start in scenarios:
    print("Reading", name)
    packets = rdpcap(name + "-2-2.pcap")
    rows = []
    for pkt in packets:
        if pkt.haslayer("IP"):
            rows.append({"time": float(pkt.time), "size": len(pkt)})
    df = pd.DataFrame(rows)
    df["window"] = (df["time"] * 10).astype(int)
    win = df.groupby("window").agg(pkts=("size", "count"), bytes=("size", "sum")).reset_index()
    win["second"] = win["window"] // 10
    sec = win.groupby("second").agg(
        packet_count=("pkts", "sum"),
        total_bytes=("bytes", "sum"),
        max_window=("pkts", "max"),
        avg_window=("pkts", "mean"),
        min_window=("pkts", "min")
    ).reset_index()
    sec["burstiness"] = sec["max_window"] / sec["avg_window"]
    sec["label"] = (sec["second"] >= start).astype(int)
    sec["scenario"] = name
    all_rows.append(sec)

data = pd.concat(all_rows, ignore_index=True)
data = data[(data["second"] >= 2) & (data["second"] <= 19)]
data.to_csv("hard_dataset.csv", index=False)
print(data.groupby("label").size())
print("Saved hard_dataset.csv with", len(data), "rows")
