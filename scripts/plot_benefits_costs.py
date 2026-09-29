"""Compare saved annual costs, revenue and monetized GHG contributions.

Input: main local workbook, Net benefits worksheet; headers in INPUT_SCHEMA.md.
Each strategy has a revenue/GHG stacked bar and a separate annual-cost bar.
The vertical axis is logarithmic. A negative GHG contribution is retained
from the input; assess whether this display is appropriate for your scenario.
Output: PNG under OUTPUT/plot_benefits_costs. Currency/time assumptions come
from the user's workbook. No cost or emissions model is recalculated here.
"""

from package_paths import ROOT, DATA, OUTPUT, save_plotly
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_rgb
from matplotlib.patches import Patch

# USER INPUTS
excel_file = DATA / "Analysis" / "costs analysis.xlsb.xlsx"
sheet_name = "Net benefits"
output_folder = OUTPUT / "plot_benefits_costs"
output_name = "benefit_cost_comparison3.png"

color_map = {
    "AD": "#8dd3c7",
    "Composting": "#ffffb3",
    "Mulch": "#bebada",
    "Wood": "#fb8072",
    "Glass": "#80b1d3",
    "Metals": "#fdb462",
    "Plastics": "#b3de69",
    "Paper": "#fccde5",
}


def lighten_color(color, factor=0.5):
    r, g, b = to_rgb(color)
    return (1 - factor * (1 - r), 1 - factor * (1 - g), 1 - factor * (1 - b))


def darken_color(color, factor=0.7):
    r, g, b = to_rgb(color)
    return (r * factor, g * factor, b * factor)


df = pd.read_excel(excel_file, sheet_name=sheet_name)
df.columns = df.columns.str.strip()
df["Process type"] = df["Process type"].str.strip()
df = df.dropna(subset=["Process type"])

df["Total annual cost"] = (
    df["Total annual cost"]
    .astype(str)
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
    .astype(float)
)

df["GHG benefit"] = df["Monetized GHG reduction benefit"]
df["Revenue benefit"] = df["Total  annual benefits from revenues"]

order = ["AD", "Composting", "Mulch", "Wood", "Glass", "Metals", "Plastics", "Paper"]
df["Process type"] = pd.Categorical(df["Process type"], categories=order, ordered=True)
df = df.sort_values("Process type")

x = np.arange(len(df))
width = 0.35
fig, ax = plt.subplots(figsize=(12, 8))

for index, row in df.iterrows():
    position = list(df.index).index(index)
    base_color = color_map[row["Process type"]]
    light = lighten_color(base_color, 0.5)
    dark = darken_color(base_color, 0.7)

    ax.bar(
        x[position] - width / 2,
        row["Revenue benefit"],
        width,
        color=light,
        edgecolor="black",
        hatch="xx",
    )
    ax.bar(
        x[position] - width / 2,
        row["GHG benefit"],
        width,
        bottom=row["Revenue benefit"],
        color=dark,
        edgecolor="black",
        hatch="\\\\",
    )
    ax.bar(
        x[position] + width / 2,
        row["Total annual cost"],
        width,
        color=base_color,
        edgecolor="black",
        hatch="..",
    )

ax.set_xticks(x)
ax.set_xticklabels(df["Process type"], rotation=45, ha="right")
ax.set_ylabel("Annual value ($ in log scale)", fontsize=12)
ax.set_xlabel("Waste diversion strategy", fontsize=12)
ax.set_yscale("log")
ax.set_ylim(bottom=1)
ax.legend(
    handles=[
        Patch(facecolor="lightgray", edgecolor="black", hatch="xxxx", label="Revenue benefit"),
        Patch(facecolor="gray", edgecolor="black", hatch="\\\\", label="Monetized GHG benefit"),
        Patch(facecolor="white", edgecolor="black", hatch="..", label="Total annual cost"),
    ]
)

os.makedirs(output_folder, exist_ok=True)
save_path = os.path.join(output_folder, output_name)
plt.tight_layout()
plt.savefig(save_path, dpi=300, bbox_inches="tight")
plt.close("all")
print(f"Saved to: {save_path}")
