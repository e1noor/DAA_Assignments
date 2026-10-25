"""Local runner, NOT the unavailable instructor's 36-case public checker."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--setup', action='store_true')
parser.add_argument('--check', action='store_true')
args = parser.parse_args()
if args.setup:
    if sys.version_info < (3, 12):
        raise SystemExit('Python 3.12+ required')
    print('Local setup OK: standard library only; no compilation or installs.')
if args.check:
    subprocess.run([sys.executable, str(ROOT / 'tests/check.py')], check=True)
if not (args.setup or args.check):
    subprocess.run([sys.executable, str(ROOT / 'src/main.py')], check=True)
