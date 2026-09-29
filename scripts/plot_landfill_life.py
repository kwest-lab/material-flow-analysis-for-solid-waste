"""Plot saved contributions to landfill-life extension.

Input: main local workbook, Extended landfill life worksheet, Process type
and Lp columns. Rows without numeric Lp are removed and categories are ordered.
Output: PNG under OUTPUT/plot_landfill_life.
The inherited axis labels Lp in years. Verify the workbook's baseline lifetime
and time conversion before interpreting these values as years; this script
only plots saved numbers and does not calculate landfill capacity or lifetime.
"""

from package_paths import ROOT, DATA, OUTPUT, save_plotly
import os
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# USER INPUTS
# =========================
excel_file = DATA / "Analysis" / "costs analysis.xlsb.xlsx"
sheet_name = "Extended landfill life"

output_folder = OUTPUT / "plot_landfill_life"
output_name = "landfill_life_extension.png"

os.makedirs(output_folder, exist_ok=True)
save_path = os.path.join(output_folder, output_name)

# =========================
# COLOR MAP (same as before)
# =========================
color_map = {
    "Food waste": "#8dd3c7",   # map Food → AD color
    "Mulch": "#bebada",
    "Wood": "#fb8072",
    "Glass": "#80b1d3",
    "Metals": "#fdb462",
    "Plastics": "#b3de69",
    "Paper": "#fccde5"
}

# =========================
# READ DATA
# =========================
df = pd.read_excel(excel_file, sheet_name=sheet_name)

# Clean columns
df.columns = df.columns.str.strip().str.replace("\n", " ", regex=False)
df = df.dropna(subset=["Process type", "Lp"])
df["Process type"] = df["Process type"].astype(str).str.strip()
df["Lp"] = pd.to_numeric(df["Lp"], errors="coerce")
df = df.dropna(subset=["Lp"])

# Clean process names
df["Process type"] = df["Process type"].astype(str).str.strip()

# Convert Lp to numeric
df["Lp"] = pd.to_numeric(df["Lp"], errors="coerce")

# =========================
# ORDER (optional but nice)
# =========================
order = ["Food waste", "Mulch", "Wood", "Glass", "Metals", "Plastics", "Paper"]
df["Process type"] = pd.Categorical(df["Process type"], categories=order, ordered=True)
df = df.sort_values("Process type")

# Colors
colors = [color_map.get(x, "#cccccc") for x in df["Process type"]]

# =========================
# PLOT
# =========================
plt.figure(figsize=(10, 6))

bars = plt.bar(
    df["Process type"],
    df["Lp"],
    color=colors,
    edgecolor="black"
)

# Labels
plt.xlabel("Waste diversion strategy", fontsize=12)
plt.ylabel("Contribution to landfill life extension (ΔLₚ in years)", fontsize=12)
#plt.title("Contribution of Waste Streams to Landfill Life Extension", fontsize=14)

plt.xticks(rotation=45, ha="right")

# Value labels
#for bar, val in zip(bars, df["Lp"]):
   # plt.text(
        #bar.get_x() + bar.get_width()/2,
        #val,
        #f"{val:.2f}",
        #ha="center",
        #va="bottom",
        #fontsize=10
   # )

# Grid
plt.grid(axis='y', linestyle='--', alpha=0.3)

# =========================
# SAVE
# =========================
plt.tight_layout()
plt.savefig(save_path, dpi=300, bbox_inches="tight")
plt.close("all")

print(f"Saved to: {save_path}")