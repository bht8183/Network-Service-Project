# tests/conftest.py
import sys, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(root))   # guarantees 'dns_server' is importable