from scapy.all import rdpcap
import pandas as pd

# name, attackStart (must match run_all.sh)
scenarios = [("s1",8),("s2",8),("s3",8),("s4",6),("s5",10),
             ("s6",8),("s7",100),("s8",100),("s9",7),("s10",9)]

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
data.to_csv("lowrate_dataset.csv", index=False)
print(data.groupby("label").size())
print("Saved lowrate_dataset.csv with", len(data), "rows")
