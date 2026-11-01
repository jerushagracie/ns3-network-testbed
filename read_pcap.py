from scapy.all import rdpcap
import pandas as pd
packets = rdpcap("ddos-test-6-0.pcap")
rows = []
for pkt in packets:
    if pkt.haslayer("IP"):
        rows.append({"time": pkt.time, "size": len(pkt), "src": pkt["IP"].src, "dst": pkt["IP"].dst})
df = pd.DataFrame(rows)
print(df)
df["time"] = df["time"].astype(float)
df["second"] = df["time"].astype(int)

stats = df.groupby("second").agg(
    packet_count=("size", "count"),
    total_bytes=("size", "sum"),
    unique_sources=("src", "nunique")
).reset_index()

print(stats)
