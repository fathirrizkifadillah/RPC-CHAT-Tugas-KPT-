"""Distributed Chat Room Package using gRPC.

Mata Kuliah Komputasi Paralel dan Terdistribusi.
"""

import sys
from pathlib import Path

# Ensure package directory is in sys.path for grpc generated stub imports
_pkg_dir = str(Path(__file__).parent.resolve())
if _pkg_dir not in sys.path:
    sys.path.insert(0, _pkg_dir)

__version__ = "1.0.0"
