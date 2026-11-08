# Veiculo 3: picape Lida (picape de cabine simples, desenho próprio e sem marca).
# Frente, portas e cabine com desenho próprio (mais alta e quadrada); motor, rodas, tanque, escapamento, bancos e painel são os do sedã Rumo.
# Carregado por gerar_veiculos.py depois de veiculo01_sedan.py (usa as funções de lá; a forma vem de picape_forma.py).
import picape_forma as _PF

PECA.update({
    'tampa_cacamba': _peca('tampa_cacamba', 'Tampa da caçamba', 14, 'picape_lida', 'fecha a caçamba; aberta, vira rampa e aumenta a carga', carga_maos=True),
    'vidro_traseiro_cabine': _peca('vidro_traseiro_cabine', 'Vidro de trás da cabine', 4, 'picape_lida', 'protege a cabine por trás', carga_maos=True),
    'para_choque_traseiro_picape': _peca('para_choque_traseiro_picape', 'Para-choque traseiro da picape', 7, 'picape_lida', 'absorve a primeira parte das batidas de trás; tem o degrau', (7, 1)),
})
_frente_propria('_picape', 'picape_lida', 'da picape')


@modelo('picape_lida', 'Picape Lida', classe='picape', portas=2, lugares=2,
        descricao='Picape de cabine simples, desenho próprio e sem marca: frente quadrada e alta, faróis duplos, capô reto, para-brisa '
                  'mais em pé e alargadores nas rodas. O motor, as rodas, o tanque, o escapamento, os bancos e o volante são os mesmos do '
                  'sedã Rumo. A caçamba é aberta, leva 600 kg e a tampa cai para trás.',
        fisica=dict(massa_kg=1010, centro_massa_m=[0, 0.46, 0.25], tracao='dianteira', forca_motor_n=3300, freio=40, carga_kg=600,
                    direcao_graus=[32, 8], vel_max_kmh=135, roda_raio_m=_PF.R_RODA, roda_largura_m=0.185,
                    suspensao=dict(curso_m=0.17, rigidez=48, compressao=0.85, retorno=0.9), atrito_pneu=dict(asfalto=2.6, terra=1.9, grama=1.5, lama=1.0)),
        combustivel=dict(tanque_l=45, consumo_l_100km=8.5, marcha_lenta_l_h=0.8, bocal='tampa_combustivel'),
        bateria=dict(capacidade_ah=45), cor_padrao=_fator((236, 236, 230)),
        cores_sorteio=[_fator(c) for c in [(236, 236, 230), (150, 34, 28), (48, 74, 52), (40, 40, 44), (176, 150, 104), (54, 82, 128),
                                           (120, 120, 116), (200, 92, 30)]])
