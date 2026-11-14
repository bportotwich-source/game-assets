"""Classes de material do mural de desaparecidos, do suporte de soro, do banco de praça e do balcão de recepção
(somadas às de publico)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_publico', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'publico', 'materiais.py'))
publico = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(publico)
forja = publico.forja
quarto = publico.quarto
madeira = forja.madeira

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'cortica':       ((0.420, 0.270, 0.140), 0.92, 0.0, (0.300, 0.200, 0.110), 0.92, 0.0, 0.20, 2.20, 1.4),   # cortiça de mural, furadinha
    'foto_azul':     ((0.180, 0.300, 0.450), 0.30, 0.0, (0.500, 0.500, 0.480), 0.50, 0.0, 0.30, 0.30, 1.2),   # fundos das fotos 3x4
    'foto_verde':    ((0.250, 0.360, 0.220), 0.30, 0.0, (0.500, 0.500, 0.480), 0.50, 0.0, 0.30, 0.30, 1.2),
    'foto_bege':     ((0.600, 0.520, 0.400), 0.30, 0.0, (0.500, 0.500, 0.480), 0.50, 0.0, 0.30, 0.30, 1.2),
    'foto_cabelo':   ((0.060, 0.040, 0.030), 0.35, 0.0, (0.200, 0.180, 0.160), 0.50, 0.0, 0.20, 0.30, 1.0),
    'foto_loiro':    ((0.520, 0.380, 0.180), 0.35, 0.0, (0.400, 0.350, 0.300), 0.50, 0.0, 0.20, 0.30, 1.0),
    'foto_roupa':    ((0.400, 0.060, 0.060), 0.35, 0.0, (0.400, 0.350, 0.330), 0.50, 0.0, 0.20, 0.30, 1.0),
    'recado':        ((0.700, 0.600, 0.200), 0.85, 0.0, (0.600, 0.550, 0.350), 0.85, 0.0, 0.30, 0.60, 1.6),   # papel amarelo de recado
    'caneta_azul':   ((0.030, 0.050, 0.200), 0.50, 0.0, None, 0, 0, 0, 0, 0),
    'pino_vermelho': ((0.500, 0.030, 0.030), 0.30, 0.0, (0.500, 0.200, 0.200), 0.40, 0.0, 0.20, 0.20, 0.8),
    'pino_azul':     ((0.040, 0.120, 0.450), 0.30, 0.0, (0.300, 0.300, 0.450), 0.40, 0.0, 0.20, 0.20, 0.8),
    'ferro_banco':   ((0.030, 0.065, 0.040), 0.50, 0.0, (0.200, 0.100, 0.050), 0.80, 0.3, 1.00, 0.50, 2.0),   # ferro fundido pintado de verde, descascando
    'praca_x':       ((0.230, 0.160, 0.100), 0.82, 0.0, (0.400, 0.360, 0.300), 0.85, 0.0, 0.80, 1.40, 2.6),   # ripa de madeira de rua, cinzenta do sol
    'bolsa_soro':    ((0.780, 0.800, 0.800), 0.25, 0.0, (0.700, 0.700, 0.680), 0.35, 0.0, 0.10, 0.20, 1.0),
    'tampo_balcao':  ((0.160, 0.150, 0.150), 0.30, 0.0, (0.300, 0.290, 0.280), 0.50, 0.0, 0.30, 0.80, 1.4),
    'laca_creme':    ((0.560, 0.500, 0.400), 0.45, 0.0, (0.400, 0.330, 0.250), 0.70, 0.0, 0.60, 0.40, 1.8),   # painéis de balcão pintados
    'bege_monitor':  ((0.520, 0.480, 0.400), 0.45, 0.0, (0.400, 0.380, 0.330), 0.60, 0.0, 0.30, 0.30, 1.6),   # plástico de computador velho amarelado
    'jornal':        ((0.520, 0.500, 0.450), 0.88, 0.0, (0.450, 0.420, 0.360), 0.88, 0.0, 0.20, 0.60, 2.0),
})
madeira.COR['praca_x'] = madeira.cor_madeira('praca_x')
texturas.RELEVO['praca_x'] = madeira.relevo_madeira('praca_x')
