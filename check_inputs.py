"""Check that user-supplied local workbooks are available; no data are distributed."""
from pathlib import Path
import os, sys
root=Path(__file__).resolve().parent
data=Path(os.environ.get('SWACO_INPUT_DIR',root/'private_inputs')).expanduser().resolve()
required=[data/'Analysis'/'costs analysis.xlsb.xlsx',data/'Sankey Plotly'/'data_V5.xlsx']
missing=[p for p in required if not p.is_file()]
if missing:
    print('This code-only package does not include study data. Supply compatible local inputs:')
    for p in missing: print(' - '+str(p))
    print('See INPUT_SCHEMA.md or set SWACO_INPUT_DIR to your local input directory.')
    sys.exit(1)
print('Required local files exist. This check does not validate their contents or formulas.')