def picape_lida(Vc):
    global SF
    SF = _PF
    _partes_carroceria(Vc)
    X0 = SF.x_lado(0.50, 1.0) - 0.07
    Vc.parte('para_choque_d', (0, 0.315, SF.ZF), 'peca', item=PECA['para_choque_dianteiro_picape'], peca='para_choque_dianteiro_picape', **REG['para_choque'])
    Vc.parte('para_choque_t', (0, 0.315, SF.ZR), 'peca', item=PECA['para_choque_traseiro_picape'], peca='para_choque_traseiro_picape', **REG['para_choque'])
    for s, l in ((1, 'e'), (-1, 'd')):
        Vc.parte(f'farol_{l}', (s * 0.58, 0.61, 2.03), 'peca', item=PECA['farol_picape'], peca='farol_picape', **REG['farol'])
    for s, l in ((1, 'e'), (-1, 'd')):
        Vc.parte(f'lanterna_{l}', (s * 0.70, 0.79, SF.ZR + 0.06), 'peca', item=PECA['lanterna_vertical'], peca='lanterna_vertical', **REG['lanterna'])
    for s, l, pai in ((1, 'e', 'porta_de'), (-1, 'd', 'porta_dd')):
        Vc.parte(f'retrovisor_{l}', (s * X0, 0.955 + SF.DY_CINTURA, 0.50), 'peca', pai=pai, item=PECA['retrovisor'], peca='retrovisor', **REG['retrovisor'])
    for no, s, zc in (('roda_de', 1, SF.EIXO_D), ('roda_dd', -1, SF.EIXO_D), ('roda_te', 1, SF.EIXO_T), ('roda_td', -1, SF.EIXO_T)):
        Vc.parte(no, (s * SF.X_RODA, SF.Y_RODA, zc), 'roda', repouso=(0, 0, 90), item=PECA['roda_aro14'], peca='roda_aro14',
                 tracao=zc > 0, direcao=zc > 0, **REG['roda'])
    ye, ze = SF.ESTEPE
    Vc.parte('estepe', (0, ye, ze), 'peca', repouso=(0, 0, 0), item=PECA['roda_aro14'], peca='roda_aro14',
             obrigatoria=False, ferramentas=[], tempo_s=[10, 15], depende_de=[])
    Vc.parte('motor', (0, 0.26, ZM), 'peca', item=PECA['motor_1_6'], peca='motor_1_6', **REG['motor'])
    Vc.parte('alternador', (-0.22, 0.50, ZM + 0.16), 'peca', item=PECA['alternador'], peca='alternador', **REG['alternador'])
    Vc.parte('radiador', (0, 0.37, 1.905), 'peca', repouso=(90, 0, 0), item=PECA['radiador'], peca='radiador', **REG['radiador'])
    Vc.parte('bateria', (0.30, 0.565, 0.93), 'peca', item=PECA['bateria_12v'], peca='bateria_12v', **REG['bateria'])
    Vc.parte('escapamento', (0, 0.165, -0.5), 'peca', item=PECA['escapamento'], peca='escapamento', **REG['escapamento'])
    Vc.parte('tanque', (0, 0.125, -0.83), 'peca', item=PECA['tanque_45l'], peca='tanque_45l', **REG['tanque'])
    Vc.parte('banco_motorista', (0.37, 0.29, -0.28), 'peca', item=PECA['banco_dianteiro'], peca='banco_dianteiro', **REG['banco_motorista'])
    Vc.parte('banco_passageiro', (-0.37, 0.29, -0.28), 'peca', item=PECA['banco_dianteiro'], peca='banco_dianteiro', **REG['banco_passageiro'])
    Vc.parte('volante', (0.37, 0.82, 0.06), 'peca', repouso=(-68, 0, 0), item=PECA['volante'], peca='volante', **REG['volante'])
    Vc.parte('porta_luvas', (-0.375, 0.586, 0.215), 'tampa', eixo='x', abre_graus=-75, peca=None)
    Vc.parte('quebra_sol_e', (0.38, *_quebra_sol()), 'tampa', eixo='x', abre_graus=-80, peca=None)
    Vc.parte('quebra_sol_d', (-0.38, *_quebra_sol()), 'tampa', eixo='x', abre_graus=-80, peca=None)

    fora, dentro = _carroceria(Vc, _recortes())
    _frisos(Vc, fora)
    p = Vc.base
    _grade(p); _limpadores(p); _cofre(p); _cubos_e_suspensao(p)
    _para_choque(Vc.achar('para_choque_d')['geo'], True); _para_choque(Vc.achar('para_choque_t')['geo'], False)
    _degrau_para_choque(Vc.achar('para_choque_t')['geo']); _alargadores(Vc)
    _tampa_cacamba(Vc.achar('tampa_porta_malas')['geo'])
    for s, l in ((1, 'e'), (-1, 'd')):
        _farol(Vc.achar(f'farol_{l}')['geo'], s); _lanterna_vertical(Vc.achar(f'lanterna_{l}')['geo'], s)
        _retrovisor(Vc.achar(f'retrovisor_{l}')['geo'], s)
    for no, s in (('porta_de', 1), ('porta_dd', -1)):
        _macaneta(Vc.achar(no)['geo'], s, -0.30, -0.17, chave=True); _porta_dentro(Vc.achar(no)['geo'], s, True)
    for no, s, zc in (('roda_de', 1, SF.EIXO_D), ('roda_dd', -1, SF.EIXO_D), ('roda_te', 1, SF.EIXO_T), ('roda_td', -1, SF.EIXO_T)):
        q = V(); _roda(q); g = Vc.achar(no)['geo']
        for k, ms in q.parts.items():
            for m in ms:
                mm = m.copy()
                if s < 0: mm = _mx(mm)
                mm.apply_translation([s * SF.X_RODA, SF.Y_RODA, zc]); g.add(k, mm)
    q = V(); _roda(q); g = Vc.achar('estepe')['geo']
    for k, ms in q.parts.items():
        for m in ms:
            mm = m.copy(); mm.apply_transform(TF.rotation_matrix(math.pi / 2, [0, 0, 1])); mm.apply_translation([0, ye, ze]); g.add(k, mm)
    _motor(Vc.achar('motor')['geo']); _alternador(Vc.achar('alternador')['geo']); _radiador(Vc.achar('radiador')['geo'])
    _bateria(Vc.achar('bateria')['geo']); _escapamento(Vc.achar('escapamento')['geo']); _tanque(Vc.achar('tanque')['geo'])
    _bocal_picape(p)
    _banco_dianteiro(Vc.achar('banco_motorista')['geo'], 0.37); _banco_dianteiro(Vc.achar('banco_passageiro')['geo'], -0.37)
    _painel(Vc, dentro); _forro_e_cabine(Vc, dentro); _cacamba(Vc, fora, dentro)
    _fundo_preto(Vc)
    zb = SF.Z_BOCAL
    for no, pos in (('camera_1a_pessoa', (0.37, 1.13, -0.32)), ('assento_motorista', (0.37, 0.48, -0.30)), ('assento_passageiro', (-0.37, 0.48, -0.30)),
                    ('saida_motorista', (1.35, 0.0, -0.05)), ('saida_passageiro', (-1.35, 0.0, -0.05)),
                    ('subir_cacamba', (0.0, 0.0, SF.ZR - 0.55)), ('bocal_tanque', (round(SF.x_lado(zb, 1.0) - 0.02, 3), 0.80, zb)),
                    ('saida_escape', (-0.43, 0.19, -2.33)), ('luz_farol_e', (0.58, 0.614, 2.09)), ('luz_farol_d', (-0.58, 0.614, 2.09)),
                    ('luz_freio_e', (0.70, 0.86, SF.ZR - 0.03)), ('luz_freio_d', (-0.70, 0.86, SF.ZR - 0.03)),
                    ('macaco_e', (0.70, 0.22, -0.20)), ('macaco_d', (-0.70, 0.22, -0.20)), ('talha_motor', (0.0, 1.40, ZM))):
        Vc.encaixes.append(dict(no=no, pos=pos, tipo='ponto'))
    SAQ = {
        'cacamba': [['caixa_ferramentas', 0.25], ['galao_gasolina', 0.2], ['tabuas', 0.3], ['saco_cimento', 0.15], ['pneu_velho', 0.2], ['corda', 0.3],
                    ['lona', 0.25], ['caixa_papelao', 0.3], ['pa', 0.15], ['enxada', 0.1], ['sucata', 0.4]],
        'porta_luvas': [['mapa_cidade', 0.4], ['lanterna', 0.3], ['pilhas', 0.3], ['isqueiro', 0.25], ['fita_isolante', 0.3], ['chave_casa', 0.1], ['frasco_remedio', 0.1]],
        'bolsa': [['garrafa_agua', 0.2], ['salgadinho', 0.2], ['chave_carro', 0.02]],
        'console': [['isqueiro', 0.3], ['pilhas', 0.2]],
        'quebra_sol': [['chave_carro', 0.10]],
        'atras_banco': [['macaco_sanfona', 0.6], ['chave_de_roda', 0.6], ['cabos_chupeta', 0.25], ['mangueira_sifao', 0.15], ['roupas', 0.2]],
    }
    Vc.compartimento('cacamba', 'Caçamba', (10, 6), None, saque=SAQ['cacamba'], aberta=True, carga_kg=600,
                     nota='aberta: qualquer um pega e a chuva molha; com a tampa aberta vira 10 × 8')
    Vc.compartimento('atras_banco', 'Atrás do banco', (4, 2), None, saque=SAQ['atras_banco'])
    Vc.compartimento('porta_luvas', 'Porta-luvas', (3, 2), 'porta_luvas', saque=SAQ['porta_luvas'])
    Vc.compartimento('bolsa_porta_de', 'Bolsa da porta do motorista', (3, 1), 'porta_de', saque=SAQ['bolsa'])
    Vc.compartimento('bolsa_porta_dd', 'Bolsa da porta do passageiro', (3, 1), 'porta_dd', saque=SAQ['bolsa'])
    Vc.compartimento('console', 'Console', (2, 1), None, saque=SAQ['console'])
    Vc.compartimento('quebra_sol_e', 'Quebra-sol do motorista', (1, 1), 'quebra_sol_e', saque=SAQ['quebra_sol'])
    Vc.compartimento('quebra_sol_d', 'Quebra-sol do passageiro', (1, 1), 'quebra_sol_d', saque=SAQ['quebra_sol'])


