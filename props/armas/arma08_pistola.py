# Arma 1 (refeita): cores da armação da pistola Sentinela, supressores coloridos e ponte de mira presa na armação.
# Carregado por gerar_armas.py depois dos outros arquivos (mesmos globais). A pistola base fica em gerar_armas.py.

CORES_PISTOLA = {
    'tan': ('areia', {'polimero': 'polimero_tan', 'polimero_pontos': 'polimero_pontos_tan'}, 'cerakote_areia'),
    'verde': ('verde-oliva', {'polimero': 'polimero_verde', 'polimero_pontos': 'polimero_pontos_verde'}, 'cerakote_verde'),
    'cinza': ('cinza', {'polimero': 'polimero_cinza', 'polimero_pontos': 'polimero_pontos_cinza'}, 'cerakote_cinza'),
}


def _pistola_cor(mapa):
    def fn(A):
        pistola_9mm(A)
        _recolore(A.base, mapa)
        for pt in A.partes:
            if pt['no'] == 'cano': _recolore(pt['peca'], {'aco_cano': 'cano_dourado'})     # cano com acabamento dourado
    return fn


for _k, (_nome, _mapa, _cer) in CORES_PISTOLA.items():
    REG[f'pistola_9mm_{_k}'] = dict(REG['pistola_9mm'], id=f'pistola_9mm_{_k}', nome=f'Pistola Sentinela 9 mm ({_nome})', fn=_pistola_cor(_mapa),
                                     descricao=f'A mesma Sentinela com armação {_nome}, ferrolho preto e cano dourado. Aceita os mesmos acessórios.')
    REG[f'supressor_9mm_{_k}'] = dict(REG['supressor_9mm'], id=f'supressor_9mm_{_k}', nome=f'Supressor 9 mm ({_nome})',
                                       fn=(lambda c: (lambda A: supressor_9mm(A, c)))(_cer))


def _ponte(A, mat='aluminio_preto'):
    """Ponte de mira: duas placas laterais presas na armacao (por fora do ferrolho), subindo na frente da janela de ejecao,
    e uma travessa por cima do ferrolho com a mira de ponto vermelho. Nao anda com o ferrolho; a massa de mira passa pela fenda."""
    q = A.base; Z0, Z1 = 0.0128, 0.0153; YT0, YT1 = SL_Y1 + 0.002, SL_Y1 + 0.0087
    lado = arred([(0.072, -0.029), (0.166, -0.029), (0.17, -0.025), (0.17, YT1), (0.118, YT1), (0.113, YT1 - 0.004), (0.113, 0.004),
                  (0.093, -0.0155), (0.075, -0.0155), (0.072, -0.018)], 0.0015)
    bolso = arred([(0.124, -0.0085), (0.16, -0.0085), (0.16, 0.0125), (0.124, 0.0125)], 0.003)
    bolso2 = arred([(0.08, -0.0255), (0.11, -0.0255), (0.11, -0.019), (0.08, -0.019)], 0.0015)
    for zs in (-1, 1):
        za, zb = min(zs * Z0, zs * Z1), max(zs * Z0, zs * Z1)
        zc = (zb if zs > 0 else za)
        pl = solido(lado, za, zb, 0.0006)
        pl = menos(pl, solido(bolso, zc - 0.0012, zc + 0.0012), solido(bolso2, zc - 0.0009, zc + 0.0009))
        q.add(mat, pl)
        q.add(mat, solido(arred([(0.074, -0.029), (0.168, -0.029), (0.168, -0.016), (0.074, -0.016)], 0.001),
                          min(zs * 0.0111, zs * Z0), max(zs * 0.0111, zs * Z0)))            # garra que abraca a armacao
        for x in (0.082, 0.16):
            q.add('aco_oxidado', cil_z(0.0018, min(zs * Z1, zs * (Z1 + 0.0012)), max(zs * Z1, zs * (Z1 + 0.0012)), x, -0.0225, 6))   # parafusos
        q.add('aco_oxidado', cil_z(0.0015, min(zs * Z1, zs * (Z1 + 0.001)), max(zs * Z1, zs * (Z1 + 0.001)), 0.1645, YT1 - 0.0035, 6))
    topo = solido(arred([(0.113, YT0), (0.17, YT0), (0.17, YT1), (0.113, YT1)], 0.0012), -Z1, Z1, 0.001)
    q.add(mat, menos(topo, caixa(0.112, 0.172, YT0 - 0.001, SL_Y1 + 0.0068, -0.0024, 0.0024)))        # fenda da massa de mira
    _mini_ponto(q, 'aluminio_preto', 0.1415, YT1)
    A.encaixe('olho', (0.1415, YT1 + 0.0145, 0), 'mira', descricao='centro da lente: linha de visada')
    A.pivo = (0.14, -0.022, 0)


@_acessorio('ponte_mira_pistola', 'Ponte de mira com ponto vermelho', 'mira', 'ponte_pistola', peso_kg=0.09, raridade='muito raro', valor_troca=70,
            usa='pilhas', autonomia_min=3000, modificadores={'precisao_mirando': 1.3, 'tempo_mirar': 0.85}, onde=['quartel', 'delegacia'],
            linha_de_visada='encaixe "olho": centro da lente, a câmera mira por ali',
            descricao='Ponte de alumínio presa na armação que passa por cima do ferrolho, na frente da janela de ejeção, com uma mira de ponto '
                      'vermelho em cima. Como não anda com o ferrolho, o ponto fica parado no tiro. Põe-se sem ferramenta.')
def ponte_mira_pistola(A): _ponte(A)


@_acessorio('ponte_mira_pistola_tan', 'Ponte de mira com ponto vermelho (areia)', 'mira', 'ponte_pistola', peso_kg=0.09, raridade='muito raro',
            valor_troca=70, usa='pilhas', autonomia_min=3000, modificadores={'precisao_mirando': 1.3, 'tempo_mirar': 0.85}, onde=['quartel'],
            linha_de_visada='encaixe "olho": centro da lente, a câmera mira por ali',
            descricao='A mesma ponte de mira em alumínio cor de areia, para combinar com a armação areia.')
def ponte_mira_pistola_tan(A): _ponte(A, 'cerakote_areia')
