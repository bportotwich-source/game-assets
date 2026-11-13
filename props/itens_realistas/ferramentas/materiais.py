"""Classes de material das ferramentas e materiais de craft (somadas às da M4A1 e às das estações)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_municao', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'moveis_realistas', 'bancada_municao', 'materiais.py'))
municao = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(municao)
forja = municao.forja

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'prego':    ((0.330, 0.330, 0.340), 0.42, 1.0, (0.330, 0.330, 0.340), 0.42, 1.0, 0.0, 0.40, 0.8),     # miúdo: sem desgaste de quina
    'zinco':    ((0.360, 0.380, 0.390), 0.46, 1.0, (0.520, 0.540, 0.550), 0.36, 1.0, 0.5, 0.50, 1.6),     # chapa galvanizada que enferruja
    'etiqueta': ((0.640, 0.600, 0.480), 0.80, 0.0, (0.640, 0.600, 0.480), 0.80, 0.0, 0.0, 0.30, 0.4),
})


# madeiras que faltavam: travessa do punho da pá (veio em z) e talas escuras do facão
IMBUIA = ((0.120, 0.060, 0.028), 0.50, 0.0, (0.300, 0.180, 0.090), 0.58, 0.0, 0.70, 0.90, 1.4)
texturas.CLASSES.update({'faia_z': forja.madeira.FAIA, 'imbuia_x': IMBUIA})
forja.madeira.EIXO.setdefault('z', 'Y')
for _c in ('faia_z', 'imbuia_x'):
    forja.madeira.COR[_c] = forja.madeira.cor_madeira(_c)
    texturas.RELEVO[_c] = forja.madeira.relevo_madeira(_c)


def _zinco(nt, pos, S, nome):
    """Chapa galvanizada velha: ferrugem em manchas esticadas ao longo das ondas, zinco fosco no resto."""
    f = forja
    x, y, z = f._xyz(nt, pos)
    risco = f._noise(nt, f._vec(nt, x, y, z, 0.10, 1.0, 1.0), 14.0, 3.0, 0.6)       # x do Blender = comprimento da chapa
    mancha = f._noise(nt, pos, 7.0, 4.0, 0.62)
    fr = f._smooth(nt, f._math(nt, 'ADD', f._math(nt, 'MULTIPLY', mancha, 0.55), f._math(nt, 'MULTIPLY', risco, 0.45)), 0.47, 0.60)
    ferr = f._mix(nt, f._smooth(nt, f._noise(nt, pos, 90.0, 3.0, 0.6), 0.3, 0.7), (0.200, 0.075, 0.028), (0.085, 0.036, 0.018))
    S['cor'] = f._mix(nt, fr, S['cor'], ferr)
    S['rug'] = f._mixf(nt, fr, S['rug'], 0.90)
    S['met'] = f._mixf(nt, fr, S['met'], 0.15)


forja.VELHO['zinco'] = _zinco

texturas.CLASSES['pedra_lascada'] = ((0.090, 0.088, 0.085), 0.38, 0.0, (0.300, 0.290, 0.270), 0.55, 0.0, 0.45, 0.60, 0.8)   # sílex: escuro e liso, lascas claras nas arestas