def _cacamba(Vc, fora, dentro):
    """Caçamba: assoalho com frisos, paredes de dentro, parede da frente, caixas de roda, ganchos e a parede de trás da cabine."""
    p = Vc.base; yf = SF.Y_FUNDO; rc = SF.REC_CACAMBA
    zp, xa = SF.Z_POSTE, SF.X_ABERTURA
    anel = SF.planta_cacamba(rc - 0.02, z1=zp).difference(SF.planta_cacamba(rc, z1=zp))
    p.add('pintura', inter(prisma_xz(anel, yf - 0.02, 2.0), fora))                                       # paredes de dentro
    p.add('pintura', prisma_xz(SF.planta_cacamba(rc - 0.02, z1=zp), yf - 0.02, yf))                      # assoalho
    p.add('pintura', _cx(-xa - 0.02, xa + 0.02, yf - 0.02, yf, SF.ZR + 0.035, zp))
    for s in (1, -1):                                                                                     # frente das colunas das quinas
        def L(m): return m if s > 0 else _mx(m)
        p.add('pintura', L(inter(_cx(xa, 0.9, yf - 0.02, 2.0, zp - 0.02, zp), fora)))
        p.add('pintura', L(inter(_cx(xa, xa + 0.02, yf - 0.02, 2.0, SF.ZR + 0.03, zp), fora)))
    p.add('pintura', inter(_cx(-0.9, 0.9, yf - 0.02, 2.0, SF.Z_CAB, SF.Z_CAB + 0.02), fora))              # parede da frente
    for k in range(9):                                                                                    # frisos do assoalho
        x = -0.40 + k * 0.10
        p.add('pintura', _cham(x - 0.018, x + 0.018, yf, yf + 0.009, SF.ZR + 0.08, SF.Z_CAB - 0.05, 0.004))
    for s in (1, -1):
        def L(m): return m if s > 0 else _mx(m)
        casa = menos(cil_x(SF.R_CAIXA + 0.04, 0.47, 0.84, SF.Y_CAIXA, SF.EIXO_T, 64), cil_x(SF.R_CAIXA + 0.018, 0.49, 1.2, SF.Y_CAIXA, SF.EIXO_T, 64))
        casa = inter(inter(casa, _cx(0.0, 1.2, yf - 0.02, 2.0, -3, 0)), fora)
        p.add('pintura', L(casa))                                                                         # caixa de roda dentro da caçamba
        for z in (SF.Z_CAB - 0.12, SF.ZR + 0.22):                                                         # ganchos de amarrar
            x = SF.x_lado(z, 1.0) - rc + 0.003
            p.add('aco_escuro', L(_cx(x - 0.006, x, 0.78, 0.84, z - 0.03, z + 0.03)))
            p.add('aco_escuro', L(tubo([(x - 0.004, 0.80, z - 0.022), (x - 0.03, 0.79, z - 0.015), (x - 0.03, 0.79, z + 0.015), (x - 0.004, 0.80, z + 0.022)], 0.006, 8)))
    # parede de trás da cabine, por dentro, e um tapete atrás dos bancos
    p.add('carpete', inter(dentro, _cx(-0.79, 0.79, 0.0, 2.0, -0.80, -0.78)))
    p.add('carpete', inter(dentro, _cx(-0.70, 0.70, 0.29, 0.31, -0.78, -0.64)))
    # cinta do estepe deitado na frente da caçamba
    ye, ze = SF.ESTEPE
    for x in (-0.12, 0.12):
        p.add('fio_preto', tubo([(x, yf + 0.005, ze - 0.33), (x, ye + 0.10, ze - 0.22), (x, ye + 0.10, ze + 0.22), (x, yf + 0.005, ze + 0.33)], 0.008, 8))
        p.add('aco_escuro', _cx(x - 0.02, x + 0.02, yf, yf + 0.012, ze - 0.345, ze - 0.325))
        p.add('aco_escuro', _cx(x - 0.02, x + 0.02, yf, yf + 0.012, ze + 0.325, ze + 0.345))


