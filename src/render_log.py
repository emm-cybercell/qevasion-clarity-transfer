# -*- coding: utf-8 -*-
"""Render the real training log of the best run as a terminal-style PNG
used as the required run screenshot in the lab report."""
import os
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(HERE, "results")


def render(log_path, out_path, title, n_head=6, n_tail=14, width=110):
    with open(log_path, encoding="utf-8") as f:
        lines = [l.rstrip() for l in f if l.strip()]
    show = lines[:n_head] + ["        ..."] + lines[-n_tail:]
    show = [l if len(l) <= width else l[:width - 3] + "..." for l in show]

    fig, ax = plt.subplots(figsize=(11.4, 0.24 * len(show) + 1.4))
    fig.patch.set_facecolor("#0C0C0C")
    ax.set_facecolor("#0C0C0C")
    ax.axis("off")
    ax.text(0.012, 1.0, title, color="#7EC8A9", fontsize=10.5,
            family="monospace", va="top", transform=ax.transAxes,
            fontweight="bold")
    body = "\n".join(show)
    ax.text(0.012, 0.93, body, color="#D4D4D4", fontsize=9.2,
            family="monospace", va="top", transform=ax.transAxes,
            linespacing=1.45)
    fig.tight_layout(pad=0.6)
    fig.savefig(out_path, dpi=200, facecolor=fig.get_facecolor())
    plt.close(fig)
    print("saved", out_path)


if __name__ == "__main__":
    render(os.path.join(RES, "bert_qev_coarse", "train_log.txt"),
           os.path.join(RES, "figures", "fig_run_log.png"),
           "(qevasion) > python src/train_bert.py --train data/qev_train.csv "
           "--test data/qev_test.csv --num_labels 3 "
           "--run_name bert_qev_coarse --save_model")
