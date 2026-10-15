
from pathlib import Path
import subprocess
import sys

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data/processed/uas_contracts_classified.csv"
OUTPUT = ROOT / "uas_award_values_by_year.png"

# Refresh the dataset using the existing pipeline
for script in [
    "fetch_data.py",
    "clean_uas_data.py",
    "classify_contracts.py",
]:
    print(f"Running {script}...")
    subprocess.run(
        [sys.executable, str(ROOT / "src" / script)],
        cwd=ROOT,
        check=True,
    )

df = pd.read_csv(DATA)

df["Start Date"] = pd.to_datetime(
    df["Start Date"], errors="coerce"
)
df["Award Amount"] = pd.to_numeric(
    df["Award Amount"], errors="coerce"
)

df = df.dropna(subset=["Start Date", "Award Amount"])
df["Year"] = df["Start Date"].dt.year

categories = ["UAS", "Counter-UAS", "Needs Review"]
labels = ["UAS", "Counter-UAS", "Unknown / Needs Review"]

df = df[df["Technology Category"].isin(categories)]

annual = (
    df.groupby(["Year", "Technology Category"])["Award Amount"]
    .sum()
    .unstack(fill_value=0)
    .reindex(columns=categories, fill_value=0)
    .sort_index()
)

# Display the observed contract-start years
years = annual.index.to_numpy()
values = annual.to_numpy() / 1e9
totals = values.sum(axis=1)

# Black, dark red, and white visual identity
BG = "#080808"
PANEL = "#141414"
RED = "#A51C30"
WHITE = "#F5F5F5"
GRAY = "#666666"
MUTED = "#A8A8A8"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "text.color": WHITE,
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.edgecolor": "#343434",
    "figure.facecolor": BG,
    "axes.facecolor": PANEL,
    "savefig.facecolor": BG,
})

fig, ax = plt.subplots(figsize=(16, 9), dpi=160)

fig.subplots_adjust(
    left=0.10, right=0.95,
    top=0.76, bottom=0.19
)

colors = [RED, WHITE, GRAY]
bottom = np.zeros(len(years))

for i, label in enumerate(labels):
    ax.bar(
        years,
        values[:, i],
        bottom=bottom,
        color=colors[i],
        width=0.72,
        label=label,
        edgecolor=BG,
        linewidth=0.8,
        zorder=3,
    )
    bottom += values[:, i]

# Total-value trend overlay
ax.plot(
    years, totals,
    color="#E2A0AA",
    linewidth=2.3,
    marker="o",
    markersize=5,
    zorder=5,
)

# Label the latest observed year
if len(years):
    ax.annotate(
        f"${totals[-1]:,.1f}B",
        (years[-1], totals[-1]),
        xytext=(0, 15),
        textcoords="offset points",
        ha="center",
        color=WHITE,
        fontsize=11,
        fontweight="bold",
    )

# Show every second year to improve readability
tick_years = np.arange(1996, 2027, 2)

ax.set_xticks(tick_years)
ax.set_xticklabels(
    [str(y) for y in tick_years],
    fontsize=10
)

ax.set_xlim(1995, 2027)years])

ax.yaxis.set_major_formatter(
    ticker.FuncFormatter(lambda v, _: f"${v:,.0f}B")
)

ax.set_ylabel(
    "Summed reported award values (USD billions)",
    labelpad=15
)

ax.grid(
    axis="y",
    color="#333333",
    linestyle="--",
    linewidth=0.7,
    alpha=0.8,
    zorder=0,
)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(axis="both", length=0, pad=10)
ax.set_axisbelow(True)
ax.set_ylim(bottom=0, top=max(totals.max() * 1.18, 1))

fig.text(
    0.10, 0.94,
    "DEFENSE ACQUISITION INTELLIGENCE",
    color="#D04A5E",
    fontsize=11,
    fontweight="bold",
)

fig.text(
    0.10, 0.875,
    "UAS & COUNTER-UAS CONTRACT VALUES",
    color=WHITE,
    fontsize=23,
    fontweight="bold",
)

fig.text(
    0.10, 0.825,
    "Reported award values by contract start year",
    color=MUTED,
    fontsize=13,
)

fig.legend(
    loc="lower left",
    bbox_to_anchor=(0.10, 0.105),
    ncol=3,
    frameon=False,
    labelcolor=WHITE,
    fontsize=11,
)

fig.text(
    0.10, 0.045,
    "SOURCE: USAspending.gov  |  Keyword-discovered DoD awards  |  "
    "Preliminary technology classification",
    color=MUTED,
    fontsize=9,
)

fig.text(
    0.10, 0.021,
    "Award values grouped by start year; not annual obligations. "
    "Search results are capped and may include older awards.",
    color=MUTED,
    fontsize=9,
)

fig.savefig(OUTPUT, dpi=220, facecolor=BG)
plt.close(fig)

print(f"\nGraph created: {OUTPUT}")
print("\nAnnual values (USD billions):")
print((annual / 1e9).round(2).to_string())
