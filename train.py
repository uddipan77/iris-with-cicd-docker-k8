from pathlib import Path
import joblib
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

def main():
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    clf = LogisticRegression(max_iter=200)
    clf.fit(X_train, y_train)
    acc = accuracy_score(y_test, clf.predict(X_test))

    out = Path("app") / "model.joblib"
    out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, out)
    print(f"Saved model to {out.resolve()} (test accuracy={acc:.3f})")

if __name__ == "__main__":
    main()
