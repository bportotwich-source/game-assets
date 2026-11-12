"""Classes de material (as da M4A1 e as das estações já feitas; nada de novo aqui)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_bancada_municao', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bancada_municao', 'materiais.py'))
municao = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(municao)
forja = municao.forja
