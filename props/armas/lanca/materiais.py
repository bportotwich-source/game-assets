"""Classes de material da lança improvisada (somadas às da M4A1 e às dos bastões)."""
import os, math, importlib.util
import texturas
from texturas import _n, _math, _smooth

_spec = importlib.util.spec_from_file_location('materiais_bastao_l', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bastao', 'materiais.py'))
bastao = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bastao)

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'cabo_pintado':     ((0.050, 0.120, 0.190), 0.48, 0.0, (0.400, 0.280, 0.150), 0.65, 0.0, 0.90, 0.40, 1.6),    # tinta azul gasta: a madeira aparece nas quinas
    'plastico_cinza': ((0.230, 0.240, 0.250), 0.50, 0.0, (0.320, 0.330, 0.340), 0.55, 0.0, 0.40, 0.40, 1.2),
    'fita_prata':     ((0.360, 0.370, 0.380), 0.38, 0.35, (0.420, 0.430, 0.440), 0.45, 0.2, 0.20, 0.50, 1.0),
    'pano_vermelho':  ((0.260, 0.050, 0.040), 0.92, 0.0, (0.330, 0.110, 0.090), 0.92, 0.0, 0.0, 1.00, 1.4),
    'barbante':       ((0.380, 0.300, 0.180), 0.90, 0.0, (0.380, 0.300, 0.180), 0.90, 0.0, 0.0, 1.00, 0.6),
    'aco_cozinha':    ((0.460, 0.465, 0.470), 0.34, 0.55, (0.560, 0.560, 0.560), 0.30, 0.6, 0.0, 0.35, 0.9),    # inox de cozinha (lâmina fina: sem desgaste de quina)
})


def _voltas(passo, altura):
    def relevo(nt, pos, geo):
        """Faixa enrolada no cabo: cada volta sobe um degrau sobre a anterior."""
        n = _n(nt, 'ShaderNodeSeparateXYZ')
        nt.links.new(geo.outputs['True Normal'], n.inputs[0])
        p = _n(nt, 'ShaderNodeSeparateXYZ')
        nt.links.new(pos, p.inputs[0])
        ang = _math(nt, 'DIVIDE', _math(nt, 'ARCTAN2', n.outputs['Z'], n.outputs['X']), 2 * math.pi)
        s = _math(nt, 'FRACT', _math(nt, 'ADD', _math(nt, 'DIVIDE', p.outputs['Y'], passo), ang))
        h = _math(nt, 'MULTIPLY', s, altura)
        topo = _smooth(nt, s, 0.86, 0.98)
        fundo = _math(nt, 'SUBTRACT', 1.0, _smooth(nt, s, 0.0, 0.08))
        return h, topo, fundo
    return relevo


texturas.RELEVO['fita_prata'] = _voltas(0.0165, 0.0005)
texturas.RELEVO['pano_vermelho'] = _voltas(0.0115, 0.0012)
