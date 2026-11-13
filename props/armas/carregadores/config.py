"""O que a fábrica (../m4a1/fabrica.py) precisa saber dos carregadores avulsos: uma entrada por id do
catálogo. A origem é o nó "carregador" da arma (onde fica o encaixe_carregador), nas coordenadas
do modelo da arma: M4A1 para os 5,56 (o Vigília é a M4A1 levada 145 mm à frente), M4A1 x1,1 para
os .308 de precisão (Atalaia), e o modelo.py de cada arma para os outros."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
ARMAS = os.path.dirname(AQUI)
sys.path[:0] = [AQUI, os.path.join(ARMAS, 'm4a1')]


def _montar(f, *a):
    def g():
        import texturas, montagem
        getattr(montagem, f)(*a)
    return g


M4 = (-40, -16, 0)
AR10 = (-44, -17.6, 0)
BRASA = (92, -24, 0)
_FIM = ' Modelo detalhado, com texturas assadas.'
#      id: (função de montagem.py, argumentos, origem, descrição)
_T = {
    'carregador_556_30': ('c556_30', (), M4, 'Carregador curvo de polímero de 30, com painéis de pega e base larga.'),
    'carregador_556_30_tan': ('c556_30_tan', (), M4, 'Carregador curvo de polímero caramelo de 30, com painéis de pega e base larga.'),
    'carregador_556_60': ('c556_60', (), M4, 'Carregador longo de alumínio de quatro fileiras: 60 tiros num pente só, com janelas de contagem. '
                                              'Mais leve que o tambor, mas bate no chão quando deitado.'),
    'tambor_556_60': ('tambor_556_60', (), M4, 'Tambor de 60 com o eixo ao longo do cano e tampa nervurada na frente: o dobro de tiros, mas '
                                                'pesado e lento para trocar.'),
    'tambor_556_60_tatico': ('tambor_556_60_tatico', (), M4, 'Tambor de 60 com janela na tampa para ver quantos sobram, abas de pega e '
                                                              'alavanca para carregar sem dar corda.'),
    'carregador_ar10_20': ('ar10_20', (), AR10, 'Carregador de polímero de 20 tiros .308 com janelinhas de contagem atrás. Não serve na carabina de ferrolho.'),
    'carregador_ar10_10': ('ar10_10', (), AR10, 'Carregador curto de 10: o fuzil fica mais baixo para atirar deitado.'),
    'carregador_762_30': ('c762_30', (), BRASA, 'Carregador curvo de aço de 30, com nervuras estampadas e um cartucho à vista.'),
    'carregador_762_30_grade': ('c762_30_grade', (), BRASA, 'Carregador preto de polímero com quadros em relevo dos lados: mais leve que o de aço.'),
    'carregador_762_30_grade_gasto': ('c762_30_grade_gasto', (), BRASA, 'Carregador preto de polímero com quadros em relevo dos lados: mais '
                                                                         'leve que o de aço. Peça usada, com a pintura gasta.'),
    'carregador_762_40': ('c762_40', (), BRASA, 'Carregador longo de polímero preto, 40 tiros, com quadros em relevo dos lados.'),
    'tambor_762_75': ('tambor_762_75', (), BRASA, 'Tambor de 75 com chave de corda na frente e janela de contagem: muito tiro, muito peso.'),
    'carregador_308_10': ('c308', (10,), (45, -16, 0), 'Carregador de caixa de polímero de 10 tiros, lábios de aço e canaletas de pega.'),
    'carregador_308_5': ('c308', (5,), (45, -16, 0), 'Carregador curto de 5 tiros (quase rente à coronha).'),
    'carregador_smg_20': ('smg', (20, 112.0), (31, -26, 0), 'Curto: fica rente ao fundo do punho, a arma cabe em qualquer bolso de mochila.'),
    'carregador_smg_30': ('smg', (30, 142.0), (31, -26, 0), 'Carregador padrão de 30. Vem na arma.'),
    'carregador_smg_40': ('smg', (40, 178.0), (31, -26, 0), 'Comprido: 40 tiros, mas atrapalha deitar no chão.'),
    'carregador_ciclone_17': ('ciclone', (17, 102.0), (124, -20, 0), 'Carregador curto de pistola: some dentro do poço, a arma fica baixa.'),
    'carregador_ciclone_30': ('ciclone', (30, 162.0), (124, -20, 0), 'Carregador longo de 30. Vem na arma.'),
    'tambor_ciclone_50': ('tambor_ciclone_50', (), (124, -20, 0), 'Tambor de 50 tiros com botão de corda do lado e janelinha de contagem. '
                                                                  'Pesa e demora para trocar, mas segura uma horda.'),
    'carregador_22_10': ('c22_10', (), (26, -12, 0), 'Carregador rotativo curto, quase rente à coronha.'),
    'carregador_22_25': ('c22_25', (), (26, -12, 0), 'Caixa comprida de 25 tiros com fenda de contagem. Atrapalha deitar o rifle no chão, mas '
                                                       'dá para limpar um quintal sem recarregar.'),
    'carregador_guardia_17': ('guardia', (17,), (20, -16, 0), 'Carregador de aço de 17 tiros com base cor de areia (vem na Guardiã).'),
    'carregador_guardia_20': ('guardia', (20,), (20, -16, 0), 'Carregador de 20 com luva de polímero que continua o cabo (sobra embaixo e '
                                                                'dá apoio ao dedinho).'),
    'carregador_9mm': ('sentinela', (15,), (21.5, -16, 0), 'Carregador padrão da pistola, 15 tiros.'),
    'carregador_9mm_estendido': ('sentinela', (24,), (21.5, -16, 0), 'Mais 9 tiros, mas sai pelo fundo do punho e deixa a recarga um pouco mais lenta.'),
    'carregador_rapido_38': ('rapido_38', (), (-1.2, 0, 0), 'Segura 6 cartuchos na posição das câmaras: encosta, gira o botão e os 6 entram de uma vez.'),
}


def _cfg(q):
    f, a, org, desc = _T[q]
    return dict(nome=q, montar=_montar(f, *a), gerador='carregadores/jogo.py', id=q, origem=org,
                esqueleto=json.load(open(os.path.join(AQUI, f'esqueleto_{q}.json'), encoding='utf-8')),
                nos={None: ['carregador']}, descricao=desc + _FIM)


ACESSORIOS = {q: _cfg(q) for q in _T}
