"""Draw two abatement panels from saved per-ton costs and diverted masses.

Input: main local workbook, Abt_SA worksheet. Each panel independently sorts
strategies by its cost column. Bar widths equal Landfill Saved; horizontal
positions are cumulative widths. The second-panel inset magnifies AD/Mulch.
The script reads, rather than derives, per-ton costs. Users must verify that
both cost columns and mass widths use compatible denominators.
Output: HTML under OUTPUT/plot_abatement_combined, optional PNG.
"""

from package_paths import ROOT, DATA, OUTPUT, save_plotly
import os

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


excel_file = DATA / "Analysis" / "costs analysis.xlsb.xlsx"
sheet_name = "Abt_SA"
output_folder = OUTPUT / "plot_abatement_combined"
output_name = "abatement_curve_v1_horizontal.png"

os.makedirs(output_folder, exist_ok=True)
save_path = os.path.join(output_folder, output_name)

df = pd.read_excel(excel_file, sheet_name=sheet_name)
df.columns = df.columns.str.strip()
df = df.rename(
    columns={
        "Strategy Name": "Strategy",
        "Landfill Saved": "LandfillSaved",
        "Net Cost (with GHG)": "NetCostWithGHG",
        "Net Cost (without GHG)": "DirectFinancialNetCost",
    }
)
df["Strategy"] = df["Strategy"].astype(str).str.strip()


def with_cumulative_positions(frame, sort_column):
    """Sort one panel and map each stream to its cumulative avoided-mass width."""
    panel_df = frame.sort_values(sort_column).reset_index(drop=True).copy()
    panel_df["x_start"] = panel_df["LandfillSaved"].cumsum() - panel_df["LandfillSaved"]
    panel_df["x_center"] = panel_df["x_start"] + panel_df["LandfillSaved"] / 2
    return panel_df


panel_a = with_cumulative_positions(df, "NetCostWithGHG")
panel_b = with_cumulative_positions(df, "DirectFinancialNetCost")
direct_cost_min = panel_b["DirectFinancialNetCost"].min()
direct_cost_max = panel_b["DirectFinancialNetCost"].max()
direct_cost_span = direct_cost_max - direct_cost_min

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

fig = make_subplots(
    rows=1,
    cols=2,
    shared_xaxes=False,
    horizontal_spacing=0.10,
    subplot_titles=(
        "A. Net costs including monetized GHG",
        "B. Direct net costs",
    ),
)

for _, row in panel_a.iterrows():
    color = color_map.get(row["Strategy"], "#cccccc")
    narrow_bar = row["LandfillSaved"] < 80000
    fig.add_annotation(
        x=row["x_center"],
        y=0,
        text=row["Strategy"],
        showarrow=False,
        yanchor="bottom",
        yshift=8 if narrow_bar else 6,
        textangle=45 if narrow_bar else 0,
        font=dict(size=10 if narrow_bar else 11, color="black", family="Arial"),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=[row["x_center"]],
            y=[row["NetCostWithGHG"]],
            width=[row["LandfillSaved"]],
            marker=dict(color=color, line=dict(width=0)),
            hovertemplate=(
                f"Strategy: {row['Strategy']}<br>"
                f"Landfill saved: {row['LandfillSaved']:,.0f} tons/yr<br>"
                f"Net cost including monetized GHG: ${row['NetCostWithGHG']:,.2f}/ton<extra></extra>"
            ),
            showlegend=False,
        ),
        row=1,
        col=1,
    )

for _, row in panel_b.iterrows():
    color = color_map.get(row["Strategy"], "#cccccc")
    label_y = max(row["DirectFinancialNetCost"], 0)
    fig.add_annotation(
        x=row["x_center"],
        y=label_y,
        text=row["Strategy"],
        showarrow=False,
        yanchor="bottom",
        yshift=6,
        font=dict(size=11, color="black", family="Arial"),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Bar(
            x=[row["x_center"]],
            y=[row["DirectFinancialNetCost"]],
            width=[row["LandfillSaved"]],
            marker=dict(color=color, line=dict(width=0)),
            hovertemplate=(
                f"Strategy: {row['Strategy']}<br>"
                f"Landfill saved: {row['LandfillSaved']:,.0f} tons/yr<br>"
                f"Direct net cost: ${row['DirectFinancialNetCost']:,.2f}/ton<extra></extra>"
            ),
            showlegend=False,
        ),
        row=1,
        col=2,
    )