def _tampa_cacamba(q):
    """Puxador no meio da borda de cima, placa embaixo e as dobradiças."""
    z = SF.ZR - 0.004; zt = SF.ZR + 0.035
    d = SF.DY_CINTURA
    q.add('plastico_preto', _cham(-0.12, 0.12, 0.885 + d, 0.925 + d, z - 0.008, z + 0.006, 0.006))
    q.add('chassi', _cx(-0.10, 0.10, 0.892 + d, 0.915 + d, z - 0.010, z - 0.004))
    q.add('cromado', _cham(-0.09, 0.09, 0.897 + d, 0.912 + d, z - 0.014, z - 0.008, 0.003))
    q.add('plastico_preto', _cx(-0.215, 0.215, 0.60, 0.75, z - 0.006, z + 0.002))
    q.add('placa', _cham(-0.2, 0.2, 0.607, 0.743, z - 0.010, z - 0.006, 0.003))
    for x in (-0.55, 0.55):
        q.add('aco_escuro', _cil_x(0.012, x - 0.04, x + 0.04, SF.Y_FUNDO + 0.06, SF.ZR + 0.02))         # dobradiças
    for s in (1, -1):                                                                                     # travas laterais
        def L(m): return m if s > 0 else _mx(m)
        q.add('aco_escuro', L(_cx(SF.X_TAMPA - 0.012, SF.X_TAMPA - 0.002, 0.90 + d, 0.93 + d, zt - 0.025, zt - 0.005)))
    q.add('pintura', _cham(-0.58, 0.58, 0.935 + d, 0.95 + d, zt - 0.03, zt, 0.004))                                # friso estampado em cima


