# Veiculo 4: van Jornada (van de carga, desenho próprio e sem marca).
# Frente, portas e cabine com desenho próprio (bico curto, para-brisa grande, teto alto contínuo); motor, rodas, tanque, escapamento,
# bancos e painel são os do sedã Rumo. Atrás, o baú com duas portas que abrem para os lados. Carregado por gerar_veiculos.py depois de veiculo01_sedan.py (a forma vem de van_forma.py).
import van_forma as _VF

PECA.update({
    'porta_traseira_e_van': _peca('porta_traseira_e_van', 'Porta de trás esquerda da van', 16, 'van_jornada', 'fecha o baú; tem a maçaneta e a fechadura', carga_maos=True),
    'porta_traseira_d_van': _peca('porta_traseira_d_van', 'Porta de trás direita da van', 16, 'van_jornada', 'fecha o baú; abre depois da esquerda', carga_maos=True),
    'para_choque_traseiro_van': _peca('para_choque_traseiro_van', 'Para-choque traseiro da van', 7, 'van_jornada', 'absorve a primeira parte das batidas de trás; tem o degrau', (7, 1)),
    'divisoria_van': _peca('divisoria_van', 'Divisória da cabine', 9, 'van_jornada', 'segura a carga numa freada e esconde o baú de quem olha pela janela', carga_maos=True),
})
_frente_propria('_van', 'van_jornada', 'da van')


@modelo('van_jornada', 'Van Jornada', classe='van', portas=4, lugares=2,
        descricao='Van de carga, desenho próprio e sem marca: bico curto e redondo, faróis largos, para-brisa grande e teto alto contínuo '
                  'até atrás. O motor, as rodas, o tanque, o escapamento, os bancos e o volante são os mesmos do sedã Rumo. O baú tem '
                  'assoalho de compensado, leva 650 kg '
                  'e abre por duas portas atrás; o estepe fica num poço debaixo do assoalho.',
        fisica=dict(massa_kg=1100, centro_massa_m=[0, 0.55, 0.15], tracao='dianteira', forca_motor_n=3300, freio=38, carga_kg=650,
                    direcao_graus=[32, 8], vel_max_kmh=130, roda_raio_m=_VF.R_RODA, roda_largura_m=0.185,
                    suspensao=dict(curso_m=0.16, rigidez=50, compressao=0.85, retorno=0.9), atrito_pneu=dict(asfalto=2.6, terra=1.9, grama=1.5, lama=1.0)),
        combustivel=dict(tanque_l=45, consumo_l_100km=9, marcha_lenta_l_h=0.8, bocal='tampa_combustivel'),
        bateria=dict(capacidade_ah=45), cor_padrao=_fator((232, 232, 226)),
        cores_sorteio=[_fator(c) for c in [(232, 232, 226), (196, 40, 32), (30, 66, 120), (210, 170, 40), (70, 90, 70), (140, 142, 140),
                                           (60, 60, 64), (214, 110, 40)]])
