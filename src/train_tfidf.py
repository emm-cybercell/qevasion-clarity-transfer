# -*- coding: utf-8 -*-
"""Baseline 1 (majority) + Baseline 2 (TF-IDF + Logistic Regression).

Works on any unified dataset (QEvasion coarse, QEvasion fine, QNLI) through
the same adapter fields (text_a, text_b, label).
"""
import os
import json
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import (accuracy_score, f1_score, precision_recall_fscore_support,
                             confusion_matrix, classification_report)

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(HERE, "results")
os.makedirs(RES, exist_ok=True)
SEED = 42

COARSE = ["Clear Reply", "Ambivalent", "Clear Non-Reply"]
FINE = ["Explicit", "Dodging", "Implicit", "General", "Deflection",
        "Partial/half-answer", "Declining to answer", "Claims ignorance",
        "Clarification"]


def make_text(df):
    return " [Q] " + df["text_a"] + " [A] " + df["text_b"]


def evaluate(name, y_true, y_pred, labels, target_names, out):
    acc = accuracy_score(y_true, y_pred)
    mf1 = f1_score(y_true, y_pred, average="macro")
    p, r, f, sup = precision_recall_fscore_support(y_true, y_pred,
                                                   labels=labels,
                                                   zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    out[name] = {
        "accuracy": round(float(acc), 4),
        "macro_f1": round(float(mf1), 4),
        "per_class": {tn: {"precision": round(float(pi), 4),
                           "recall": round(float(ri), 4),
                           "f1": round(float(fi), 4),
                           "support": int(si)}
                      for tn, pi, ri, fi, si in zip(target_names, p, r, f, sup)},
        "confusion_matrix": cm.tolist(),
    }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default="qev_coarse",
                    choices=["qev_coarse", "qev_fine", "qnli"])
    args = ap.parse_args()

    if args.task == "qev_coarse":
        tr = pd.read_csv(os.path.join(HERE, "data", "qev_train.csv"))
        te = pd.read_csv(os.path.join(HERE, "data", "qev_test.csv"))
        names = COARSE
    elif args.task == "qev_fine":
        # the official test split carries no fine-grained labels, so the
        # 9-class models are evaluated on a stratified 10% dev split of train
        tr = pd.read_csv(os.path.join(HERE, "data", "qev_train.csv"))
        tr = tr.dropna(subset=["fine"]).reset_index(drop=True)
        from sklearn.model_selection import train_test_split
        tr, te = train_test_split(tr, test_size=0.1, random_state=SEED,
                                  stratify=tr["fine"])
        tr, te = tr.reset_index(drop=True), te.reset_index(drop=True)
        names = FINE
    else:
        tr = pd.read_csv(os.path.join(HERE, "data", "qnli_train.csv"))
        te = pd.read_csv(os.path.join(HERE, "data", "qnli_dev.csv"))
        names = ["not_entailment", "entailment"]

    Xtr, Xte = make_text(tr), make_text(te)
    ytr, yte = tr["label"].values, te["label"].values
    labels = list(range(len(names)))

    out = {}
    # ---- majority-class baseline -------------------------------------
    maj = np.bincount(ytr).argmax()
    y_pred = np.full_like(yte, maj)
    evaluate("majority", yte, y_pred, labels, names, out)

    # ---- TF-IDF + LR ---------------------------------------------------
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=100000,
                                  sublinear_tf=True, min_df=2)),
        ("lr", LogisticRegression(C=4.0, max_iter=2000, class_weight="balanced",
                                  random_state=SEED)),
    ])
    pipe.fit(Xtr, ytr)
    y_pred = pipe.predict(Xte)
    evaluate("tfidf_lr", yte, y_pred, labels, names, out)

    os.makedirs(os.path.join(RES, "predictions"), exist_ok=True)
    pd.DataFrame({"y_true": yte, "y_pred": y_pred}).to_csv(
        os.path.join(RES, "predictions", f"tfidf_lr_{args.task}.csv"),
        index=False)
    Path(os.path.join(RES, f"baselines_{args.task}.json")).write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
