"""Classes de material da faca de combate (usa as da M4A1, do Brasa, dos arcos e da besta)."""
import os, importlib.util
import texturas

for _nome, _pasta in (('materiais_besta', 'besta'), ('materiais_brasa', 'brasa')):
    _spec = importlib.util.spec_from_file_location(_nome, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', _pasta, 'materiais.py'))
    _m = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_m)
