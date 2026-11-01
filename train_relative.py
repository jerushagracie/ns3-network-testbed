import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

def add_relative(df):
    out = []
    for name, g in df.groupby("scenario"):
        g = g.copy()
        base = g[(g["second"] >= 2) & (g["second"] <= 5)]
        g["ratio_packets"] = g["packet_count"] / base["packet_count"].mean()
        g["ratio_bytes"] = g["total_bytes"] / base["total_bytes"].mean()
        g["ratio_min"] = g["min_window"] / base["avg_window"].mean()
        g["ratio_max"] = g["max_window"] / base["avg_window"].mean()
        out.append(g)
    return pd.concat(out, ignore_index=True)

features = ["ratio_packets", "ratio_bytes", "ratio_min", "ratio_max", "burstiness"]

train = add_relative(pd.read_csv("lowrate_dataset.csv"))
test = add_relative(pd.read_csv("hard_dataset.csv"))

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(train[features], train["label"])
test["pred"] = model.predict(test[features])

def report(t, title):
    print(title)
    print("  Accuracy:", round(accuracy_score(t["label"], t["pred"]), 3))
    tn, fp, fn, tp = confusion_matrix(t["label"], t["pred"], labels=[0, 1]).ravel()
    print("  Detection rate:", round(tp / (tp + fn), 3))
    print("  False-positive rate:", round(fp / (fp + tn), 3))

report(test, "ALL hard data (relative features):")
report(test[test["second"] >= 6], "Only seconds 6+ (excludes the baseline seconds):")

print("\nPer scenario accuracy:")
for s, g in test.groupby("scenario"):
    print(s, round(accuracy_score(g["label"], g["pred"]), 2))

print("\nFeature importance:")
for f, imp in sorted(zip(features, model.feature_importances_), key=lambda x: -x[1]):
    print(f, round(imp, 3))
