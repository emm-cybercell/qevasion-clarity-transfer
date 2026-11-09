# -*- coding: utf-8 -*-
"""Draw an abstract 'question & evasive answer' cover illustration that
matches the deck palette (deep navy / amber), used on the title slide."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Ellipse

FIG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "results", "figures")
os.makedirs(FIG, exist_ok=True)

NAVY = "#16324F"
NAVY2 = "#1F4E79"
AMBER = "#E8A33D"
MIST = "#3A6491"

rng = np.random.default_rng(7)
fig, ax = plt.subplots(figsize=(6.2, 7.5))
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(NAVY)
ax.set_xlim(0, 10)
ax.set_ylim(0, 12)
ax.axis("off")

# dotted texture
xs, ys = np.meshgrid(np.linspace(0.4, 9.6, 24), np.linspace(0.4, 11.6, 30))
ax.scatter(xs, ys, s=1.5, color="#FFFFFF", alpha=0.05)

def bubble(x, y, w, h, color, alpha, tail="left", ec=None):
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.18,rounding_size=0.55",
                       fc=color, ec=ec or color, lw=1.6, alpha=alpha, zorder=3)
    ax.add_patch(b)
    tx = x + 0.9 if tail == "left" else x + w - 0.9
    ax.add_patch(plt.Polygon([[tx, y + 0.05], [tx + 0.55, y + 0.05],
                              [tx - 0.15 if tail == "left" else tx + 0.75, y - 0.75]],
                             fc=color, ec=color, alpha=alpha, zorder=3))

# a big amber question bubble
bubble(1.3, 7.6, 5.4, 3.0, AMBER, 0.96, tail="left")
ax.text(4.0, 9.05, "?", fontsize=64, ha="center", va="center",
        color=NAVY, fontweight="bold", zorder=4)
ax.text(4.0, 8.15, "QUESTION", fontsize=13, ha="center", va="center",
        color=NAVY, fontweight="bold", zorder=4, alpha=0.75)

# a hazy answer bubble (evasive: dotted, fading words)
bubble(3.4, 3.1, 5.3, 3.0, MIST, 0.92, tail="right")
for i, (word, a) in enumerate([("......", 0.95), ("maybe", 0.55),
                               ("......", 0.95)]):
    ax.text(6.0, 5.65 - i * 0.58, word, fontsize=15, ha="center", va="center",
            color="#FFFFFF", alpha=a, zorder=4, family="monospace")
ax.text(6.0, 3.55, "EVASIVE REPLY", fontsize=11, ha="center", va="center",
        color="#FFFFFF", alpha=0.75, fontweight="bold", zorder=4)

# connecting dashed line = classifier judging the pair
ax.plot([3.6, 5.6], [7.35, 6.35], ls=(0, (4, 3)), color="#FFFFFF", lw=1.6,
        alpha=0.5, zorder=2)

# classification chip
chip = FancyBboxPatch((1.2, 0.9), 7.6, 1.25,
                      boxstyle="round,pad=0.14,rounding_size=0.5",
                      fc="#0F2438", ec=AMBER, lw=1.4, zorder=3)
ax.add_patch(chip)
ax.text(5.0, 1.53, "Clear Reply   ·   Ambivalent   ·   Clear Non-Reply",
        fontsize=12.5, ha="center", va="center", color="#FFFFFF", zorder=4)

path = os.path.join(FIG, "cover_art.png")
fig.savefig(path, dpi=220, facecolor=fig.get_facecolor(),
            bbox_inches="tight", pad_inches=0.12)
plt.close(fig)
print("saved", path)
