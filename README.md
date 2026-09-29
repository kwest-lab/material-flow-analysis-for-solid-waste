# SWACO waste diversion analysis scripts

Python plotting scripts associated with *Material Flow Analysis-Based Approaches for Valuing Waste Diversion* by Narmada Ponnamperuma, Sarah McKenzie, and Daniel B. Gingerich.

**This repository contains code only. The private SWACO workbooks, datasets, derived tables and figures are not distributed.** Users must supply their own compatible inputs. These scripts read saved Excel results and make plots; the Excel calculation model is not included, and Python does not recalculate its formulas. This repository therefore does not independently reproduce the study's numerical results.

## Installation

Use Python 3.12. In this folder:

```sh
python -m venv .venv
```

Activate on Windows PowerShell with `.venv\Scripts\Activate.ps1`, or on macOS/Linux with `source .venv/bin/activate`, then run:

```sh
python -m pip install -r requirements.txt
```

## Supply local inputs

See [INPUT_SCHEMA.md](INPUT_SCHEMA.md) for required names and columns. Put your own files in this local structure:

```text
private_inputs/
  Analysis/
    costs analysis.xlsb.xlsx
  Sankey Plotly/
    data_V5.xlsx
```

Alternatively, set `SWACO_INPUT_DIR` to a local directory containing those `Analysis` and `Sankey Plotly` subfolders. Neither folder is supplied in the public package. The input filenames are retained for compatibility; no data are embedded in the repository.

```sh
python check_inputs.py
python run_figures.py
```

Outputs go to `outputs/`, or to the directory set by `SWACO_OUTPUT_DIR`. Matplotlib plots are PNGs; Plotly plots are self-contained HTML. 

Optional Plotly PNG export requires `requirements-static.txt`, Kaleido and compatible Chrome. Set `SWACO_STATIC_PLOTS=1` before running. 

## Scripts

| Script | Function |
| --- | --- |
| `scripts/plot_sankey.py` | Material-flow Sankey diagram and local node-position CSV. |
| `scripts/plot_ghg.py` | GHG reductions by strategy. |
| `scripts/plot_benefits_costs.py` | Revenue, monetized GHG benefits and annual costs. |
| `scripts/plot_abatement_combined.py` | Two-panel abatement figure. |
| `scripts/plot_abatement_separate.py` | Separate abatement panels. |
| `scripts/plot_landfill_life.py` | Saved landfill-life contributions. |



## Validation and limitations

Both workflows were tested locally with the author's private data. No private data or generated results are included. Path handling was made independent of the working directory. Direct dependency versions are recorded in `requirements.txt`. Full Excel calculation, optional Plotly PNG export, and GIS/education-outreach figure reproduction were not validated. 


## Suggested manuscript wording

“The Python scripts used to generate the figures are available at [repository URL or DOI]. The underlying SWACO datasets are private and are not included in the repository.”

This statement describes the plotting code accurately; it should not be expanded to claim that the full calculation model is included.