def van_jornada(Vc):
    global SF
    SF = _VF
    _partes_carroceria(Vc)
    X0 = SF.x_lado(0.50, 1.0) - 0.07
    abre_tras = 'porta_te|porta_td:aberta'
    for no, s, it, ab in (('porta_te', 1, 'porta_traseira_e_van', -100), ('porta_td', -1, 'porta_traseira_d_van', 100)):
        Vc.parte(no, (s * SF.X_PORTA, 1.14, SF.ZR), 'porta', eixo='y', abre_graus=ab, repouso=(90, 0, 0), item=PECA[it], peca=it,
                 obrigatoria=False, ferramentas=_JC, tempo_s=[50, 60], depende_de=[])
    Vc.parte('para_choque_d', (0, 0.315, SF.ZF), 'peca', item=PECA['para_choque_dianteiro_van'], peca='para_choque_dianteiro_van', **REG['para_choque'])
    Vc.parte('para_choque_t', (0, 0.315, SF.ZR), 'peca', item=PECA['para_choque_traseiro_van'], peca='para_choque_traseiro_van', **REG['para_choque'])
    for s, l in ((1, 'e'), (-1, 'd')):
        Vc.parte(f'farol_{l}', (s * 0.58, 0.61, 2.03), 'peca', item=PECA['farol_van'], peca='farol_van', **REG['farol'])
    for s, l in ((1, 'e'), (-1, 'd')):
        Vc.parte(f'lanterna_{l}', (s * 0.70, 0.79, SF.ZR + 0.06), 'peca', item=PECA['lanterna_vertical'], peca='lanterna_vertical',
                 **dict(REG['lanterna'], depende_de=[abre_tras]))
    for s, l, pai in ((1, 'e', 'porta_de'), (-1, 'd', 'porta_dd')):
        Vc.parte(f'retrovisor_{l}', (s * X0, 0.955 + SF.DY_CINTURA, 0.50), 'peca', pai=pai, item=PECA['retrovisor'], peca='retrovisor', **REG['retrovisor'])
    for no, s, zc in (('roda_de', 1, SF.EIXO_D), ('roda_dd', -1, SF.EIXO_D), ('roda_te', 1, SF.EIXO_T), ('roda_td', -1, SF.EIXO_T)):
        Vc.parte(no, (s * SF.X_RODA, SF.Y_RODA, zc), 'roda', repouso=(0, 0, 90), item=PECA['roda_aro14'], peca='roda_aro14',
                 tracao=zc > 0, direcao=zc > 0, **REG['roda'])
    ye, ze = SF.ESTEPE
    Vc.parte('estepe', (0, ye, ze), 'peca', repouso=(0, 0, 0), item=PECA['roda_aro14'], peca='roda_aro14',
             **dict(REG['estepe'], depende_de=[abre_tras, 'assoalho_porta_malas:aberto']))
    Vc.parte('motor', (0, 0.26, ZM), 'peca', item=PECA['motor_1_6'], peca='motor_1_6', **REG['motor'])
    Vc.parte('alternador', (-0.22, 0.50, ZM + 0.16), 'peca', item=PECA['alternador'], peca='alternador', **REG['alternador'])
    Vc.parte('radiador', (0, 0.37, 1.905), 'peca', repouso=(90, 0, 0), item=PECA['radiador'], peca='radiador', **REG['radiador'])
    Vc.parte('bateria', (0.30, 0.565, 0.93), 'peca', item=PECA['bateria_12v'], peca='bateria_12v', **REG['bateria'])
    Vc.parte('escapamento', (0, 0.165, -0.5), 'peca', item=PECA['escapamento'], peca='escapamento', **REG['escapamento'])
    Vc.parte('tanque', (0, 0.125, -0.83), 'peca', item=PECA['tanque_45l'], peca='tanque_45l', **REG['tanque'])
    Vc.parte('banco_motorista', (0.37, 0.29, -0.28), 'peca', item=PECA['banco_dianteiro'], peca='banco_dianteiro', **REG['banco_motorista'])
    Vc.parte('banco_passageiro', (-0.37, 0.29, -0.28), 'peca', item=PECA['banco_dianteiro'], peca='banco_dianteiro', **REG['banco_passageiro'])
    Vc.parte('divisoria', (0, SF.Y_PISO, SF.Z_DIVISORIA), 'peca', repouso=(90, 0, 0), item=PECA['divisoria_van'], peca='divisoria_van',
             obrigatoria=False, ferramentas=_JC, tempo_s=[60, 75], depende_de=[abre_tras])
    Vc.parte('volante', (0.37, 0.82, 0.06), 'peca', repouso=(-68, 0, 0), item=PECA['volante'], peca='volante', **REG['volante'])
    Vc.parte('porta_luvas', (-0.375, 0.586, 0.215), 'tampa', eixo='x', abre_graus=-75, peca=None)
    Vc.parte('assoalho_porta_malas', (0, SF.Y_PISO, -1.60), 'tampa', eixo='x', abre_graus=75, peca=None)
    Vc.parte('quebra_sol_e', (0.38, *_quebra_sol()), 'tampa', eixo='x', abre_graus=-80, peca=None)
    Vc.parte('quebra_sol_d', (-0.38, *_quebra_sol()), 'tampa', eixo='x', abre_graus=-80, peca=None)

    fora, dentro = _carroceria(Vc, _recortes())
    _frisos(Vc, fora)
    p = Vc.base
    _grade(p); _limpadores(p); _cofre(p); _cubos_e_suspensao(p)
    _para_choque(Vc.achar('para_choque_d')['geo'], True); _para_choque(Vc.achar('para_choque_t')['geo'], False)
    _degrau_para_choque(Vc.achar('para_choque_t')['geo'])
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
    _painel(Vc, dentro); _forro_e_cabine(Vc, dentro)
    _portas_tras(Vc); _bau(Vc, dentro); _divisoria(Vc, dentro); _nervuras_teto(p)
    _fundo_preto(Vc)
    zb = SF.Z_BOCAL
    for no, pos in (('camera_1a_pessoa', (0.37, 1.13, -0.32)), ('assento_motorista', (0.37, 0.48, -0.30)), ('assento_passageiro', (-0.37, 0.48, -0.30)),
                    ('saida_motorista', (1.35, 0.0, -0.05)), ('saida_passageiro', (-1.35, 0.0, -0.05)),
                    ('carregar_bau', (0.0, 0.0, SF.ZR - 0.70)), ('bocal_tanque', (round(SF.x_lado(zb, 1.0) - 0.02, 3), 0.80, zb)),
                    ('saida_escape', (-0.43, 0.19, -2.33)), ('luz_farol_e', (0.58, 0.614, 2.09)), ('luz_farol_d', (-0.58, 0.614, 2.09)),
                    ('luz_freio_e', (0.70, 0.86, SF.ZR - 0.03)), ('luz_freio_d', (-0.70, 0.86, SF.ZR - 0.03)), ('luz_freio_alta', (0.0, 1.76, SF.ZR - 0.02)),
                    ('macaco_e', (0.70, 0.22, -0.20)), ('macaco_d', (-0.70, 0.22, -0.20)), ('talha_motor', (0.0, 1.40, ZM))):
        Vc.encaixes.append(dict(no=no, pos=pos, tipo='ponto'))
    SAQ = {
        'bau': [['caixa_papelao', 0.45], ['caixa_ferramentas', 0.2], ['galao_gasolina', 0.15], ['garrafao_agua', 0.2], ['enlatados', 0.25],
                ['cobertor', 0.2], ['lona', 0.2], ['corda', 0.3], ['tabuas', 0.15], ['pneu_velho', 0.1], ['caixa_remedios', 0.06], ['sucata', 0.3]],
        'porta_luvas': [['mapa_cidade', 0.4], ['lanterna', 0.3], ['pilhas', 0.3], ['isqueiro', 0.25], ['fita_isolante', 0.3], ['chave_casa', 0.1],
                        ['nota_entrega', 0.5], ['frasco_remedio', 0.1]],
        'bolsa': [['garrafa_agua', 0.2], ['salgadinho', 0.2], ['chave_carro', 0.02]],
        'console': [['isqueiro', 0.3], ['pilhas', 0.2]],
        'quebra_sol': [['chave_carro', 0.10]],
        'poco_estepe': [['macaco_sanfona', 0.7], ['chave_de_roda', 0.7], ['triangulo', 0.5], ['cabos_chupeta', 0.2]],
    }
    Vc.compartimento('bau', 'Baú', (10, 8), 'porta_te', saque=SAQ['bau'], tranca=True, carga_kg=650,
                     nota='abre pela porta de trás esquerda (a direita só abre depois dela); 1,28 m de altura: as caixas empilham')
    Vc.compartimento('poco_estepe', 'Poço do estepe', (4, 2), 'assoalho_porta_malas', saque=SAQ['poco_estepe'])
    Vc.compartimento('porta_luvas', 'Porta-luvas', (3, 2), 'porta_luvas', saque=SAQ['porta_luvas'])
    Vc.compartimento('bolsa_porta_de', 'Bolsa da porta do motorista', (3, 1), 'porta_de', saque=SAQ['bolsa'])
    Vc.compartimento('bolsa_porta_dd', 'Bolsa da porta do passageiro', (3, 1), 'porta_dd', saque=SAQ['bolsa'])
    Vc.compartimento('console', 'Console', (2, 1), None, saque=SAQ['console'])
    Vc.compartimento('quebra_sol_e', 'Quebra-sol do motorista', (1, 1), 'quebra_sol_e', saque=SAQ['quebra_sol'])
    Vc.compartimento('quebra_sol_d', 'Quebra-sol do passageiro', (1, 1), 'quebra_sol_d', saque=SAQ['quebra_sol'])


