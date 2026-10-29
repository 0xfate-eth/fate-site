#!/usr/bin/env python3
"""Build the public bilingual site in place."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(root/'site-build.py'),'--output',str(root),'--publish'],check=True)
