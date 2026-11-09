# -*- coding: utf-8 -*-
"""Render LaTeX formulas for the PPT method slide as crisp PNGs."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "results", "figures")
os.makedirs(FIG, exist_ok=True)

FORMULAS = {
    "formula_input.png": (
        r"$\mathbf{h}_{[CLS]} = \mathrm{BERT}([\mathrm{CLS}]\ q\ [\mathrm{SEP}]\ a\ [\mathrm{SEP}])$",
        15),
    "formula_softmax.png": (
        r"$p(c \mid q, a) = \mathrm{softmax}(\mathbf{W}\mathbf{h}_{[CLS]} + \mathbf{b})_c$",
        15),
    "formula_loss.png": (
        r"$\mathcal{L} = -\sum_{c=1}^{C} y_c \log p(c \mid q, a)$",
        15),
    "formula_macrof1.png": (
        r"$\mathrm{Macro\text{-}F1} = \frac{1}{|C|}\sum_{c=1}^{C} \frac{2\,P_c R_c}{P_c + R_c}$",
        15),
}

for name, (tex, fs) in FORMULAS.items():
    fig = plt.figure(figsize=(7.2, 1.0))
    fig.patch.set_alpha(0.0)
    fig.text(0.5, 0.5, tex, fontsize=fs, ha="center", va="center",
             color="#16324F")
    path = os.path.join(FIG, name)
    fig.savefig(path, dpi=260, transparent=True,
                bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print("saved", name)