def _portas_tras(Vc):
    """Portas de trás: dobradiças na quina, maçaneta e fechadura na esquerda, forro de chapa por dentro, a placa embaixo."""
    z = SF.ZR; y0, y1 = SF.Y_PORTA; xp = SF.X_PORTA
    for no, s in (('porta_te', 1), ('porta_td', -1)):
        q = Vc.achar(no)['geo']
        def L(m): return m if s > 0 else _mx(m)
        for y in (y0 + 0.16, (y0 + y1) / 2, y1 - 0.16):                                                   # dobradiças
            q.add('aco_escuro', L(_cx(xp - 0.07, xp - 0.004, y - 0.035, y + 0.035, z - 0.008, z + 0.001)))
            q.add('aco_escuro', L(cyl_eixo_y(0.011, y - 0.04, y + 0.04, xp - 0.002, z - 0.012)))
        q.add('chassi', L(_cx(0.04, xp - 0.04, 0.60, 1.12, z + 0.030, z + 0.036)))                         # forro de chapa por dentro
        for y in (0.70, 0.86, 1.02): q.add('chassi', L(_cx(0.06, xp - 0.06, y - 0.015, y + 0.015, z + 0.036, z + 0.040)))
        q.add('borracha', L(_cx(0.006, 0.016, y0 + 0.02, y1 - 0.02, z - 0.004, z + 0.03)))                 # borracha do vão do meio
    q = Vc.achar('porta_te')['geo']                                                                        # maçaneta e fechadura
    q.add('plastico_preto', _cham(0.05, 0.20, 1.02, 1.07, z - 0.012, z + 0.002, 0.006))
    q.add('chassi', _cx(0.07, 0.18, 1.03, 1.06, z - 0.006, z - 0.001))
    c = trimesh.creation.cylinder(radius=0.012, height=0.012, sections=20); c.apply_translation([0.125, 0.995, z - 0.008]); q.add('cromado', c)
    q.add('aco_escuro', tubo([(0.06, 0.62, z + 0.045), (0.06, 1.66, z + 0.045)], 0.006, 8))                 # varão da trava por dentro
    q.add('aco_escuro', _cx(0.03, 0.09, 1.04, 1.10, z + 0.036, z + 0.05))
    q = Vc.achar('porta_td')['geo']
    q.add('plastico_preto', _cx(-0.20, -0.06, 1.12, 1.14, z - 0.008, z + 0.002))                            # emblema liso
    p = Vc.base                                                                                            # placa no vão de baixo
    q = Vc.achar('porta_te')['geo']
    q.add('plastico_preto', _cx(0.05, 0.48, 0.585, 0.745, z - 0.010, z + 0.002))
    q.add('placa', _cham(0.065, 0.465, 0.597, 0.732, z - 0.014, z - 0.010, 0.003))
    for x in (0.12, 0.42): q.add('lente_re', _cx(x - 0.02, x + 0.02, 0.748, 0.756, z - 0.016, z - 0.006))  # luz da placa
    p.add('plastico_preto', _cham(-0.15, 0.15, 1.742, 1.778, z - 0.010, z + 0.004, 0.004))                  # luz de freio alta
    p.add('lente_lanterna', _cx(-0.135, 0.135, 1.748, 1.772, z - 0.014, z - 0.008))


