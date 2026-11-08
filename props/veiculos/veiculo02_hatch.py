# Veiculo 2: hatch Brisa (hatch compacto de 4 portas da família Rumo, desenho próprio e sem marca).
# Mesma frente, entre-eixos, motor, rodas, tanque, interior e portas dianteiras do sedã Rumo: essas peças trocam entre os dois.
# Carregado por gerar_veiculos.py depois de veiculo01_sedan.py (usa as funções de lá; a forma vem de hatch_forma.py).
import hatch_forma as _HF

PECA.update({
    'tampa_traseira_hatch': _peca('tampa_traseira_hatch', 'Tampa traseira do hatch', 12, 'hatch_brisa', 'fecha a traseira; leva o vidro e o limpador', carga_maos=True),
    'vidro_traseiro_hatch': _peca('vidro_traseiro_hatch', 'Vidro da tampa do hatch', 6, 'hatch_brisa', 'protege a traseira da cabine', carga_maos=True),
    'porta_traseira_e_hatch': _peca('porta_traseira_e_hatch', 'Porta traseira esquerda do hatch', 18, 'hatch_brisa', 'protege quem vai atrás', carga_maos=True),
    'porta_traseira_d_hatch': _peca('porta_traseira_d_hatch', 'Porta traseira direita do hatch', 18, 'hatch_brisa', 'protege quem vai atrás', carga_maos=True),
    'para_choque_traseiro_hatch': _peca('para_choque_traseiro_hatch', 'Para-choque traseiro do hatch', 6, 'hatch_brisa', 'absorve a primeira parte das batidas de trás', (6, 1)),
    'lanterna_vertical': _peca('lanterna_vertical', 'Lanterna traseira em pé', 1, 'universal', 'luz de freio, de ré e pisca', (1, 2)),
    'escapamento_curto': _peca('escapamento_curto', 'Escapamento curto com silencioso', 7, 'hatch_brisa', 'sem ele o motor faz o dobro de barulho', (5, 1)),
})


@modelo('hatch_brisa', 'Hatch Brisa', classe='compacto', portas=4, lugares=5,
        descricao='Hatch compacto de 4 portas da família Rumo, desenho próprio e sem marca. A frente, as portas dianteiras, o motor, as rodas, '
                  'o tanque, os bancos e o volante são os mesmos do sedã Rumo e trocam entre os dois. A tampa traseira leva o vidro e abre inteira.',
        fisica=dict(massa_kg=960, centro_massa_m=[0, 0.45, 0.12], tracao='dianteira', forca_motor_n=3200, freio=40,
                    direcao_graus=[32, 8], vel_max_kmh=145, roda_raio_m=_HF.R_RODA, roda_largura_m=0.185,
                    suspensao=dict(curso_m=0.15, rigidez=38, compressao=0.85, retorno=0.9), atrito_pneu=dict(asfalto=2.6, terra=1.8, grama=1.4, lama=0.9)),
        combustivel=dict(tanque_l=45, consumo_l_100km=7.5, marcha_lenta_l_h=0.8, bocal='tampa_combustivel'),
        bateria=dict(capacidade_ah=45), cor_padrao=_fator((214, 168, 40)),
        cores_sorteio=[_fator(c) for c in [(214, 168, 40), (230, 228, 220), (36, 92, 140), (150, 30, 32), (86, 104, 60), (60, 60, 64),
                                           (190, 120, 70), (160, 176, 186)]])