def _cil_x(r, x0, x1, y, z, sec=16):
    return cil_x(r, x0, x1, y, z, sec)


def _degrau_para_choque(q):
    """Degrau de borracha no meio do para-choque, para subir na caçamba."""
    z = SF.ZR - 0.062
    q.add('borracha', _cham(-0.26, 0.26, 0.495, 0.505, z - 0.04, z + 0.06, 0.004))
    for k in range(7): q.add('borracha', _cx(-0.24, 0.24, 0.505, 0.509, z - 0.03 + k * 0.012, z - 0.025 + k * 0.012))


def _bocal_picape(p):
    """Bocal na lateral da caçamba, atrás da roda: o copo fica no vão da parede e a mangueira desce por dentro dela."""
    dz = SF.Z_BOCAL + 1.86; dx = SF.x_lado(SF.Z_BOCAL, 1.0) - 0.8085
    T = TF.translation_matrix([dx, 0, dz])
    p.add('chassi', menos(_cx(0.745, 0.778, 0.735, 0.865, -1.958, -1.762), _cx(0.755, 0.9, 0.745, 0.855, -1.948, -1.772)).apply_transform(T))
    p.add('plastico_preto', cil_x(0.034, 0.755, 0.772, 0.80, -1.86, 24).apply_transform(T))
    p.add('plastico_preto', _cx(0.766, 0.774, 0.79, 0.81, -1.89, -1.83).apply_transform(T))
    zb = SF.Z_BOCAL
    p.add('borracha', tubo(suavizar_caminho([(0.36, 0.20, -0.95), (0.45, 0.25, -1.30), (0.56, 0.32, -1.72), (0.765, 0.42, zb + 0.08),
                                             (0.765, 0.66, zb + 0.03), (0.766 + dx, 0.79, zb)], 3), 0.02, 12))


def _alargadores(Vc):
    """Alargadores de plástico preto em volta das rodas: o da frente vai no para-lama, o de trás na carroceria."""
    for zc, frente in ((SF.EIXO_D, True), (SF.EIXO_T, False)):
        r0, r1 = SF.R_CAIXA - 0.004, SF.R_CAIXA + 0.065
        ang = np.linspace(math.radians(-8), math.radians(188), 40)
        fora_ = [(zc + r1 * math.cos(a), SF.Y_CAIXA + r1 * math.sin(a)) for a in ang]
        dentro_ = [(zc + r0 * math.cos(a), SF.Y_CAIXA + r0 * math.sin(a)) for a in ang[::-1]]
        pg = _Pg(fora_ + dentro_).buffer(0.006, join_style=1).buffer(-0.006, join_style=1)
        w = SF.x_lado(zc, 1.0)
        m = prisma_zy(pg, w - 0.03, w + 0.028)
        m = menos(m, cil_x(SF.R_CAIXA, 0.3, 1.2, SF.Y_CAIXA, zc, 64))
        for s, no in ((1, 'paralama_e'), (-1, 'paralama_d')):
            mm = m if s > 0 else _mx(m)
            (Vc.achar(no)['geo'] if frente else Vc.base).add('plastico_preto', mm)
        for s in (1, -1):                                                                            # parafusos
            for a in np.linspace(math.radians(10), math.radians(170), 5):
                zz, yy = zc + (r0 + r1) / 2 * math.cos(a), SF.Y_CAIXA + (r0 + r1) / 2 * math.sin(a)
                c = cil_x(0.007, w + 0.026, w + 0.032, yy, zz, 10)
                (Vc.achar('paralama_e' if s > 0 else 'paralama_d')['geo'] if frente else Vc.base).add('aco_escuro', c if s > 0 else _mx(c))