def cyl_eixo_y(r, y0, y1, x, z, sec=16):
    return _cil_y(r, y0, y1, x, z, sec)


def _bau(Vc, dentro):
    """Baú: assoalho de compensado com tampa do poço, forração lateral, capas das caixas de roda, trilhos de amarrar e arcos do teto."""
    p = Vc.base; yf = SF.Y_PISO; xf = SF.X_FORRO; z0, z1 = SF.ZR + 0.035, SF.Z_DIVISORIA + 0.02
    rodas = [cil_x(SF.R_CAIXA + 0.042, a, b, SF.Y_CAIXA, SF.EIXO_T, 64) for a, b in ((0.46, 1.2), (-1.2, -0.46))]
    tampa = _cx(-0.36, 0.36, yf - 0.02, yf, -2.26, -1.60)
    piso = menos(inter(dentro, _cx(-xf, xf, yf - 0.02, yf, z0, z1)), *rodas, _cx(-0.364, 0.364, yf - 0.03, yf + 0.01, -2.264, -1.596))
    p.add('madeira_crua', piso)
    for x in (-0.50, 0.50):                                                                               # trilhos de alumínio no assoalho
        p.add('aluminio', _cham(x - 0.02, x + 0.02, yf, yf + 0.008, z0 + 0.02, -1.70, 0.003))
    ass = Vc.achar('assoalho_porta_malas')['geo']
    ass.add('madeira_crua', inter(dentro, tampa))
    ass.add('aco_escuro', _cx(-0.05, 0.05, yf, yf + 0.006, -2.20, -2.16))                                   # argola de puxar
    # poço do estepe e o vão debaixo do assoalho
    p.add('chassi', inter(dentro, _cx(-0.40, 0.40, 0.24, 0.26, -2.30, -1.56)))
    for s in (1, -1):
        def L(m): return m if s > 0 else _mx(m)
        p.add('chassi', L(inter(dentro, _cx(0.38, 0.40, 0.26, yf - 0.02, -2.30, -1.56))))
    p.add('chassi', inter(dentro, _cx(-0.40, 0.40, 0.26, yf - 0.02, -1.58, -1.56)))
    for s in (1, -1):
        def L(m): return m if s > 0 else _mx(m)
        # capa da caixa de roda: casca que sai da lateral e a tampa de lado
        casa = menos(cil_x(SF.R_CAIXA + 0.042, 0.47, 0.86, SF.Y_CAIXA, SF.EIXO_T, 64), cil_x(SF.R_CAIXA + 0.020, 0.49, 1.2, SF.Y_CAIXA, SF.EIXO_T, 64))
        p.add('chassi', L(inter(inter(casa, _cx(0.0, 1.2, yf - 0.02, 2.0, -3, 0)), dentro)))
        # forração de compensado: em cima da roda inteira, embaixo só na frente e atrás dela
        fo = menos(inter(dentro, _cx(xf, xf + 0.012, yf - 0.02, 1.22, z0, z1)), cil_x(SF.R_CAIXA + 0.042, 0.4, 1.2, SF.Y_CAIXA, SF.EIXO_T, 64))
        p.add('madeira_crua', L(fo))
        for y in (0.82, 1.08):                                                                            # trilhos de amarrar
            p.add('aluminio', L(_cx(xf - 0.010, xf, y - 0.02, y + 0.02, z0 + 0.04, z1 - 0.04)))
            for k in range(16):
                zz = z0 + 0.08 + k * 0.095
                if zz > z1 - 0.06: break
                p.add('aco_escuro', L(_cx(xf - 0.012, xf - 0.010, y - 0.008, y + 0.008, zz - 0.02, zz + 0.02)))
        p.add('aluminio', L(_cx(xf - 0.03, xf + 0.012, yf, 1.22, z0, z0 + 0.03)))                          # cantoneira da porta
    # arcos do teto e da lateral (por dentro da chapa)
    anel_ = menos(SF.corpo_cabine(0.022, pontas=0.03), SF.corpo_cabine(0.05, pontas=0.0))
    for z in (-1.15, -1.65, -2.10):
        p.add('pintura', inter(anel_, _cx(-0.9, 0.9, 1.22, 2.0, z - 0.025, z + 0.025)))
    p.add('plastico_translucido', _cham(-0.10, 0.10, 1.755, 1.775, -1.42, -1.30, 0.008))                  # luz do baú


