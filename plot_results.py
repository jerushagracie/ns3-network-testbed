import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

names = {"none": "No attack", "nodef": "Attack, no defense",
         "fw": "Static firewall", "mydef": "ML defense (ours)"}
for k, label in names.items():
    y = [float(l) for l in open("col_" + k + ".txt")]
    plt.plot(range(1, len(y) + 1), y, label=label)

plt.axvline(8, color="gray", linestyle="--")
plt.text(8.1, 0.2, "attack starts")
plt.xlabel("Time (s)")
plt.ylabel("Legitimate throughput (Mbps)")
plt.title("Low-Rate DoS: throughput under different defenses")
plt.legend()
plt.grid(True)
plt.savefig("throughput_comparison.png", dpi=150)
print("Saved throughput_comparison.png")

