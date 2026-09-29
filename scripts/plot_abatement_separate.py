"""Draw separate abatement figures using the saved Abt_SA worksheet.

Each panel sorts strategies by its own net-cost column, then places bars at
cumulative avoided-mass positions. Widths represent Landfill Saved and heights
represent the supplied net costs per ton. Negative heights indicate net
benefits under the input's conventions. This script does not normalize or
repair the workbook's cost denominators.
Output: two HTML files under OUTPUT/plot_abatement_separate, optional PNGs.
"""

from package_paths import ROOT, DATA, OUTPUT, save_plotly
import os

import pandas as pd
import plotly.graph_objects as go


excel_file = DATA / "Analysis" / "costs analysis.xlsb.xlsx"
sheet_name = "Abt_SA"
output_folder = OUTPUT / "plot_abatement_separate"

os.makedirs(output_folder, exist_ok=True)

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


def with_cumulative_positions(frame, sort_column):
    """Sort a figure independently and map each stream to its cumulative width."""
    figure_df = frame.sort_values(sort_column).reset_index(drop=True).copy()
    figure_df["x_start"] = figure_df["LandfillSaved"].cumsum() - figure_df["LandfillSaved"]
    figure_df["x_center"] = figure_df["x_start"] + figure_df["LandfillSaved"] / 2
    return figure_df


def create_macc(figure_df, cost_column, y_axis_title, output_name):
    """Create one full-size MACC figure with its own cost-priority order."""
    fig = go.Figure()

    for _, row in figure_df.iterrows():
        color = color_map.get(row["Strategy"], "#cccccc")
        positive_cost = row[cost_column] > 0
        fig.add_annotation(
            x=row["x_center"],
            y=0,
            text=row["Strategy"],
            showarrow=False,
            yanchor="top" if positive_cost else "bottom",
            yshift=-8 if positive_cost else 8,
            textangle=45,
            font=dict(size=20, color="black", family="Arial"),
        )
        fig.add_trace(
            go.Bar(
                x=[row["x_center"]],
                y=[row[cost_column]],
                width=[row["LandfillSaved"]],
                marker=dict(color=color, line=dict(width=0)),
                hovertemplate=(
                    f"Strategy: {row['Strategy']}<br>"
                    f"Landfill saved: {row['LandfillSaved']:,.0f} tons/yr<br>"
                    f"{y_axis_title}: ${row[cost_column]:,.2f}/ton<extra></extra>"
                ),
                showlegend=False,
            )
        )

    cost_min = figure_df[cost_column].min()
    cost_max = figure_df[cost_column].max()
    cost_span = cost_max - cost_min
    fig.update_layout(
        bargap=0,
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=90, r=40, t=60, b=75),
        font=dict(family="Arial", size=16, color="black"),
        xaxis=dict(
            title="Avoided landfill mass (tons/year)",
            showgrid=False,
            showline=True,
            linecolor="#444444",
            title_font=dict(size=20),
            tickfont=dict(size=16),
        ),
        yaxis=dict(
            title=y_axis_title,
            showgrid=False,
            zeroline=True,
            zerolinecolor="#444444",
            zerolinewidth=1.5,
            showline=True,
            linecolor="#444444",
            title_font=dict(size=20),
            tickfont=dict(size=16),
            range=[cost_min - cost_span * 0.06, cost_max + cost_span * 0.14],
        ),
    )

    output_path = os.path.join(output_folder, output_name)
    save_plotly(fig, output_path, scale=5, width=1600, height=900)


ghg_figure = with_cumulative_positions(df, "NetCostWithGHG")
direct_figure = with_cumulative_positions(df, "DirectFinancialNetCost")

create_macc(
    ghg_figure,
    "NetCostWithGHG",
    "Net cost including monetized GHG (USD/ton)",
    "abatement_curve_including_ghg.png",
)
create_macc(
    direct_figure,
    "DirectFinancialNetCost",
    "Direct net cost (USD/ton)",
    "abatement_curve_direct.png",
)
