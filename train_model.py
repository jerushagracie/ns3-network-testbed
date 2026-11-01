import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

data = pd.read_csv("lowrate_dataset.csv")

features = ["packet_count", "total_bytes", "max_window", "avg_window", "min_window", "burstiness"]
X = data[features]
y = data["label"]

# Test 1: random 70/30 split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
pred = model.predict(X_test)
print("TEST 1 - random split accuracy:", round(accuracy_score(y_test, pred), 3))
print(confusion_matrix(y_test, pred))

# Test 2: train on some scenarios, test on scenarios the model never saw
test_scen = ["s3", "s7", "s9"]
train = data[~data["scenario"].isin(test_scen)]
test = data[data["scenario"].isin(test_scen)]
model2 = RandomForestClassifier(n_estimators=100, random_state=42)
model2.fit(train[features], train["label"])
pred2 = model2.predict(test[features])
print("\nTEST 2 - unseen scenarios accuracy:", round(accuracy_score(test["label"], pred2), 3))
print(confusion_matrix(test["label"], pred2))
print(classification_report(test["label"], pred2))

# Which features matter most
print("\nFeature importance:")
for f, imp in sorted(zip(features, model.feature_importances_), key=lambda x: -x[1]):
    print(f, round(imp, 3))
