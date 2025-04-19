import importlib, pathlib, sys
print("cwd =", pathlib.Path().absolute())
try:
    mod = importlib.import_module("dns_server")
    print("dns_server imported from", mod.__file__)
except ImportError as e:
    print("IMPORT FAILED:", e)
    sys.exit(1)
