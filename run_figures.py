"""Run figure scripts from any working directory."""
from pathlib import Path
import argparse, subprocess, sys, os
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--workflow',choices=['current','v8'],default='current')
a=p.parse_args()
names=['plot_sankey.py','plot_ghg.py','plot_benefits_costs.py','plot_abatement_combined.py','plot_abatement_separate.py','plot_landfill_life.py'] if a.workflow=='current' else ['plot_v8_revision.py']
for name in names:
    print('Running '+name,flush=True)
    subprocess.run([sys.executable,str(ROOT/'scripts'/name)],check=True,cwd=ROOT)
print('Finished. See '+str(Path(os.environ.get('SWACO_OUTPUT_DIR', ROOT/'outputs'))))
