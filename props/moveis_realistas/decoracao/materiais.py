"""Classes de material da decoração (somadas às do banheiro, da cozinha, da sala e do quarto)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_banheiro', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'banheiro', 'materiais.py'))
banheiro = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(banheiro)
cozinha = banheiro.cozinha
forja = banheiro.forja
from texturas import _n, _math, _mix, _mixf, _smooth, _noise

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'foto_papel':   ((0.520, 0.440, 0.310), 0.35, 0.0, (0.520, 0.440, 0.310), 0.35, 0.0, 0.0, 0.30, 1.2),   # fundo da foto desbotada
    'foto_sombra':  ((0.110, 0.080, 0.055), 0.35, 0.0, (0.110, 0.080, 0.055), 0.35, 0.0, 0.0, 0.30, 1.2),   # roupas escuras
    'foto_meio':    ((0.270, 0.210, 0.140), 0.35, 0.0, (0.270, 0.210, 0.140), 0.35, 0.0, 0.0, 0.30, 1.2),   # roupas claras
    'foto_pele':    ((0.420, 0.330, 0.220), 0.35, 0.0, (0.420, 0.330, 0.220), 0.35, 0.0, 0.0, 0.30, 1.2),
    'passepartout': ((0.560, 0.540, 0.470), 0.90, 0.0, (0.560, 0.540, 0.470), 0.90, 0.0, 0.0, 0.50, 1.6),
    'terracota':    ((0.420, 0.170, 0.085), 0.88, 0.0, (0.560, 0.470, 0.400), 0.92, 0.0, 0.50, 1.60, 1.8),   # barro cozido, salitre branco
    'terra_seca':   ((0.085, 0.060, 0.042), 0.97, 0.0, (0.180, 0.140, 0.100), 0.97, 0.0, 0.50, 2.60, 1.2),
    'galho_seco':   ((0.130, 0.090, 0.060), 0.90, 0.0, (0.260, 0.200, 0.140), 0.90, 0.0, 0.50, 1.80, 1.2),
    'folha_seca':   ((0.260, 0.150, 0.055), 0.80, 0.0, (0.380, 0.280, 0.120), 0.85, 0.0, 0.60, 1.20, 1.2),
    'ceramica_azul': ((0.030, 0.110, 0.130), 0.10, 0.0, (0.350, 0.320, 0.260), 0.60, 0.0, 0.20, 0.20, 1.8),  # vidrado azul-petróleo
    'cupula':       ((0.600, 0.520, 0.380), 0.90, 0.0, (0.600, 0.520, 0.380), 0.90, 0.0, 0.0, 0.50, 1.8),    # linho cru amarelado
    'vidro_lampada': ((0.700, 0.700, 0.660), 0.25, 0.0, (0.700, 0.700, 0.660), 0.25, 0.0, 0.0, 0.10, 1.5),
})


def _foto(nt, pos, S, nome):
    """Foto velha: manchas de umidade e desbotado irregular."""
    m = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 9.0, 4.0, 0.6), 0.45, 0.80), 0.45)
    S['cor'] = _mix(nt, m, S['cor'], (0.600, 0.520, 0.380))
    m2 = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 30.0, 3.0, 0.6), 0.62, 0.72), 0.5)
    S['cor'] = _mix(nt, m2, S['cor'], (0.200, 0.150, 0.090))


def _terracota(nt, pos, S, nome):
    """Vaso de barro velho: salitre branco em manchas e limo escuro."""
    m = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 7.0, 4.0, 0.65), 0.50, 0.78), 0.55)
    S['cor'] = _mix(nt, m, S['cor'], (0.560, 0.500, 0.440))
    m2 = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 16.0, 3.0, 0.6), 0.60, 0.75), 0.5)
    S['cor'] = _mix(nt, m2, S['cor'], (0.120, 0.090, 0.060))


forja.VELHO.update(foto_papel=_foto, foto_sombra=_foto, foto_meio=_foto, foto_pele=_foto, ceramica_azul=banheiro._louca,
                   cupula=forja.VELHO['pano_cru'], terracota=_terracota, galho_seco=forja.VELHO['casca'])
