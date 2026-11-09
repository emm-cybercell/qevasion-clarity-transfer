# -*- coding: utf-8 -*-
"""Post-training analysis: confusion-matrix figures, per-class bars,
error-sample extraction for the report tables, and coarse<-fine
consistency stats for the label-hierarchy extension."""
import os
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(HERE, "results")
FIG = os.path.join(RES, "figures")
os.makedirs(FIG, exist_ok=True)


def safe_path(base_dir, *paths):
    base = os.path.realpath(os.path.abspath(base_dir))
    target = os.path.realpath(os.path.abspath(os.path.join(base, *paths)))
    if os.path.commonpath([base, target]) != base:
        raise ValueError(f"Path traversal detected: {target} is outside {base}")
    return target

plt.rcParams["font.family"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

COARSE = ["Clear Reply", "Ambivalent", "Clear Non-Reply"]
FINE = ["Explicit", "Dodging", "Implicit", "General", "Deflection",
        "Partial/half-answer", "Declining to answer", "Claims ignorance",
        "Clarification"]
FINE2COARSE = {  # documented hierarchy (Thomas et al., 2024)
    "Explicit": "Clear Reply",
    "Dodging": "Ambivalent", "Implicit": "Ambivalent", "General": "Ambivalent",
    "Deflection": "Ambivalent", "Partial/half-answer": "Ambivalent",
    "Declining to answer": "Clear Non-Reply",
    "Claims ignorance": "Clear Non-Reply",
    "Clarification": "Clear Non-Reply",
}


def plot_cm(cm, names, title, path, figsize=(5.2, 4.4)):
    cm = np.array(cm)
    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(names))); ax.set_yticks(range(len(names)))
    ax.set_xticklabels(names, rotation=28, ha="right", fontsize=9)
    ax.set_yticklabels(names, fontsize=9)
    thresh = cm.max() / 2 if cm.max() else 1
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "#222", fontsize=10)
    ax.set_xlabel("预测标签"); ax.set_ylabel("真实标签"); ax.set_title(title)
    fig.colorbar(im, shrink=0.8)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main():
    # ---------- confusion matrices --------------------------------------
    m = json.load(open(os.path.join(RES, "bert_qev_coarse", "metrics.json"),
                       encoding="utf-8"))
    plot_cm(m["confusion_matrix"], COARSE,
            f"BERT 微调（最佳模型）混淆矩阵\nAcc={m['accuracy']:.3f}  Macro-F1={m['macro_f1']:.3f}",
            os.path.join(FIG, "fig3_cm_bert_coarse.png"))

    base = json.load(open(os.path.join(RES, "baselines_qev_coarse.json"),
                          encoding="utf-8"))
    plot_cm(base["tfidf_lr"]["confusion_matrix"], COARSE,
            f"TF-IDF + LR 基线混淆矩阵\nAcc={base['tfidf_lr']['accuracy']:.3f}  "
            f"Macro-F1={base['tfidf_lr']['macro_f1']:.3f}",
            os.path.join(FIG, "fig4_cm_tfidf.png"))

    fine = json.load(open(os.path.join(RES, "bert_qev_fine", "metrics.json"),
                          encoding="utf-8"))
    plot_cm(fine["confusion_matrix"], FINE,
            "细粒度 9 类混淆矩阵（BERT）", os.path.join(FIG, "fig6_cm_fine.png"),
            figsize=(8.6, 6.4))

    # ---------- model comparison bar chart ------------------------------
    rows = [("多数类基线", base["majority"]),
            ("TF-IDF + LR", base["tfidf_lr"]),
            ("SBERT + LR", base["sbert_lr"]),
            ("BERT 微调", m)]
    fig, ax = plt.subplots(figsize=(7, 4))
    x = np.arange(len(rows)); w = 0.38
    acc = [r[1]["accuracy"] for r in rows]
    mf1 = [r[1]["macro_f1"] for r in rows]
    b1 = ax.bar(x - w / 2, acc, w, label="Accuracy", color="#5B8FF9")
    b2 = ax.bar(x + w / 2, mf1, w, label="Macro-F1", color="#F6903D")
    for b in list(b1) + list(b2):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.012,
                f"{b.get_height():.3f}", ha="center", fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels([r[0] for r in rows], fontsize=10)
    ax.set_ylim(0, 1.0); ax.set_ylabel("得分")
    ax.set_title("QEvasion 粗粒度三分类：各模型总体性能对比（官方测试集）")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig5_model_compare.png"), dpi=200)
    plt.close(fig)

    # ---------- error samples for the report ----------------------------
    te = pd.read_csv(os.path.join(HERE, "data", "qev_test.csv"))
    pred = pd.read_csv(os.path.join(RES, "bert_qev_coarse", "predictions.csv"))
    te = te.reset_index(drop=True)
    te["pred"] = pred["y_pred"]
    te["pred_name"] = te["pred"].map(lambda i: COARSE[i])
    err = te[te["clarity_label"] != te["pred_name"]].copy()
    err["err_len"] = err["text_b"].str.split().str.len()
    # one canonical misclassification per error type
    picks = []
    wants = [
        ("长而空泛", lambda d: d.sort_values("err_len", ascending=False).head(8)),
        ("部分/半回答→误判为明确回答", lambda d: d[d["clarity_label"] == "Ambivalent"]),
        ("隐式回答边界模糊", lambda d: d[(d["clarity_label"] == "Ambivalent") & (d["pred_name"] == "Clear Reply")]),
        ("明确拒答被误判", lambda d: d[d["clarity_label"] == "Clear Non-Reply"]),
        ("明确回答被误判为回避", lambda d: d[(d["clarity_label"] == "Clear Reply") & (d["pred_name"] != "Clear Reply")]),
    ]
    used = set()
    for label, fn in wants:
        sub = fn(err)
        sub = sub[~sub.index.isin(used)]
        if len(sub):
            row = sub.iloc[0]
            used.add(row.name)
            picks.append((label, row))
    dump = []
    for label, row in picks:
        dump.append({
            "type": label,
            "gold": row["clarity_label"], "pred": row["pred_name"],
            "question": str(row["text_a"])[:220],
            "answer_head": str(row["text_b"])[:420],
            "answer_len": int(row["err_len"]),
        })
    Path(safe_path(RES, "error_samples.json")).write_text(
        json.dumps(dump, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---------- coarse-fine consistency (hierarchy extension) -----------
    fine_pred = pd.read_csv(os.path.join(RES, "bert_qev_fine", "predictions.csv"))
    y_fine_gold = fine_pred["y_true"].map(lambda i: FINE[i])
    coarse_gold = y_fine_gold.map(FINE2COARSE)
    hier_pred = fine_pred["y_pred"].map(lambda i: FINE2COARSE[FINE[i]])
    agree_hier = float((hier_pred.values == coarse_gold.values).mean())

    coarse_pred = pd.read_csv(os.path.join(RES, "bert_qev_coarse", "predictions.csv"))
    te2 = te.reset_index(drop=True)
    te2["fine_gold"] = te2["evasion_label"]
    merged = te2.merge(fine_pred, left_index=True, right_index=True,
                       suffixes=("", "_fp"))
    # align: coarse predictions are on the official test set in the same order
    coarse_pred_aligned = coarse_pred["y_pred"].values[:len(merged)]
    coarse_names_pred = [COARSE[i] for i in coarse_pred_aligned]
    fine_names_pred = [FINE[i] for i in merged["y_pred"]]
    agree_models = float(np.mean([FINE2COARSE[a] == b for a, b
                                  in zip(fine_names_pred, coarse_names_pred)]))
    conf = {}
    for a, b in zip(fine_names_pred, coarse_names_pred):
        key = (a, b)
        conf[key] = conf.get(key, 0) + 1
    worst = sorted(conf.items(), key=lambda kv: -kv[1])[:8]
    cons = {
        "hierarchy_macro_consistency_dev": round(agree_hier, 4),
        "two_model_agreement_test": round(agree_models, 4),
        "top_conflict_pairs_fine_pred_vs_coarse_pred": [
            {"fine_pred": a, "coarse_pred": b, "count": c} for (a, b), c in worst],
    }
    Path(safe_path(RES, "hierarchy_consistency.json")).write_text(
        json.dumps(cons, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(cons, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
