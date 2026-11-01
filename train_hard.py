import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

features = ["packet_count", "total_bytes", "max_window", "avg_window", "min_window", "burstiness"]
train = pd.read_csv("lowrate_dataset.csv")
test = pd.read_csv("hard_dataset.csv")

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(train[features], train["label"])
test["pred"] = model.predict(test[features])

print("Accuracy on hard data:", round(accuracy_score(test["label"], test["pred"]), 3))
tn, fp, fn, tp = confusion_matrix(test["label"], test["pred"]).ravel()
print("Detection rate:", round(tp / (tp + fn), 3))
print("False-positive rate:", round(fp / (fp + tn), 3))
print("\nPer scenario accuracy:")
for s, g in test.groupby("scenario"):
    print(s, round(accuracy_score(g["label"], g["pred"]), 2))
