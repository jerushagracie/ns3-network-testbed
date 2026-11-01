import subprocess
import pandas as pd
from scapy.all import rdpcap
from sklearn.ensemble import RandomForestClassifier

settings = {"c1": (0.1, 8), "c2": (0.2, 10), "c3": (0.3, 10), "c4": (0.15, 12)}

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

def load_tp(fn):
    return [float(l.split()[2]) for l in open(fn) if l.startswith("THROUGHPUT")]

F = ["ratio_packets", "ratio_bytes", "ratio_min", "ratio_max", "burstiness"]
tr = pd.read_csv("lowrate_dataset.csv")
tr = pd.concat([rel(g) for _, g in tr.groupby("scenario")])
model = RandomForestClassifier(n_estimators=100, random_state=42).fit(tr[F], tr["label"])

results = []
for name, (on, rate) in settings.items():
    t = rel(feats(name + "nodef"))
    t = t[(t["second"] >= 2) & (t["second"] <= 19)]
    t["pred"] = model.predict(t[F])
    false_alarms = int(((t["pred"] == 1) & (t["second"] < 8)).sum())
    flag = t[(t["pred"] == 1) & (t["second"] >= 8)]
    if len(flag) == 0:
        print(name, "attack not detected")
        continue
    first = int(flag["second"].iloc[0])
    block = first + 1
    cmd = "./ns3 run \"lowrate-test --prefix=" + name + "my --blockAt=" + str(block) + " --onTime=" + str(on) + " --rate=" + str(rate) + "\""
    out = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout
    open("tp_" + name + "_mydef.txt", "w").write(out)
    d = {k: load_tp("tp_" + name + "_" + k + ".txt") for k in ["none", "nodef", "fw", "mydef"]}
    sl = slice(11, 19)  # seconds 12-19
    avg = {k: sum(v[sl]) / len(v[sl]) for k, v in d.items()}
    results.append({"setting": name, "onTime": on, "rate": rate, "detect_delay_s": first - 8,
                    "false_alarms": false_alarms, "none": avg["none"], "nodef": avg["nodef"],
                    "fw": avg["fw"], "mydef": avg["mydef"]})

df = pd.DataFrame(results)
df["loss_nodef_%"] = 100 * (1 - df["nodef"] / df["none"])
df["loss_fw_%"] = 100 * (1 - df["fw"] / df["none"])
df["loss_mydef_%"] = 100 * (1 - df["mydef"] / df["none"])
pd.set_option("display.width", 200)
print(df.round(2).to_string(index=False))
print("\nAVERAGES")
print(df[["detect_delay_s", "false_alarms", "loss_nodef_%", "loss_fw_%", "loss_mydef_%"]].mean().round(2))
df.to_csv("final_results.csv", index=False)