# The main Panel B axis remains complete; this inset only magnifies its near-zero streams.
zoom_df = panel_b.loc[panel_b["Strategy"].isin(["Mulch", "AD"])]
zoom_x_min = zoom_df["x_start"].min() - 4000
zoom_x_max = (zoom_df["x_start"] + zoom_df["LandfillSaved"]).max() + 4000

for _, row in zoom_df.iterrows():
    color = color_map[row["Strategy"]]
    fig.add_trace(
        go.Bar(
            x=[row["x_center"]],
            y=[row["DirectFinancialNetCost"]],
            width=[row["LandfillSaved"]],
            marker=dict(color=color, line=dict(width=0)),
            hovertemplate=(
                f"Strategy: {row['Strategy']}<br>"
                f"Direct net cost: ${row['DirectFinancialNetCost']:,.2f}/ton<extra></extra>"
            ),
            showlegend=False,
            xaxis="x3",
            yaxis="y3",
        )
    )
    fig.add_annotation(
        x=row["x_center"],
        y=0,
        xref="x3",
        yref="y3",
        text=row["Strategy"],
        showarrow=False,
        yanchor="bottom",
        yshift=3,
        font=dict(size=10, color="black", family="Arial"),
    )

fig.add_annotation(
    x=0.865,
    y=0.48,
    xref="paper",
    yref="paper",
    text="Zoom: Mulch and AD",
    showarrow=False,
    font=dict(size=11, color="black", family="Arial"),
)

fig.update_layout(
    bargap=0,
    showlegend=False,
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(l=90, r=40, t=90, b=75),
    font=dict(family="Arial", size=12, color="black"),
    xaxis3=dict(
        domain=[0.76, 0.98],
        anchor="y3",
        range=[zoom_x_min, zoom_x_max],
        showgrid=False,
        showline=True,
        linecolor="#444444",
        showticklabels=False,
        zeroline=False,
    ),
    yaxis3=dict(
        domain=[0.12, 0.40],
        anchor="x3",
        range=[-5, 5],
        showgrid=False,
        showline=True,
        linecolor="#444444",
        zeroline=True,
        zerolinecolor="#444444",
        zerolinewidth=1,
        tickfont=dict(size=9),
        nticks=3,
    ),
)

fig.update_yaxes(
    title_text="Net cost including monetized GHG (USD/ton)",
    showgrid=False,
    zeroline=True,
    zerolinecolor="#444444",
    zerolinewidth=1.5,
    showline=True,
    linecolor="#444444",
    title_font=dict(size=14),
    tickfont=dict(size=11),
    row=1,
    col=1,
)
fig.update_yaxes(
    title_text="Direct net cost (USD/ton)",
    showgrid=False,
    zeroline=True,
    zerolinecolor="#444444",
    zerolinewidth=1.5,
    showline=True,
    linecolor="#444444",
    title_font=dict(size=14),
    tickfont=dict(size=11),
    range=[
        direct_cost_min - direct_cost_span * 0.06,
        direct_cost_max + direct_cost_span * 0.14,
    ],
    row=1,
    col=2,
)
fig.update_xaxes(
    title_text="Avoided landfill mass (tons/year)",
    showgrid=False,
    showline=True,
    linecolor="#444444",
    title_font=dict(size=14),
    tickfont=dict(size=11),
    row=1,
    col=1,
)
fig.update_xaxes(
    title_text="Avoided landfill mass (tons/year)",
    showgrid=False,
    showline=True,
    linecolor="#444444",
    title_font=dict(size=14),
    tickfont=dict(size=11),
    row=1,
    col=2,
)

save_plotly(fig, save_path, scale=5, width=1600, height=900)