def hatch_brisa(Vc):
    global SF
    SF = _HF
    _partes_carroceria(Vc)
    X0 = SF.x_lado(0.50, 1.0) - 0.07
    Vc.parte('para_choque_d', (0, 0.315, SF.ZF), 'peca', item=PECA['para_choque_dianteiro'], peca='para_choque_dianteiro', **REG['para_choque'])
    Vc.parte('para_choque_t', (0, 0.315, SF.ZR), 'peca', item=PECA['para_choque_traseiro_hatch'], peca='para_choque_traseiro_hatch', **REG['para_choque'])
    for s, l in ((1, 'e'), (-1, 'd')):
        Vc.parte(f'farol_{l}', (s * 0.58, 0.61, 2.03), 'peca', item=PECA['farol'], peca='farol', **REG['farol'])
    for s, l in ((1, 'e'), (-1, 'd')):
        Vc.parte(f'lanterna_{l}', (s * 0.70, 0.79, SF.ZR + 0.06), 'peca', item=PECA['lanterna_vertical'], peca='lanterna_vertical', **REG['lanterna'])
    for s, l, pai in ((1, 'e', 'porta_de'), (-1, 'd', 'porta_dd')):
        Vc.parte(f'retrovisor_{l}', (s * X0, 0.955, 0.50), 'peca', pai=pai, item=PECA['retrovisor'], peca='retrovisor', **REG['retrovisor'])
    for no, s, zc in (('roda_de', 1, SF.EIXO_D), ('roda_dd', -1, SF.EIXO_D), ('roda_te', 1, SF.EIXO_T), ('roda_td', -1, SF.EIXO_T)):
        Vc.parte(no, (s * SF.X_RODA, SF.Y_RODA, zc), 'roda', repouso=(0, 0, 90), item=PECA['roda_aro14'], peca='roda_aro14',
                 tracao=zc > 0, direcao=zc > 0, **REG['roda'])
    ye, ze = SF.ESTEPE
    Vc.parte('estepe', (0, ye, ze), 'peca', repouso=(0, 0, 0), item=PECA['roda_aro14'], peca='roda_aro14', **REG['estepe'])
    Vc.parte('motor', (0, 0.26, ZM), 'peca', item=PECA['motor_1_6'], peca='motor_1_6', **REG['motor'])
    Vc.parte('alternador', (-0.22, 0.50, ZM + 0.16), 'peca', item=PECA['alternador'], peca='alternador', **REG['alternador'])
    Vc.parte('radiador', (0, 0.37, 1.905), 'peca', repouso=(90, 0, 0), item=PECA['radiador'], peca='radiador', **REG['radiador'])
    Vc.parte('bateria', (0.30, 0.565, 0.93), 'peca', item=PECA['bateria_12v'], peca='bateria_12v', **REG['bateria'])
    Vc.parte('escapamento', (0, 0.165, -0.5), 'peca', item=PECA['escapamento_curto'], peca='escapamento_curto', **REG['escapamento'])
    Vc.parte('tanque', (0, 0.125, -0.83), 'peca', item=PECA['tanque_45l'], peca='tanque_45l', **REG['tanque'])
    Vc.parte('banco_motorista', (0.37, 0.29, -0.28), 'peca', item=PECA['banco_dianteiro'], peca='banco_dianteiro', **REG['banco_motorista'])
    Vc.parte('banco_passageiro', (-0.37, 0.29, -0.28), 'peca', item=PECA['banco_dianteiro'], peca='banco_dianteiro', **REG['banco_passageiro'])
    Vc.parte('banco_traseiro', (0, 0.30, -1.13), 'peca', item=PECA['banco_traseiro'], peca='banco_traseiro', **REG['banco_traseiro'])
    Vc.parte('volante', (0.37, 0.82, 0.06), 'peca', repouso=(-68, 0, 0), item=PECA['volante'], peca='volante', **REG['volante'])
    Vc.parte('porta_luvas', (-0.375, 0.586, 0.215), 'tampa', eixo='x', abre_graus=-75, peca=None)
    Vc.parte('assoalho_porta_malas', (0, 0.478, -1.585), 'tampa', eixo='x', abre_graus=75, peca=None)
    Vc.parte('quebra_sol_e', (0.38, 1.336, -0.215), 'tampa', eixo='x', abre_graus=-80, peca=None)
    Vc.parte('quebra_sol_d', (-0.38, 1.336, -0.215), 'tampa', eixo='x', abre_graus=-80, peca=None)

    fora, dentro = _carroceria(Vc, _recortes())
    _frisos(Vc, fora)
    p = Vc.base
    _grade(p); _limpadores(p); _cofre(p); _cubos_e_suspensao(p)
    _para_choque(Vc.achar('para_choque_d')['geo'], True); _para_choque(Vc.achar('para_choque_t')['geo'], False)
    tampa = Vc.achar('tampa_porta_malas')['geo']
    _placa_hatch(tampa); _limpador_traseiro(tampa)
    for s, l in ((1, 'e'), (-1, 'd')):
        _farol(Vc.achar(f'farol_{l}')['geo'], s); _lanterna_vertical(Vc.achar(f'lanterna_{l}')['geo'], s)
        _retrovisor(Vc.achar(f'retrovisor_{l}')['geo'], s)
    for no, s in (('porta_de', 1), ('porta_dd', -1)):
        _macaneta(Vc.achar(no)['geo'], s, -0.30, -0.17, chave=True); _porta_dentro(Vc.achar(no)['geo'], s, True)
    for no, s in (('porta_te', 1), ('porta_td', -1)):
        _macaneta(Vc.achar(no)['geo'], s, -1.16, -1.03); _porta_dentro(Vc.achar(no)['geo'], s, False)
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
    _bateria(Vc.achar('bateria')['geo']); _escapamento_curto(Vc.achar('escapamento')['geo']); _tanque(Vc.achar('tanque')['geo']); _bocal(p)
    _banco_dianteiro(Vc.achar('banco_motorista')['geo'], 0.37); _banco_dianteiro(Vc.achar('banco_passageiro')['geo'], -0.37)
    _banco_traseiro(Vc.achar('banco_traseiro')['geo'])
    _painel(Vc, dentro); _forro_e_cabine(Vc, dentro); _porta_malas_hatch(Vc, dentro)
    _fundo_preto(Vc)
    zb = SF.Z_BOCAL
    for no, pos in (('camera_1a_pessoa', (0.37, 1.13, -0.32)), ('assento_motorista', (0.37, 0.48, -0.30)), ('assento_passageiro', (-0.37, 0.48, -0.30)),
                    ('assento_traseiro_e', (0.40, 0.50, -1.12)), ('assento_traseiro_m', (0.0, 0.50, -1.12)), ('assento_traseiro_d', (-0.40, 0.50, -1.12)),
                    ('saida_motorista', (1.35, 0.0, -0.05)), ('saida_passageiro', (-1.35, 0.0, -0.05)), ('saida_traseira_e', (1.35, 0.0, -0.95)),
                    ('saida_traseira_d', (-1.35, 0.0, -0.95)), ('bocal_tanque', (round(SF.x_lado(zb, 1.0) - 0.02, 3), 0.80, zb)),
                    ('saida_escape', (-0.43, 0.19, -2.10)), ('luz_farol_e', (0.58, 0.614, 2.09)), ('luz_farol_d', (-0.58, 0.614, 2.09)),
                    ('luz_freio_e', (0.70, 0.86, SF.ZR - 0.03)), ('luz_freio_d', (-0.70, 0.86, SF.ZR - 0.03)),
                    ('macaco_e', (0.70, 0.22, -0.20)), ('macaco_d', (-0.70, 0.22, -0.20)), ('talha_motor', (0.0, 1.40, ZM))):
        Vc.encaixes.append(dict(no=no, pos=pos, tipo='ponto'))
    SAQ = {
        'porta_malas': [['mochila', 0.30], ['macaco_sanfona', 0.5], ['chave_de_roda', 0.5], ['garrafa_agua', 0.25], ['oleo_motor', 0.2],
                        ['cabos_chupeta', 0.15], ['bola', 0.1], ['sacola_compras', 0.3], ['roupas', 0.25], ['lata_feijao', 0.2]],
        'porta_luvas': [['mapa_cidade', 0.4], ['lanterna', 0.3], ['pilhas', 0.3], ['isqueiro', 0.25], ['oculos_sol', 0.2], ['chave_casa', 0.1], ['frasco_remedio', 0.15]],
        'bolsa': [['garrafa_agua', 0.2], ['salgadinho', 0.2], ['chave_carro', 0.02]],
        'console': [['isqueiro', 0.3], ['pilhas', 0.2]],
        'quebra_sol': [['chave_carro', 0.10]],
        'banco': [['mochila', 0.1], ['roupas', 0.2], ['cadeirinha_bebe', 0.08]],
    }
    Vc.compartimento('porta_malas', 'Porta-malas', (7, 4), 'tampa_porta_malas', saque=SAQ['porta_malas'], tranca=True)
    Vc.compartimento('fundo_porta_malas', 'Fundo do porta-malas', (3, 3), 'assoalho_porta_malas', so_aceita=['roda_aro14'], parte='estepe')
    Vc.compartimento('porta_luvas', 'Porta-luvas', (3, 2), 'porta_luvas', saque=SAQ['porta_luvas'])
    Vc.compartimento('bolsa_porta_de', 'Bolsa da porta do motorista', (3, 1), 'porta_de', saque=SAQ['bolsa'])
    Vc.compartimento('bolsa_porta_dd', 'Bolsa da porta do passageiro', (3, 1), 'porta_dd', saque=SAQ['bolsa'])
    Vc.compartimento('console', 'Console', (2, 1), None, saque=SAQ['console'])
    Vc.compartimento('quebra_sol_e', 'Quebra-sol do motorista', (1, 1), 'quebra_sol_e', saque=SAQ['quebra_sol'])
    Vc.compartimento('quebra_sol_d', 'Quebra-sol do passageiro', (1, 1), 'quebra_sol_d', saque=SAQ['quebra_sol'])
    Vc.compartimento('banco_tras', 'Banco de trás', (8, 4), None, saque=SAQ['banco'], vira_carga_sem='banco_traseiro', carga_sem_banco=[9, 6])


