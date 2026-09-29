"""Generate a material-flow Sankey diagram from a user-supplied workbook.

Input: DATA/Sankey Plotly/data_V5.xlsx, first worksheet. See INPUT_SCHEMA.md.
Each node has an integer ID, label and color; each link has source/target IDs
and a nonnegative mass flow. PAPER_COLUMNS defines the expected labels and
horizontal layout. Node heights use max(total inflow, total outflow); this
layout convention is not a mass-balance check.
Output: self-contained Sankey HTML and node-position CSV in OUTPUT.
Neither the private study data nor generated results are distributed.
"""

from package_paths import ROOT, DATA, OUTPUT, save_plotly
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go


DATA_FILE = DATA / "Sankey Plotly" / "data_V5.xlsx"
POSITION_TABLE_FILE = OUTPUT / "node_positions_v5.csv"
TOP_MARGIN = 0.05
BOTTOM_MARGIN = 0.95
COLUMN_GAP = 0.02
PAPER_COLUMNS = {
    0.05: ["SWACO Waste"],
    0.18: [
        "Green Waste",
        "Wood waste",
        "Metal Waste",
        "Plastic",
        "Glass",
        "Paper",
    ],
    0.38: [
        "Food Waste",
        "Yard Waste",
        "Palletes",
        "Recovered Metals",
        "Plastic resins",
        "Cullets",
        "Recovered Paper",
    ],
    0.58: [
        "Anaerobic Digestion",
        "Contaminants",
        "Mulching",
    ],
    0.78: ["Composting", "Biomethane"],
    0.95: ["Fertilizer", "Landfill"],
}


def load_sankey_inputs(excel_file: Path):
    df = pd.read_excel(excel_file)

    links = df.loc[
        df["Source No."].notna() & df["Target No."].notna() & df["Values"].notna(),
        ["Source No.", "Target No.", "Values"],
    ].copy()
    links["Source No."] = links["Source No."].astype(int)
    links["Target No."] = links["Target No."].astype(int)

    nodes = df.loc[
        df["Labels"].notna() & df["Lable No."].notna(),
        ["Lable No.", "Labels", "Color", "X_Nodes"],
    ].copy()
    nodes["Lable No."] = nodes["Lable No."].astype(int)
    nodes["Labels"] = nodes["Labels"].astype(str).str.strip()
    nodes["Color"] = (
        nodes["Color"].astype(str).str.strip().str.replace('"', "", regex=False)
    )
    nodes = nodes.sort_values("Lable No.").reset_index(drop=True)

    return links, nodes


def compute_node_values(links: pd.DataFrame, nodes: pd.DataFrame):
    node_values = {}
    for node_id, label in zip(nodes["Lable No."], nodes["Labels"]):
        incoming = links.loc[links["Target No."] == node_id, "Values"].sum()
        outgoing = links.loc[links["Source No."] == node_id, "Values"].sum()
        node_values[label] = float(max(incoming, outgoing))
    return node_values


def compute_positions(nodes: pd.DataFrame, node_values: dict):
    position_rows = []
    center_y_by_label = {}
    x_by_label = {}

    for x_value, labels in PAPER_COLUMNS.items():
        total_value = sum(node_values[label] for label in labels)
        usable_height = BOTTOM_MARGIN - TOP_MARGIN - (COLUMN_GAP * (len(labels) - 1))
        scale = usable_height / total_value if total_value else 0.0

        cursor = TOP_MARGIN
        for label in labels:
            height = node_values[label] * scale
            top_y = cursor
            bottom_y = top_y + height
            center_y = top_y + (height / 2)

            center_y_by_label[label] = center_y
            x_by_label[label] = float(x_value)
            position_rows.append(
                {
                    "label": label,
                    "x": float(x_value),
                    "y": float(center_y),
                    "top_y": float(top_y),
                    "bottom_y": float(bottom_y),
                    "center_y": float(center_y),
                    "node_value": float(node_values[label]),
                }
            )

            cursor = bottom_y + COLUMN_GAP

    positions = pd.DataFrame(position_rows)
    missing_labels = sorted(set(nodes["Labels"]) - set(x_by_label))
    if missing_labels:
        raise ValueError(f"Missing paper x-position mapping for: {missing_labels}")

    return center_y_by_label, x_by_label, positions


def build_figure(
    links: pd.DataFrame,
    nodes: pd.DataFrame,
    center_y_by_label: dict,
    x_by_label: dict,
):
    node_id_to_index = {
        node_id: index for index, node_id in enumerate(nodes["Lable No."].tolist())
    }

    x_positions = [x_by_label[label] for label in nodes["Labels"]]
    y_positions = [center_y_by_label[label] for label in nodes["Labels"]]

    source = [node_id_to_index[node_id] for node_id in links["Source No."].tolist()]
    target = [node_id_to_index[node_id] for node_id in links["Target No."].tolist()]
    values = links["Values"].astype(float).tolist()

    fig = go.Figure(
        go.Sankey(
            arrangement="fixed",
            node=dict(
                pad=20,
                thickness=30,
                line=dict(color="black", width=0.5),
                label=nodes["Labels"].tolist(),
                x=x_positions,
                y=y_positions,
                color=nodes["Color"].tolist(),
            ),
            link=dict(
                source=source,
                target=target,
                value=values,
                hovertemplate=(
                    "Source: %{source.label}<br>"
                    "Target: %{target.label}<br>"
                    "Flow: %{value}<extra></extra>"
                ),
            ),
        )
    )

    fig.update_layout(title_text="SWACO Waste Flow (tons/year)", font_size=12)
    return fig


def main():
    links, nodes = load_sankey_inputs(DATA_FILE)
    node_values = compute_node_values(links, nodes)
    center_y_by_label, x_by_label, positions = compute_positions(nodes, node_values)

    positions = positions[["label", "x", "y", "node_value"]].round(6)
    positions.to_csv(POSITION_TABLE_FILE, index=False)

    print(f"\nSaved node position table to: {POSITION_TABLE_FILE}")
    print(positions.to_string(index=False))

    fig = build_figure(links, nodes, center_y_by_label, x_by_label)
    save_plotly(fig, OUTPUT / "sankey_diagram_v5.png", width=1500, height=800)


if __name__ == "__main__":
    main()
