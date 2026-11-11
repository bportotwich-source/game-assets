"""O que a fábrica (../m4a1/fabrica.py) precisa saber da besta recurva."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]


def montar():
    import materiais, modelo
    modelo.montar()


ACESSORIOS = {}
CFG = dict(
    nome='besta', montar=montar, gerador='besta/jogo.py', tris_leve=6000,
    origem=(-40, -60, 0),            # a mesma origem da besta antiga
    esqueleto=json.load(open(os.path.join(AQUI, 'esqueleto.json'), encoding='utf-8')),
    # peças de cada nó (None = direto na raiz)
    nos={None: ['corpo', 'punho', 'trilho_voo'],
         **{k: [k] for k in ('braco_dir', 'braco_esq', 'corda_dir', 'corda_esq', 'trava_corda', 'gatilho', 'seguranca', 'virote')}},
    variantes={
        '': ('besta_recurva',
             'Besta de 165 lb com braços recurvos de fibra e coronha esqueletada: atira forte e quase sem barulho, e pode ficar armada '
             'esperando (sem cansar o braço). Armar é lento: pé no estribo e puxar com as duas mãos. Mantenha os dedos embaixo das abas '
             'do guarda-mão. Modelo detalhado, com texturas assadas (polímero verde-oliva, alumínio, corda torcida, gravações).'),
    })
