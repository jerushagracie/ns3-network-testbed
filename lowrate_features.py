from scapy.all import rdpcap
import pandas as pd

packets = rdpcap("lowrate-test-2-2.pcap")

rows = []
for pkt in packets:
    if pkt.haslayer("IP"):
        rows.append({"time": float(pkt.time), "size": len(pkt), "src": pkt["IP"].src, "proto": pkt["IP"].proto})

df = pd.DataFrame(rows)
df["window"] = (df["time"] * 10).astype(int)
df["second"] = df["time"].astype(int)

win = df.groupby("window").agg(pkts=("size", "count"), bytes=("size", "sum"), sources=("src", "nunique")).reset_index()
win["second"] = win["window"] // 10

sec = win.groupby("second").agg(
    packet_count=("pkts", "sum"),
    total_bytes=("bytes", "sum"),
    max_window=("pkts", "max"),
    avg_window=("pkts", "mean"),
    unique_sources=("sources", "max")
).reset_index()

sec["burstiness"] = sec["max_window"] / sec["avg_window"]
sec["label"] = (sec["second"] >= 8).astype(int)

print(sec)
sec.to_csv("lowrate_features.csv", index=False)
print("Saved to lowrate_features.csv")
