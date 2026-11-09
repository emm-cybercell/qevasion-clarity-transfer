# -*- coding: utf-8 -*-
"""EDA: label distribution + length distribution figures and stats tables."""
import os
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
FIG = os.path.join(HERE, "results", "figures")
os.makedirs(FIG, exist_ok=True)

plt.rcParams["font.family"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

COARSE = ["Clear Reply", "Ambivalent", "Clear Non-Reply"]
FINE = ["Explicit", "Dodging", "Implicit", "General", "Deflection",
        "Partial/half-answer", "Declining to answer", "Claims ignorance",
        "Clarification"]
COLORS = ["#5B8FF9", "#F6903D", "#5AD8A6", "#9270CA", "#FF9D4D",
          "#269A99", "#6DC8EC", "#E8684A", "#BFBFBF"]


def fig_label_dist(tr, te):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    tc = tr["clarity_label"].value_counts().reindex(COARSE)
    ec = te["clarity_label"].value_counts().reindex(COARSE)
    x = np.arange(3)
    axes[0].bar(x - 0.2, tc / len(tr) * 100, 0.4, label="train", color="#5B8FF9")
    axes[0].bar(x + 0.2, ec / len(te) * 100, 0.4, label="test", color="#F6903D")
    for i, v in enumerate(tc / len(tr) * 100):
        axes[0].text(i - 0.2, v + 0.8, f"{v:.1f}%", ha="center", fontsize=8.5)
    for i, v in enumerate(ec / len(te) * 100):
        axes[0].text(i + 0.2, v + 0.8, f"{v:.1f}%", ha="center", fontsize=8.5)
    axes[0].set_xticks(x); axes[0].set_xticklabels(COARSE, fontsize=9)
    axes[0].set_ylabel("比例 (%)"); axes[0].set_title("粗粒度 clarity_label 分布")
    axes[0].legend()

    fc = tr["evasion_label"].value_counts().reindex(FINE)
    axes[1].barh(range(len(FINE)), fc.values, color=COLORS)
    axes[1].set_yticks(range(len(FINE)))
    axes[1].set_yticklabels(FINE, fontsize=9)
    axes[1].invert_yaxis()
    for i, v in enumerate(fc.values):
        axes[1].text(v + 12, i, str(v), va="center", fontsize=8.5)
    axes[1].set_xlabel("样本数（仅训练集提供细粒度标签）")
    axes[1].set_title("细粒度 evasion_label 分布（9 类）")
    axes[1].set_xlim(0, fc.max() * 1.15)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig1_label_dist.png"), dpi=200)
    plt.close(fig)


def fig_length_dist(tr):
    ql = tr["text_a"].str.split().str.len().clip(upper=80)
    al = tr["text_b"].str.split().str.len().clip(upper=1200)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.0))
    axes[0].hist(ql, bins=30, color="#5B8FF9", edgecolor="white")
    axes[0].set_xlabel("问题词数（>80 截断）"); axes[0].set_ylabel("样本数")
    axes[0].set_title(f"问题长度分布（中位数 {tr['text_a'].str.split().str.len().median():.0f} 词）")
    axes[1].hist(al, bins=40, color="#F6903D", edgecolor="white")
    axes[1].axvline(tr["text_b"].str.split().str.len().median(), color="#C33",
                    ls="--", lw=1.2, label="中位数")
    axes[1].set_xlabel("回答词数（>1200 截断）"); axes[1].set_ylabel("样本数")
    axes[1].set_title(f"回答长度分布（中位数 {tr['text_b'].str.split().str.len().median():.0f} 词）")
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig2_length_dist.png"), dpi=200)
    plt.close(fig)


def main():
    tr = pd.read_csv(os.path.join(DATA, "qev_train.csv"))
    te = pd.read_csv(os.path.join(DATA, "qev_test.csv"))

    fig_label_dist(tr, te)
    fig_length_dist(tr)

    stats = {
        "train_size": int(len(tr)),
        "test_size": int(len(te)),
        "train_coarse": tr["clarity_label"].value_counts().to_dict(),
        "test_coarse": te["clarity_label"].value_counts().to_dict(),
        "train_fine": tr["evasion_label"].value_counts().to_dict(),
        "question_words_mean": float(tr["text_a"].str.split().str.len().mean()),
        "question_words_median": float(tr["text_a"].str.split().str.len().median()),
        "answer_words_mean": float(tr["text_b"].str.split().str.len().mean()),
        "answer_words_median": float(tr["text_b"].str.split().str.len().median()),
        "answer_words_p95": float(tr["text_b"].str.split().str.len().quantile(0.95)),
        "answer_words_max": int(tr["text_b"].str.split().str.len().max()),
        "class_ratio_major_to_minor": float(
            tr["clarity_label"].value_counts().max() /
            tr["clarity_label"].value_counts().min()),
    }
    Path(os.path.join(HERE, "results", "eda_stats.json")).write_text(
        json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
