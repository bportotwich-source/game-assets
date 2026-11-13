"""Classes de material da comida embalada (somadas às da M4A1, às das estações e às das ferramentas)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_ferramentas', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ferramentas', 'materiais.py'))
ferramentas = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ferramentas)
forja = ferramentas.forja


def _estampa(cor, rug=0.55, gasto=0.30, sujeira=1.2):
    """Tinta de embalagem: gasta nas quinas até o papel claro."""
    return (cor, rug, 0.0, (0.600, 0.560, 0.480), 0.75, 0.0, gasto, 0.30, sujeira)


# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'rot_vermelho': _estampa((0.430, 0.030, 0.022)),
    'rot_marrom':   _estampa((0.210, 0.075, 0.030)),
    'rot_creme':    _estampa((0.640, 0.540, 0.360)),
    'rot_verde':    _estampa((0.050, 0.240, 0.060)),
    'rot_amarelo':  _estampa((0.720, 0.480, 0.030)),
    'rot_azul':     _estampa((0.030, 0.110, 0.380)),
    'rot_laranja':  _estampa((0.700, 0.230, 0.020)),
    'rot_branco':   _estampa((0.700, 0.700, 0.680)),
    'letra_amarela': ((0.800, 0.600, 0.050), 0.55, 0.0, (0.800, 0.600, 0.050), 0.55, 0.0, 0.0, 0.30, 0.8),
    'letra_azul':    ((0.030, 0.100, 0.380), 0.55, 0.0, (0.030, 0.100, 0.380), 0.55, 0.0, 0.0, 0.30, 0.8),
    'letra_vermelha': ((0.450, 0.030, 0.022), 0.55, 0.0, (0.450, 0.030, 0.022), 0.55, 0.0, 0.0, 0.30, 0.8),
    # sacos plásticos: lisos, com brilho, sem desgaste de quina
    'saco_branco':  ((0.720, 0.720, 0.700), 0.32, 0.0, (0.720, 0.720, 0.700), 0.32, 0.0, 0.0, 0.15, 0.9),
    'saco_azul':    ((0.030, 0.110, 0.400), 0.30, 0.0, (0.030, 0.110, 0.400), 0.30, 0.0, 0.0, 0.15, 0.9),
    'saco_laranja': ((0.720, 0.250, 0.020), 0.26, 0.0, (0.720, 0.250, 0.020), 0.26, 0.0, 0.0, 0.15, 0.9),
    'saco_vermelho': ((0.450, 0.030, 0.022), 0.26, 0.0, (0.450, 0.030, 0.022), 0.26, 0.0, 0.0, 0.15, 0.9),
    'folha_aluminio': ((0.620, 0.620, 0.630), 0.30, 1.0, (0.620, 0.620, 0.630), 0.30, 1.0, 0.0, 0.50, 0.6),
    'chocolate':    ((0.085, 0.036, 0.016), 0.42, 0.0, (0.150, 0.075, 0.040), 0.50, 0.0, 0.35, 0.20, 0.5),
    'arroz':        ((0.760, 0.740, 0.660), 0.72, 0.0, (0.760, 0.740, 0.660), 0.72, 0.0, 0.0, 1.60, 0.3),
    'flocos':       ((0.700, 0.420, 0.080), 0.70, 0.0, (0.700, 0.420, 0.080), 0.70, 0.0, 0.0, 1.20, 0.4),
    # comida fresca
    'saco_papel':   ((0.640, 0.590, 0.480), 0.85, 0.0, (0.700, 0.660, 0.560), 0.85, 0.0, 0.15, 0.60, 1.1),
    'papel_pardo':  ((0.400, 0.280, 0.150), 0.85, 0.0, (0.520, 0.400, 0.250), 0.85, 0.0, 0.25, 0.60, 1.1),
    'papel_acougue': ((0.660, 0.580, 0.520), 0.60, 0.0, (0.660, 0.580, 0.520), 0.60, 0.0, 0.0, 0.40, 1.0),
    'pao_crosta':   ((0.300, 0.120, 0.030), 0.60, 0.0, (0.560, 0.330, 0.110), 0.70, 0.0, 0.35, 1.20, 0.4),
    'pao_miolo':    ((0.600, 0.400, 0.170), 0.80, 0.0, (0.600, 0.400, 0.170), 0.80, 0.0, 0.0, 1.20, 0.3),
    'carne':        ((0.270, 0.018, 0.022), 0.32, 0.0, (0.420, 0.060, 0.055), 0.30, 0.0, 0.10, 0.90, 0.3),
    'gordura':      ((0.700, 0.610, 0.480), 0.36, 0.0, (0.700, 0.610, 0.480), 0.36, 0.0, 0.0, 0.50, 0.3),
    'defumada':     ((0.085, 0.030, 0.015), 0.46, 0.0, (0.250, 0.085, 0.030), 0.55, 0.0, 0.40, 1.20, 0.6),
    'carne_cozida': ((0.400, 0.170, 0.130), 0.55, 0.0, (0.400, 0.170, 0.130), 0.55, 0.0, 0.0, 0.90, 0.3),
    'alface':       ((0.130, 0.330, 0.045), 0.50, 0.0, (0.130, 0.330, 0.045), 0.50, 0.0, 0.0, 0.50, 0.4),
    'alface_claro': ((0.400, 0.520, 0.130), 0.50, 0.0, (0.400, 0.520, 0.130), 0.50, 0.0, 0.0, 0.50, 0.3),
    'tomate':       ((0.500, 0.030, 0.018), 0.22, 0.0, (0.500, 0.030, 0.018), 0.22, 0.0, 0.0, 0.10, 0.3),
    'cenoura':      ((0.720, 0.230, 0.018), 0.55, 0.0, (0.720, 0.230, 0.018), 0.55, 0.0, 0.0, 0.70, 0.5),
    'peixe':        ((0.400, 0.420, 0.430), 0.28, 0.35, (0.560, 0.570, 0.560), 0.24, 0.5, 0.30, 0.60, 0.3),
    'peixe_dorso':  ((0.090, 0.120, 0.130), 0.30, 0.20, (0.200, 0.240, 0.250), 0.28, 0.3, 0.30, 0.60, 0.3),
    'peixe_barriga': ((0.660, 0.640, 0.580), 0.30, 0.10, (0.660, 0.640, 0.580), 0.30, 0.1, 0.0, 0.50, 0.3),
    'peixe_nadadeira': ((0.170, 0.170, 0.160), 0.50, 0.0, (0.300, 0.290, 0.260), 0.50, 0.0, 0.30, 0.90, 0.4),
    'peixe_olho':   ((0.700, 0.620, 0.250), 0.15, 0.0, (0.700, 0.620, 0.250), 0.15, 0.0, 0.0, 0.10, 0.2),
    'peixe_tostado': ((0.360, 0.180, 0.055), 0.50, 0.0, (0.600, 0.400, 0.150), 0.60, 0.0, 0.40, 1.20, 0.5),
    'assada':       ((0.150, 0.060, 0.030), 0.48, 0.0, (0.330, 0.150, 0.065), 0.55, 0.0, 0.40, 1.20, 0.5),
    'gordura_tostada': ((0.560, 0.360, 0.130), 0.40, 0.0, (0.560, 0.360, 0.130), 0.40, 0.0, 0.0, 0.80, 0.4),
    'osso':         ((0.700, 0.660, 0.560), 0.55, 0.0, (0.700, 0.660, 0.560), 0.55, 0.0, 0.0, 0.60, 0.7),
    'talo':         ((0.060, 0.210, 0.035), 0.55, 0.0, (0.060, 0.210, 0.035), 0.55, 0.0, 0.0, 0.50, 0.4),
})


def _manchas(escala, amp, detalhe=4.0):
    """Relevo de manchas (ruído): altura em m; o alto clareia para a cor gasta, o fundo escurece."""
    def f(nt, pos, geo):
        n = texturas._n(nt, 'ShaderNodeTexNoise')
        n.inputs['Scale'].default_value = escala
        n.inputs['Detail'].default_value = detalhe
        nt.links.new(pos, n.inputs['Vector'])
        v = n.outputs[0]
        h = texturas._math(nt, 'MULTIPLY', texturas._math(nt, 'SUBTRACT', v, 0.5), amp)
        topo = texturas._smooth(nt, v, 0.50, 0.72)
        fundo = texturas._math(nt, 'SUBTRACT', 1.0, texturas._smooth(nt, v, 0.30, 0.50))
        return h, topo, fundo
    return f


texturas.RELEVO['pao_crosta'] = _manchas(55.0, 0.0016)
texturas.RELEVO['carne'] = _manchas(140.0, 0.0006)
texturas.RELEVO['defumada'] = _manchas(60.0, 0.0018)
texturas.RELEVO['peixe'] = _manchas(420.0, 0.0004)
texturas.RELEVO['peixe_dorso'] = _manchas(420.0, 0.0004)
texturas.RELEVO['peixe_tostado'] = _manchas(90.0, 0.0012)
texturas.RELEVO['assada'] = _manchas(70.0, 0.0014)
