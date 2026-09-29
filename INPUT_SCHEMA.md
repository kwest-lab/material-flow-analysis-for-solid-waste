# Local input schema

This file describes structure only and contains no study values. Supply your own data in Excel workbooks. Formula cells must have saved numeric results from Excel; openpyxl and pandas do not calculate them.

## Main workbook

Filename: `Analysis/costs analysis.xlsb.xlsx` under `SWACO_INPUT_DIR` or `private_inputs`. This is an XLSX workbook despite the historical filename.

| Worksheet | Required column headers | Used by |
| --- | --- | --- |
| `Net benefits` | `Process type`, `Total annual cost`, `Monetized GHG reduction benefit`, `Total  annual benefits from revenues` (two spaces after Total) | Benefits/costs plot |
| `Carbon cost` | `Process type`, `AD`, `Compost`, `Difference` | GHG plot |
| `Abt_SA` | `Strategy Name`, `Landfill Saved`, `Net Cost (with GHG)`, `Net Cost (without GHG)` | Abatement plots |
| `Extended landfill life` | `Process type`, `Lp` | Landfill-life plot |

The current scripts expect these strategy names: `AD`, `Composting`, `Mulch`, `Wood`, `Glass`, `Metals`, `Plastics`, `Paper`. In `Carbon cost`, food uses one `Food` row with separate AD and Compost columns; the other six strategies use Difference. Food reductions are read directly; other Difference values are negated. The landfill-life plot uses `Food waste` for the food category. Check these sign and aggregation conventions for your own inputs.

Abatement widths must be positive masses. Annual costs and the logged benefits/costs plot require values appropriate to a logarithmic scale. Units, mass definitions, price year and time bases must be supplied and verified by the user; they cannot be inferred from the column names alone.

### V8 fixed-cell layout

The separate V8 script requires `Net benefits` rows 2–9 in strategy order AD, Composting, Mulch, Wood, Glass, Metals, Plastics, Paper. Columns A, C, D, E and G supply names, revenue, monetized GHG contribution, cost and the mulch mass respectively. `Carbon cost!D3/E3` supply food GHG reductions; `F4/F8/F7/F6/F5/F2` supply the remaining differences. `MFA!C8/C11/C14/C25/C19/C22/C28` supply the AD, composting, wood, glass, metals, plastics and paper mass values. The V8 script sets the mulch monetized GHG contribution to zero in its financial calculations. Adapt and validate the script before using a workbook with another layout.

## Sankey workbook

Filename: `Sankey Plotly/data_V5.xlsx`; inputs are read from the first worksheet.

Required headers are `Labels`, `Lable No.` (historical spelling), `Color`, `X_Nodes`, `Source No.`, `Target No.` and `Values`. Node IDs must be unique integers, links must refer to existing IDs, and flows must be finite and nonnegative. Colors must be valid Plotly color strings. The `PAPER_COLUMNS` mapping in the script specifies the expected node labels and diagram columns; adapt this mapping when using other labels. Input X_Nodes is retained by the reader, but layout positions are calculated from PAPER_COLUMNS.

No input example containing private or derived study values is provided.