def _divisoria(Vc, dentro):
    """Divisória atrás dos bancos: chapa até a cintura e grade até o teto, com moldura."""
    q = Vc.achar('divisoria')['geo']; z = SF.Z_DIVISORIA; yf = SF.Y_PISO
    sec = inter(dentro, _cx(-0.9, 0.9, 0.0, 2.0, z, z + 0.015))
    q.add('chassi', inter(sec, _cx(-0.9, 0.9, 0.29, 1.05, z, z + 0.015)))
    for k in range(7): q.add('chassi', inter(sec, _cx(-0.9, 0.9, 0.45 + k * 0.08, 0.465 + k * 0.08, z - 0.006, z)))   # vincos
    alto = inter(dentro, _cx(-0.9, 0.9, 1.05, 2.0, z + 0.004, z + 0.012))
    moldura = menos(alto, inter(dentro, _cx(-0.68, 0.68, 1.09, 1.70, -3, 3)))
    q.add('chassi', moldura)
    for x in np.arange(-0.62, 0.63, 0.08):
        q.add('aco_escuro', inter(alto, _cx(x - 0.006, x + 0.006, 1.05, 2.0, -3, 3)))
    for y in (1.30, 1.50): q.add('aco_escuro', inter(alto, _cx(-0.9, 0.9, y - 0.006, y + 0.006, -3, 3)))


def _nervuras_teto(p):
    """Quatro nervuras estampadas no teto, da coluna do meio até perto da traseira, e as calhas de chuva nas laterais do teto."""
    z0, z1 = -0.42, SF.ZR + 0.12
    for x in (-0.45, -0.15, 0.15, 0.45):
        zs = np.linspace(z0, z1, 24); an = []
        for z in zs:
            y = SF.ytop(z) - 0.004
            an.append([(x - 0.045, y, z), (x - 0.02, y + 0.012, z), (x + 0.02, y + 0.012, z), (x + 0.045, y, z), (x, y - 0.01, z)])
        p.add('pintura', loft(an))
    for s in (1, -1):
        zs = np.linspace(SF.Z_CALHA, SF.ZR + 0.03, 40); an = []
        for z in zs:
            x, y = SF.quina_cabine(z); x = x * s
            an.append([(x - 0.006 * s, y + 0.012, z), (x + 0.008 * s, y + 0.010, z), (x + 0.010 * s, y, z), (x - 0.004 * s, y + 0.002, z)])
        m = loft(an)
        if s < 0: m.invert()
        p.add('cromado', m)