def _lanterna_vertical(q, s):
    """Lanterna em pé na quina: freio vermelho em cima, pisca âmbar no meio, ré branca embaixo, com frisos cromados."""
    def L(m): return m if s > 0 else _mx(m)
    xa, xb, ya, yb = SF.LANTERNA
    C = lambda x0, x1, y0, y1, d0, d1, n=14: _casca_contorno(x0, x1, y0, y1, d0, d1, frente=False, n=n)
    q.add('plastico_preto', L(menos(C(xa + 0.003, xb - 0.003, ya + 0.003, yb - 0.003, -0.004, -0.03), C(xa + 0.009, xb - 0.009, ya + 0.009, yb - 0.009, 0.02, -0.05))))
    q.add('refletor', L(C(xa + 0.005, xb - 0.005, ya + 0.005, yb - 0.005, -0.02, -0.032)))
    q.add('plastico_preto', L(C(xa + 0.009, xb - 0.009, ya + 0.009, yb - 0.009, -0.032, -getattr(SF, 'LANTERNA_FUNDO', 0.08))))
    y1, y2 = ya + 0.075, ya + 0.165
    q.add('lente_re', L(C(xa + 0.007, xb - 0.007, ya + 0.007, y1 - 0.002, -0.002, -0.009)))
    q.add('lente_pisca', L(C(xa + 0.007, xb - 0.007, y1 + 0.002, y2 - 0.002, -0.002, -0.009)))
    q.add('lente_lanterna', L(C(xa + 0.007, xb - 0.007, y2 + 0.002, yb - 0.007, -0.002, -0.009)))
    for y in (y1, y2): q.add('cromado', L(C(xa + 0.007, xb - 0.007, y - 0.002, y + 0.002, 0.0, -0.006)))
    for k in range(6):                                                     # frisos horizontais da lente vermelha
        y = y2 + 0.03 + k * 0.045
        if y + 0.006 > yb - 0.015: break
        q.add('lente_lanterna', L(C(xa + 0.012, xb - 0.012, y, y + 0.006, 0.001, -0.004)))


