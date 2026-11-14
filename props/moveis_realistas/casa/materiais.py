"""Classes de material da mesa de lanchonete, da vitrola, da máquina de lavar, da banheira, do tapete e da escrivaninha (somadas às dos sinais)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_sinais', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sinais', 'materiais.py'))
sinais = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sinais)
forja = sinais.forja
quarto = sinais.quarto

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'tela_som':       quarto._pano_cls((0.300, 0.230, 0.150)),          # tecido do alto-falante
    'disco':          ((0.012, 0.012, 0.014), 0.22, 0.0, (0.050, 0.050, 0.050), 0.45, 0.0, 0.30, 0.20, 1.0),
    'capa_disco_1':   ((0.550, 0.120, 0.060), 0.70, 0.0, (0.600, 0.450, 0.300), 0.80, 0.0, 0.50, 0.40, 1.3),
    'capa_disco_2':   ((0.060, 0.200, 0.330), 0.70, 0.0, (0.450, 0.450, 0.400), 0.80, 0.0, 0.50, 0.40, 1.3),
    'capa_disco_3':   ((0.700, 0.580, 0.200), 0.70, 0.0, (0.600, 0.500, 0.350), 0.80, 0.0, 0.50, 0.40, 1.3),
    'feltro':         ((0.250, 0.030, 0.030), 0.95, 0.0, (0.250, 0.030, 0.030), 0.95, 0.0, 0.0, 0.40, 1.5),
    'banheira_fora':  ((0.090, 0.180, 0.150), 0.45, 0.0, (0.300, 0.280, 0.240), 0.60, 0.0, 0.45, 0.35, 1.6),   # ferro fundido pintado
    'la_vinho':       quarto._pano_cls((0.230, 0.040, 0.040)),          # lã do tapete
    'la_creme':       quarto._pano_cls((0.520, 0.440, 0.300)),
    'la_azul':        quarto._pano_cls((0.050, 0.080, 0.160)),
    'franja':         quarto._pano_cls((0.600, 0.540, 0.420)),
    'esmalte_lavar':  ((0.780, 0.780, 0.760), 0.35, 0.0, (0.600, 0.550, 0.450), 0.55, 0.0, 0.40, 0.25, 1.6),
})
forja.VELHO.update(tela_som=forja.VELHO['pano_cru'], la_vinho=forja.VELHO['pano_cru'], la_creme=forja.VELHO['pano_cru'],
                   la_azul=forja.VELHO['pano_cru'], franja=forja.VELHO['pano_cru'])
