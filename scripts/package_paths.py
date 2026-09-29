"""Paths for user-supplied inputs and local outputs; no study data are distributed."""
from pathlib import Path
import os
ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get('SWACO_INPUT_DIR', ROOT / 'private_inputs')).expanduser().resolve()
OUTPUT = Path(os.environ.get('SWACO_OUTPUT_DIR', ROOT / 'outputs')).expanduser().resolve()
OUTPUT.mkdir(parents=True, exist_ok=True)
os.environ.setdefault('MPLBACKEND', 'Agg')
os.environ.setdefault('MPLCONFIGDIR', str(OUTPUT / '.mplconfig'))

def save_plotly(fig, path, **kwargs):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    html = path.with_suffix('.html')
    fig.write_html(str(html), include_plotlyjs=True, auto_open=False)
    print(f'Saved interactive figure: {html}')
    if os.environ.get('SWACO_STATIC_PLOTS') == '1':
        fig.write_image(str(path), **kwargs)
        print(f'Saved static figure: {path}')