def _placa_hatch(q):
    z = SF.ZR - 0.004
    q.add('plastico_preto', _cx(-0.215, 0.215, 0.663, 0.812, z - 0.006, z + 0.002))
    q.add('placa', _cham(-0.2, 0.2, 0.670, 0.805, z - 0.010, z - 0.006, 0.003))
    for x in (-0.12, 0.12): q.add('lente_re', _cx(x - 0.02, x + 0.02, 0.814, 0.822, z - 0.012, z - 0.004))   # luz da placa
    zf = SF.z_ponta(0.3, False, k=1.0) - 0.004
    q.add('plastico_preto', _cham(-0.58, 0.58, 0.835, 0.868, zf - 0.008, z + 0.004, 0.004))                # friso preto com a fechadura
    q.add('aco_escuro', _cham(-0.06, 0.06, 0.842, 0.862, z - 0.012, z - 0.004, 0.003))
    c = trimesh.creation.cylinder(radius=0.012, height=0.012, sections=20); c.apply_translation([0, 0.852, z - 0.016]); q.add('cromado', c)
    e = trimesh.creation.cylinder(radius=0.03, height=0.008, sections=32); e.apply_translation([0, 0.92, SF.z_ponta(0.0, False, k=1.0) - 0.02])
    q.add('cromado', e)                                                     # emblema liso


