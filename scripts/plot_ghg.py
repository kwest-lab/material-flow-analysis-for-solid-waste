"""Plot annual greenhouse-gas reductions by diversion strategy.

Input: DATA/Analysis/costs analysis.xlsb.xlsx, Carbon cost worksheet.
Food AD and composting columns store baseline-minus-alternative reductions.
Other strategies' Difference values store alternative-minus-baseline and
are negated so positive bars indicate reductions. Units: tCO2e/year.
Output: PNG under OUTPUT/plot_ghg. Labels use three significant figures.
Reads saved Excel values; does not run WARM or recalculate formulas.
"""

from package_paths import ROOT, DATA, OUTPUT, save_plotly
import os
import math
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# USER INPUTS
# =========================
excel_file = DATA / "Analysis" / "costs analysis.xlsb.xlsx"
sheet_name = "Carbon cost"
output_folder = OUTPUT / "plot_ghg"
output_name = "ghg_reduction_by_strategy_V5.png"

# Colors in this order:
# AD, Composting, Mulch, Wood, Glass, Metals, Plastics, Paper
color_map = {
    "AD": "#8dd3c7",
    "Composting": "#ffffb3",
    "Mulch": "#bebada",
    "Wood": "#fb8072",
    "Glass": "#80b1d3",
    "Metals": "#fdb462",
    "Plastics": "#b3de69",
    "Paper": "#fccde5"
}


def format_significant_figures(value, significant_figures=3):
    """Format a number with a fixed number of significant figures and commas."""
    if value == 0:
        return "0"

    decimal_places = significant_figures - int(math.floor(math.log10(abs(value)))) - 1
    rounded_value = round(value, decimal_places)
    return f"{rounded_value:,.{max(decimal_places, 0)}f}"

# =========================
# READ EXCEL
# =========================
source_df = pd.read_excel(excel_file, sheet_name=sheet_name)

# Build Figure 4 values directly from the cost-analysis workbook. The Food row
# contains separate AD and composting reductions (baseline minus alternative).
# Other strategies store Difference as alternative minus baseline, so negate it:
# positive values indicate reductions and negative values indicate increases.
source_df.columns = source_df.columns.str.strip()
source_df["Process type"] = source_df["Process type"].astype("string").str.strip()

food_row = source_df.loc[source_df["Process type"] == "Food"].iloc[0]
other_rows = source_df.loc[
    source_df["Process type"].isin(["Mulch", "Wood", "Glass", "Metals", "Plastics", "Paper"])
].copy()

df = pd.concat(
    [
        pd.DataFrame(
            {
                "Strategy Name": ["AD", "Composting"],
                "GHG reduction MTCO2": [food_row["AD"], food_row["Compost"]],
            }
        ),
        pd.DataFrame(
            {
                "Strategy Name": other_rows["Process type"].to_numpy(),
                "GHG reduction MTCO2": -other_rows["Difference"].to_numpy(),
            }
        ),
    ],
    ignore_index=True,
)

# Force desired plotting order
strategy_order = ["AD", "Composting", "Mulch", "Wood", "Glass", "Metals", "Plastics", "Paper"]
df["Strategy Name"] = pd.Categorical(df["Strategy Name"], categories=strategy_order, ordered=True)
df = df.sort_values("Strategy Name")

# Get colors in matching order
bar_colors = [color_map[s] for s in df["Strategy Name"]]

# =========================
# CREATE OUTPUT FOLDER
# =========================
os.makedirs(output_folder, exist_ok=True)
save_path = os.path.join(output_folder, output_name)

# =========================
# PLOT
# =========================
plt.figure(figsize=(10, 6))
bars = plt.bar(
    df["Strategy Name"],
    df["GHG reduction MTCO2"],
    color=bar_colors,
    edgecolor="black"
)

plt.xlabel("Waste diversion strategy", fontsize=12)
plt.ylabel("Annual GHG reduction (tCO₂e/yr)", fontsize=12)
plt.axhline(0, color="black", linewidth=0.8)
plt.margins(y=0.10)
#plt.title("GHG Reduction by Waste Type", fontsize=14)
plt.xticks(rotation=45, ha="right")

# Place labels outside both positive and negative bars.
for bar, val in zip(bars, df["GHG reduction MTCO2"]):
    plt.annotate(
        format_significant_figures(val),
        xy=(bar.get_x() + bar.get_width() / 2, val),
        xytext=(0, 4 if val >= 0 else -4),
        textcoords="offset points",
        ha="center",
        va="bottom" if val >= 0 else "top",
        fontsize=10
    )

plt.tight_layout()
plt.savefig(save_path, dpi=300, bbox_inches="tight")
plt.close("all")

print(f"Plot saved to:\n{save_path}")
