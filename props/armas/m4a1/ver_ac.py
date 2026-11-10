"""Renders de conferência das montagens com acessórios (sem textura)."""
import sys, time, bpy
sys.path.insert(0, '.')
import ver
ver.cena_limpa()
import modelo, acessorios
from lib import PARTES
t = time.time()
modelo.montar(); n0 = len(PARTES)
acessorios.montar()
for o in PARTES[n0:]:
    print(f"{o.name:26s} {sum(len(p.vertices) - 2 for p in o.data.polygons):6d}")
print('tris acessorios', sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in PARTES[n0:]), time.time() - t)
cores = {'anod': (0.05, 0.052, 0.055), 'anod_tubo': (0.06, 0.06, 0.06), 'fosf': (0.09, 0.09, 0.085), 'fosf_escuro': (0.12, 0.12, 0.12),
         'polim': (0.03, 0.03, 0.03), 'polim_grip': (0.05, 0.03, 0.03), 'magal': (0.1, 0.1, 0.1), 'serr': (0.12, 0.1, 0.08),
         'inox': (0.5, 0.5, 0.5), 'latao': (0.8, 0.6, 0.2), 'cobre': (0.7, 0.35, 0.2), 'tinta': (0.8, 0.8, 0.8), 'polim_claro': (0.2, 0.2, 0.15),
         'tan': (0.22, 0.17, 0.11), 'vermelho': (0.25, 0.02, 0.02), 'lente': (0.02, 0.05, 0.12), 'lente_clara': (0.3, 0.3, 0.3),
         'borracha': (0.02, 0.02, 0.02), 'rotulo': (0.3, 0.25, 0.05)}
for m in bpy.data.materials:
    b = m.node_tree.nodes.get('Principled BSDF')
    if b and m.name in cores:
        c = cores[m.name]; k = 3.0
        b.inputs['Base Color'].default_value = (min(1, c[0] * k), min(1, c[1] * k), min(1, c[2] * k), 1)
        b.inputs['Roughness'].default_value = 0.55
CLASSICO = {'gm': ['guarda_mao_superior', 'guarda_mao_inferior', 'anel_delta', 'tampa_guarda_mao', 'base_massa', 'pino_base_massa_1',
                   'pino_base_massa_2', 'pino_massa', 'zarelho_frontal'],
            'boca': ['quebra_chamas', 'arruela_boca'],
            'mira': ['alca_transporte', 'alca_mira', 'botao_deriva', 'tambor_elevacao', 'porca_alca_1', 'porca_alca_2'],
            'carr': ['carregador', 'transportador', 'cartucho_1', 'cartucho_2'],
            'cor': ['coronha', 'trava_coronha', 'zarelho_traseiro'], 'tubo': ['tubo_coronha'], 'punho': ['punho'],
            'alav': ['alavanca_manejo', 'trava_alavanca']}
BASE_OUT = [n for v in CLASSICO.values() for n in v]
AC = [o.name for o in PARTES[n0:]]
M1 = ['guarda_mao_longo', 'porca_cano', 'bloco_gas', 'trilho_baixo', 'supressor', 'empunhadura_angulada', 'luneta', 'suporte_luneta',
      'carregador_polimero', 'coronha_fixa', 'tubo_coronha', 'punho', 'alavanca_manejo', 'trava_alavanca']
M2 = ['guarda_mao_longo', 'porca_cano', 'bloco_gas', 'trilho_baixo', 'trilho_esquerdo', 'supressor', 'empunhadura_vertical', 'lanterna',
      'mira_prismatica', 'tampa_lente_frente', 'tampa_lente_tras', 'suporte_prismatica', 'mira_reflex', 'suporte_45', 'modulo_laser',
      'punho_vazado', 'carregador_tambor', 'tubo_coronha_vermelho', 'alavanca_ambi', 'coronha_moderna', 'trava_coronha_moderna']
out = sys.argv[1]
quais = sys.argv[2:] or ['m1', 'm2']
for nome, on in (('m1', M1), ('m2', M2)):
    if nome not in quais:
        continue
    for o in PARTES:
        o.hide_render = (o.name in BASE_OUT or o.name in AC) and o.name not in on
    c = (0, 0.03, -0.02)
    ver.render(f'{out}_{nome}_esq.png', (-2, 0.03, -0.02), c, ortho=1.08, res=(1800, 760))
    ver.render(f'{out}_{nome}_dir.png', (2, 0.03, -0.02), c, ortho=1.08, res=(1800, 760))
    ver.render(f'{out}_{nome}_34.png', (-1.2, 1.5, 0.8), (0, 0.05, -0.02), ortho=0.9, res=(1800, 900))
    ver.render(f'{out}_{nome}_34t.png', (1.1, -1.4, 0.8), (0, 0.0, -0.02), ortho=0.9, res=(1800, 900))
bpy.ops.wm.save_as_mainfile(filepath='/tmp/m4_ac.blend')