def _limpador_traseiro(q):
    """Limpador do vidro traseiro: eixo embaixo do vidro, braço e palheta deitados na base."""
    zp = SF.ZBL + 0.015; yp = SF.ytop(zp) + 0.006
    q.add('plastico_preto', _cil_y(0.022, yp - 0.01, yp + 0.012, 0.0, zp, 20))
    za = zp + 0.06; ya = SF.ytop(za) + 0.018
    q.add('plastico_preto', tubo([(0.0, yp + 0.012, zp), (0.18, SF.ytop(zp + 0.03) + 0.018, zp + 0.03), (0.36, ya, za)], 0.007, 8))
    q.add('borracha', tubo([(0.06, SF.ytop(zp + 0.035) + 0.01, zp + 0.035), (0.46, SF.ytop(za + 0.015) + 0.01, za + 0.015)], 0.006, 8))


def _escapamento_curto(q):
    cam = suavizar_caminho([(0.0, 0.42, ZM + 0.19), (0.0, 0.30, ZM + 0.26), (-0.02, 0.17, ZM + 0.10), (-0.05, 0.165, 0.6), (-0.05, 0.165, -0.20),
                            (-0.06, 0.165, -0.55), (-0.08, 0.165, -1.45), (-0.15, 0.17, -1.70)], 3)
    q.add('aco_galv', tubo(cam, 0.024, 14))
    q.add('aco_galv', _cham(-0.12, 0.02, 0.135, 0.205, -0.55, -0.20, 0.03))                                   # ressonador
    q.add('aco_galv', _cham(-0.50, -0.10, 0.115, 0.222, -1.96, -1.70, 0.035))                                  # silencioso
    q.add('aco_galv', tubo([(-0.40, 0.17, -1.96), (-0.42, 0.18, -2.03), (-0.43, 0.19, -2.09)], 0.022, 14))
    q.add('ferrugem', _cil_z(0.026, -2.10, -2.07, -0.43, 0.19, 16))
    for x, z in ((-0.05, -0.40), (-0.30, -1.80)): q.add('borracha', _cil_y(0.008, 0.20, 0.232, x, z, 8))


def _porta_malas_hatch(Vc, dentro):
    """Porta-malas curto atrás do banco: assoalho que levanta, poço do estepe e laterais forradas."""
    p = Vc.base; z0, z1 = SF.ZR, -1.585
    ass = Vc.achar('assoalho_porta_malas')['geo']
    ass.add('carpete', inter(dentro, _cx(-0.79, 0.79, 0.458, 0.478, z0, z1)))
    ass.add('plastico_preto', _cx(-0.06, 0.06, 0.478, 0.486, z0 + 0.12, z0 + 0.16))
    p.add('chassi', inter(dentro, _cx(-0.62, 0.62, 0.24, 0.27, z0, -1.36)))                                 # fundo do poço
    p.add('chassi', inter(dentro, _cx(-0.62, 0.62, 0.27, 0.458, -1.375, -1.36)))                            # parede da frente do poço
    for s in (1, -1):
        def L(m): return m if s > 0 else _mx(m)
        p.add('chassi', L(inter(dentro, _cx(0.60, 0.62, 0.27, 0.458, z0, -1.36))))
        p.add('carpete', L(inter(dentro, _cx(0.64, 0.66, 0.478, 0.95, z0 + 0.02, -1.62))))
    p.add('carpete', menos(inter(dentro, _cx(-0.79, 0.79, 0.43, 0.458, z0, -1.36)), _cx(-0.62, 0.62, 0.40, 0.46, -2.2, -1.36)))  # aba do poço
    p.add('aco_escuro', _cx(-0.03, 0.03, 0.64, 0.67, SF.ZR + 0.005, SF.ZR + 0.03))                            # fechadura
