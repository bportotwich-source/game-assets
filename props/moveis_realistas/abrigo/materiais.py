"""Classes de material da máquina de lanches, do colchão no chão, do quadro de procurados e dos riscos de contagem de dias
(somadas às de atendimento)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_atendimento', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'atendimento', 'materiais.py'))
atendimento = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(atendimento)
forja = atendimento.forja
quarto = atendimento.quarto

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'azul_vending':   ((0.020, 0.090, 0.300), 0.40, 0.0, (0.300, 0.300, 0.320), 0.60, 0.6, 0.70, 0.30, 1.8),   # chapa pintada de máquina de venda
    'salgadinho_1':   ((0.550, 0.060, 0.030), 0.30, 0.0, (0.550, 0.300, 0.200), 0.40, 0.0, 0.20, 0.20, 0.8),   # pacotes metalizados
    'salgadinho_2':   ((0.600, 0.420, 0.020), 0.30, 0.0, (0.550, 0.450, 0.200), 0.40, 0.0, 0.20, 0.20, 0.8),
    'salgadinho_3':   ((0.040, 0.250, 0.080), 0.30, 0.0, (0.300, 0.400, 0.300), 0.40, 0.0, 0.20, 0.20, 0.8),
    'chocolate_emb':  ((0.150, 0.060, 0.030), 0.35, 0.0, (0.350, 0.250, 0.200), 0.45, 0.0, 0.20, 0.20, 0.8),
    'cartaz_velho':   ((0.640, 0.580, 0.440), 0.88, 0.0, (0.520, 0.460, 0.340), 0.88, 0.0, 0.30, 0.60, 2.0),   # papel de cartaz amarelado
    'tinta_cartaz':   ((0.050, 0.040, 0.035), 0.70, 0.0, None, 0, 0, 0, 0, 0),
    'vermelho_cartaz': ((0.450, 0.040, 0.030), 0.70, 0.0, None, 0, 0, 0, 0, 0),
    'risco_carvao':   ((0.012, 0.011, 0.010), 0.95, 0.0, (0.035, 0.032, 0.030), 0.95, 0.0, 0.15, 1.50, 0.3),   # carvão riscado na parede
    'vela':           ((0.700, 0.660, 0.560), 0.50, 0.0, (0.600, 0.560, 0.480), 0.55, 0.0, 0.10, 0.30, 1.2),
})
for k, v in (('colchao_chao', (0.360, 0.320, 0.250)), ('cobertor_cinza', (0.140, 0.150, 0.150))):
    texturas.CLASSES[k] = quarto._pano_cls(v)
    forja.VELHO[k] = forja.VELHO['pano_cru']
