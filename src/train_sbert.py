# -*- coding: utf-8 -*-
"""Baseline 3: frozen pretrained sentence embeddings (Sentence-BERT,
all-MiniLM-L6-v2) + Logistic Regression head. Represents the
"pretrained text representation without fine-tuning" tier."""
import os
import json
import argparse

import numpy as np
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, f1_score,
                             precision_recall_fscore_support,
                             confusion_matrix)
from sklearn.preprocessing import normalize

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(HERE, "results")
os.makedirs(RES, exist_ok=True)
SEED = 42
MODEL = "sentence-transformers/all-MiniLM-L6-v2"

COARSE = ["Clear Reply", "Ambivalent", "Clear Non-Reply"]
FINE = ["Explicit", "Dodging", "Implicit", "General", "Deflection",
        "Partial/half-answer", "Declining to answer", "Claims ignorance",
        "Clarification"]


def encode(model, df, device):
    """Encode question and answer separately, keep both plus cosine(q, a)."""
    q = df["text_a"].tolist()
    a = df["text_b"].str.slice(0, 2000).tolist()
    eq = model.encode(q, batch_size=128, show_progress_bar=True,
                      device=device, normalize_embeddings=True)
    ea = model.encode(a, batch_size=64, show_progress_bar=True,
                      device=device, normalize_embeddings=True)
    cos = (eq * ea).sum(1, keepdims=True)
    X = np.hstack([eq, ea, cos]).astype(np.float32)
    return normalize(X)


def evaluate(name, y_true, y_pred, labels, target_names, out):
    acc = accuracy_score(y_true, y_pred)
    mf1 = f1_score(y_true, y_pred, average="macro")
    p, r, f, sup = precision_recall_fscore_support(y_true, y_pred,
                                                   labels=labels,
                                                   zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    out[name] = {"accuracy": round(float(acc), 4),
                 "macro_f1": round(float(mf1), 4),
                 "per_class": {tn: {"precision": round(float(pi), 4),
                                    "recall": round(float(ri), 4),
                                    "f1": round(float(fi), 4),
                                    "support": int(si)}
                               for tn, pi, ri, fi, si
                               in zip(target_names, p, r, f, sup)},
                 "confusion_matrix": cm.tolist()}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default="qev_coarse",
                    choices=["qev_coarse", "qev_fine", "qnli"])
    args = ap.parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"

    if args.task == "qev_coarse":
        tr = pd.read_csv(os.path.join(HERE, "data", "qev_train.csv"))
        te = pd.read_csv(os.path.join(HERE, "data", "qev_test.csv"))
        names = COARSE
    elif args.task == "qev_fine":
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

    model = SentenceTransformer(MODEL, device=device)
    Xtr = encode(model, tr, device)
    Xte = encode(model, te, device)
    ytr, yte = tr["label"].values, te["label"].values

    clf = LogisticRegression(C=4.0, max_iter=2000, class_weight="balanced",
                             random_state=SEED)
    clf.fit(Xtr, ytr)
    y_pred = clf.predict(Xte)

    out = {}
    evaluate("sbert_lr", yte, y_pred, list(range(len(names))), names, out)
    pd.DataFrame({"y_true": yte, "y_pred": y_pred}).to_csv(
        os.path.join(RES, "predictions", f"sbert_lr_{args.task}.csv"),
        index=False)
    with open(os.path.join(RES, f"baselines_{args.task}.json"), "r+",
              encoding="utf-8") as f:
        prev = json.load(f)
        prev.update(out)
        f.seek(0); f.truncate()
        json.dump(prev, f, ensure_ascii=False, indent=2)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
