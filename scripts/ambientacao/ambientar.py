"""Ambienta os predios: escolhe os itens de cada comodo e acha uma posicao livre para cada um.

Le os comodos detectados por comodos.py, o tipo de cada comodo em kits.json (o ponto de cada regra cai
dentro do comodo) e as listas de itens de cada tipo (TIPOS, abaixo). Grava kits/<kit>/ambientacao.json.

Regras de posicao:
  parede  encostado numa parede, de costas para ela (frente para dentro do comodo)
  centro  no meio do comodo, com 0,6 m livres em volta
  livre   em qualquer lugar livre (cacos, papeis, manchas, loot no chao)
  muro    pendurado na parede (itens montagem=wall), na altura sugerida
Nenhum item fica na frente de uma porta (faixa de 0,9 m), nem em cima de outro, nem atravessa parede.

Uso: python3 scripts/ambientacao/ambientar.py [kit ...] [--forcar]     (sem argumentos: todos os kits de kits.json)
Kit com "editado_a_mao" no ambientacao.json (salvo pelo Modo Mobiliar) fica como está, a não ser com --forcar.
"""
import json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comodos as CM

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CAT = {}
for g in ('mobilias', 'loot'):
    for i in json.load(open(os.path.join(RAIZ, 'props', g, 'catalogo.json'), encoding='utf-8'))['itens']: CAT[i['id']] = i

# (item, quantidade, regra, probabilidade)
S = [('cacos_vidro', 1, 'livre', 0.35), ('papeis_espalhados', 1, 'livre', 0.35), ('mancha_sangue', 1, 'livre', 0.15), ('cadeira_quebrada', 1, 'livre', 0.12)]
S_PAREDE = [('pichacao_infectados', 1, 'muro', 0.08), ('marca_busca', 1, 'muro', 0.15)]
TIPOS = {
    # ---- casa
    'sala': [('sofa', 1, 'parede', 1), ('poltrona', 1, 'parede', 0.8), ('rack_tv', 1, 'parede', 0.9), ('tv_tubo', 1, 'parede', 0.5), ('tapete_sala', 1, 'centro', 0.8),
             ('estante_livros', 1, 'parede', 0.6), ('abajur', 1, 'parede', 0.6), ('vitrola', 1, 'parede', 0.3), ('vaso_planta_morta', 1, 'parede', 0.6),
             ('quadro_familia', 1, 'muro', 0.8), ('relogio_parede', 1, 'muro', 0.5), ('pilha_livros', 1, 'livre', 0.4), ('porta_retrato', 1, 'livre', 0.4), ('aquecedor', 1, 'parede', 0.3)] + S + S_PAREDE,
    'cozinha': [('geladeira', 1, 'parede', 1), ('fogao', 1, 'parede', 1), ('balcao_pia', 1, 'parede', 1), ('armario_aereo', 1, 'muro', 0.9), ('mesa_jantar', 1, 'centro', 0.7),
                ('fruteira_podre', 1, 'livre', 0.5), ('calendario_parede', 1, 'muro', 0.7), ('lixeira', 1, 'parede', 0.6),
                ('louca_quebrada', 1, 'livre', 0.5), ('lata_feijao', 1, 'livre', 0.4), ('panela', 1, 'livre', 0.4), ('garrafa_agua', 1, 'livre', 0.3)] + S,
    'jantar': [('mesa_jantar', 1, 'centro', 1), ('estante_livros', 1, 'parede', 0.4), ('quadro_familia', 1, 'muro', 0.6), ('relogio_parede', 1, 'muro', 0.5)] + S,
    'quarto': [('cama_casal', 1, 'parede', 1), ('criado_mudo', 2, 'parede', 0.9), ('guarda_roupa', 1, 'parede', 0.9), ('comoda', 1, 'parede', 0.7), ('abajur', 1, 'parede', 0.4),
               ('mala_viagem', 1, 'livre', 0.4), ('roupas', 1, 'livre', 0.5), ('quadro_familia', 1, 'muro', 0.5), ('porta_retrato', 1, 'livre', 0.3)] + S + S_PAREDE,
    'quarto_crianca': [('cama_solteiro', 1, 'parede', 1), ('comoda', 1, 'parede', 0.8), ('berco', 1, 'parede', 0.3), ('ursinho', 1, 'livre', 0.8), ('bola_futebol', 1, 'livre', 0.5),
                       ('desenho_crianca', 1, 'muro', 0.8), ('pilha_livros', 1, 'livre', 0.3)] + S,
    'quarto_solteiro': [('cama_solteiro', 1, 'parede', 1), ('criado_mudo', 1, 'parede', 0.8), ('guarda_roupa', 1, 'parede', 0.6), ('escrivaninha', 1, 'parede', 0.5), ('mala_viagem', 1, 'livre', 0.3), ('roupas', 1, 'livre', 0.4)] + S,
    'banheiro': [('vaso_sanitario', 1, 'parede', 1), ('pia_banheiro', 1, 'parede', 1), ('banheira', 1, 'parede', 0.7), ('armario_banheiro', 1, 'muro', 0.8), ('sabao', 1, 'livre', 0.4),
                 ('frasco_remedio', 1, 'livre', 0.3)] + S,
    'lavabo': [('vaso_sanitario', 1, 'parede', 1), ('pia_banheiro', 1, 'parede', 1), ('armario_banheiro', 1, 'muro', 0.6)],
    'lavanderia': [('maquina_lavar', 1, 'parede', 1), ('caixa_papelao', 1, 'parede', 0.6), ('varal_roupas', 1, 'centro', 0.3), ('sabao', 1, 'livre', 0.5), ('roupas', 1, 'livre', 0.4)] + S,
    'escritorio': [('mesa_escritorio', 1, 'parede', 1), ('arquivo_aco', 1, 'parede', 0.8), ('estante_livros', 1, 'parede', 0.6), ('escrivaninha', 1, 'parede', 0.3),
                   ('calendario_parede', 1, 'muro', 0.6), ('papeis_espalhados', 1, 'livre', 0.7), ('relogio_parede', 1, 'muro', 0.4)] + S + S_PAREDE,
    'corredor': [('vaso_planta_morta', 1, 'parede', 0.3), ('quadro_familia', 1, 'muro', 0.4), ('papeis_espalhados', 1, 'livre', 0.3), ('mancha_sangue', 1, 'livre', 0.1), ('marca_busca', 1, 'muro', 0.2)],
    'garagem': [('bancada_trabalho', 1, 'parede', 1), ('painel_ferramentas', 1, 'muro', 0.8), ('estante_metal', 1, 'parede', 0.8), ('bicicleta', 1, 'parede', 0.5), ('carrinho_mao', 1, 'parede', 0.3),
                ('galao_gasolina', 1, 'livre', 0.4), ('caixa_papelao', 2, 'parede', 0.6), ('pilha_pneus', 1, 'parede', 0.3), ('mangueira_jardim', 1, 'parede', 0.3), ('martelo', 1, 'livre', 0.3)] + S,
    'deposito': [('estante_metal', 2, 'parede', 0.9), ('caixa_papelao', 3, 'parede', 0.9), ('caixa_madeira', 2, 'parede', 0.6), ('tambor_200l', 1, 'parede', 0.4), ('pallet', 1, 'parede', 0.4),
                 ('lata_feijao', 1, 'livre', 0.3)] + S,
    'sotao': [('caixa_papelao', 3, 'parede', 1), ('mala_viagem', 1, 'parede', 0.6), ('cadeira_quebrada', 1, 'livre', 0.5), ('pilha_livros', 1, 'livre', 0.5), ('quadro_familia', 1, 'livre', 0.3),
              ('ursinho', 1, 'livre', 0.2), ('colchao_chao', 1, 'livre', 0.25)],
    'varanda': [('cadeira', 2, 'parede', 0.6), ('vaso_planta_morta', 2, 'parede', 0.6), ('lixeira', 1, 'parede', 0.3), ('bicicleta', 1, 'parede', 0.2)],
    'quintal': [('churrasqueira', 1, 'parede', 0.4), ('varal_roupas', 1, 'centro', 0.4), ('casinha_cachorro', 1, 'parede', 0.4), ('mangueira_jardim', 1, 'parede', 0.4), ('lixeira', 1, 'parede', 0.5),
                ('bola_futebol', 1, 'livre', 0.3), ('carrinho_mao', 1, 'livre', 0.2), ('toco_lenha', 1, 'livre', 0.3), ('vaso_tomate', 1, 'parede', 0.2)],
    # ---- comercio e servicos
    'loja': [('gondola', 3, 'centro', 1), ('balcao_caixa', 1, 'parede', 1), ('geladeira_bebidas', 1, 'parede', 0.8), ('freezer_horizontal', 1, 'parede', 0.5), ('cesta_compras', 2, 'livre', 0.7),
             ('carrinho_compras', 1, 'livre', 0.5), ('cartaz_evacuacao', 1, 'muro', 0.6), ('lata_milho', 1, 'livre', 0.4), ('salgadinho', 1, 'livre', 0.4)] + S + S_PAREDE,
    'mercado': [('gondola', 6, 'centro', 1), ('balcao_caixa', 2, 'parede', 1), ('geladeira_bebidas', 2, 'parede', 1), ('freezer_horizontal', 2, 'parede', 0.8), ('carrinho_compras', 3, 'livre', 0.9),
                ('cesta_compras', 2, 'livre', 0.7), ('cartaz_evacuacao', 1, 'muro', 0.8), ('lixo_espalhado', 1, 'livre', 0.6), ('lata_feijao', 2, 'livre', 0.5), ('pacote_arroz', 1, 'livre', 0.4)] + S + S_PAREDE,
    'padaria_loja': [('prateleira_padaria', 2, 'parede', 1), ('vitrine_tortas', 1, 'parede', 1), ('balcao_caixa', 1, 'parede', 1), ('mesa_booth', 1, 'parede', 0.5), ('banqueta_giratoria', 2, 'livre', 0.4),
                     ('maquina_refrigerante', 1, 'parede', 0.5), ('pao_velho', 1, 'livre', 0.6)] + S + S_PAREDE,
    'padaria_producao': [('masseira', 1, 'parede', 1), ('carrinho_assadeiras', 2, 'parede', 1), ('bancada_trabalho', 1, 'parede', 0.6), ('saco_farinha', 2, 'livre', 0.7), ('estante_metal', 1, 'parede', 0.6),
                         ('relogio_parede', 1, 'muro', 0.4)] + S,
    'diner': [('mesa_booth', 4, 'parede', 1), ('banqueta_giratoria', 4, 'livre', 0.9), ('jukebox', 1, 'parede', 1), ('vitrine_tortas', 1, 'parede', 0.7), ('maquina_refrigerante', 1, 'parede', 0.7),
              ('balcao_caixa', 1, 'parede', 0.6), ('louca_quebrada', 1, 'livre', 0.5)] + S + S_PAREDE,
    'cozinha_comercial': [('chapa_lanchonete', 1, 'parede', 1), ('fritadeira', 1, 'parede', 1), ('geladeira', 1, 'parede', 0.9), ('balcao_pia', 1, 'parede', 0.8), ('estante_metal', 1, 'parede', 0.6),
                          ('fogao', 1, 'parede', 0.4), ('panela', 1, 'livre', 0.5), ('faca_cozinha', 1, 'livre', 0.4)] + S,
    'posto_loja': [('gondola', 2, 'centro', 1), ('balcao_caixa', 1, 'parede', 1), ('geladeira_bebidas', 1, 'parede', 1), ('freezer_sorvete', 1, 'parede', 0.8), ('expositor_oleo', 1, 'parede', 0.8),
                   ('maquina_lanches', 1, 'parede', 0.4), ('mapa_cidade', 1, 'livre', 0.5), ('salgadinho', 1, 'livre', 0.4)] + S + S_PAREDE,
    'oficina': [('carrinho_ferramentas', 1, 'parede', 1), ('bancada_trabalho', 1, 'parede', 1), ('painel_ferramentas', 1, 'muro', 1), ('compressor_ar', 1, 'parede', 0.8), ('pilha_pneus', 1, 'parede', 0.8),
                ('macaco_jacare', 1, 'livre', 0.6), ('tambor_200l', 1, 'parede', 0.6), ('elevador_automotivo', 1, 'centro', 0.5), ('calibrador_pneu', 1, 'parede', 0.3), ('chave_inglesa', 1, 'livre', 0.4)] + S,
    'showroom': [('totem_ofertas', 2, 'livre', 1), ('mesa_escritorio', 2, 'parede', 1), ('carro_abandonado', 1, 'centro', 0.8), ('vaso_planta_morta', 2, 'parede', 0.7),
                 ('banco_espera', 1, 'parede', 0.5), ('papeis_espalhados', 1, 'livre', 0.6)] + S + S_PAREDE,
    'estacionamento': [('carro_abandonado', 3, 'livre', 1), ('carcaca_carro', 1, 'livre', 0.4), ('cone_transito', 2, 'livre', 0.6), ('lixo_espalhado', 1, 'livre', 0.5), ('cavalete_bloqueio', 1, 'livre', 0.3),
                       ('mancha_sangue', 1, 'livre', 0.2), ('pichacao_nao_entre', 1, 'muro', 0.2)],
    'recepcao': [('balcao_recepcao', 1, 'parede', 1), ('banco_espera', 2, 'parede', 0.9), ('vaso_planta_morta', 1, 'parede', 0.6), ('relogio_parede', 1, 'muro', 0.6), ('mural_desaparecidos', 1, 'muro', 0.6),
                 ('maquina_lanches', 1, 'parede', 0.4), ('papeis_espalhados', 1, 'livre', 0.6)] + S + S_PAREDE,
    'quarto_hotel': [('cama_casal', 1, 'parede', 1), ('criado_mudo', 1, 'parede', 1), ('frigobar', 1, 'parede', 0.8), ('comoda', 1, 'parede', 0.6), ('tv_tubo', 1, 'parede', 0.5), ('mala_viagem', 1, 'livre', 0.5),
                     ('abajur', 1, 'parede', 0.4), ('roupas', 1, 'livre', 0.3)] + S,
    'corredor_hotel': [('carrinho_camareira', 1, 'parede', 0.5), ('carrinho_bagagem', 1, 'parede', 0.3), ('vaso_planta_morta', 1, 'parede', 0.4), ('mancha_sangue', 1, 'livre', 0.2), ('marca_busca', 1, 'muro', 0.3)],
    'saguao_estacao': [('banco_espera', 4, 'centro', 1), ('quadro_horarios', 1, 'muro', 1), ('relogio_estacao', 1, 'muro', 0.8), ('maquina_lanches', 1, 'parede', 0.8), ('carrinho_plataforma', 1, 'parede', 0.6),
                       ('balcao_recepcao', 1, 'parede', 0.5), ('mala_viagem', 2, 'livre', 0.6), ('cartaz_evacuacao', 1, 'muro', 0.8), ('orelhao', 1, 'parede', 0.4), ('mural_desaparecidos', 1, 'muro', 0.6)] + S + S_PAREDE,
    'igreja': [('banco_igreja', 8, 'centro', 1), ('altar', 1, 'parede', 1), ('pulpito', 1, 'livre', 0.9), ('castical', 2, 'livre', 0.9), ('harmonio', 1, 'parede', 0.7), ('pia_batismal', 1, 'livre', 0.6),
               ('quadro_hinos', 1, 'muro', 0.8), ('pichacao_igreja', 1, 'muro', 0.6), ('colchao_chao', 2, 'livre', 0.4)] + S,
    'biblioteca': [('estante_biblioteca', 4, 'parede', 1), ('mesa_leitura', 2, 'centro', 1), ('fichario_catalogo', 1, 'parede', 0.9), ('carrinho_livros', 1, 'livre', 0.8),
                   ('globo_terrestre', 1, 'parede', 0.6), ('pilha_livros', 2, 'livre', 0.8), ('livro', 1, 'livre', 0.5), ('mapa_cidade', 1, 'livre', 0.3)] + S,
    'sala_aula': [('carteira_escolar', 8, 'centro', 1), ('mesa_professor', 1, 'parede', 1), ('lousa_escola', 1, 'muro', 1), ('cabide_lancheiras', 1, 'muro', 0.8), ('estufa_lenha', 1, 'parede', 0.5),
                  ('globo_terrestre', 1, 'parede', 0.4), ('desenho_crianca', 2, 'muro', 0.7), ('mochila', 1, 'livre', 0.4)] + S,
    'correios': [('balanca_correio', 1, 'parede', 1), ('carrinho_correspondencia', 1, 'livre', 0.9), ('estante_triagem', 1, 'parede', 0.9), ('caixa_correio_rua', 1, 'parede', 0.5), ('saco_correio', 2, 'livre', 0.8),
                 ('banco_espera', 1, 'parede', 0.5), ('cartaz_evacuacao', 1, 'muro', 0.6)] + S,
    'triagem': [('estante_triagem', 2, 'parede', 1), ('esteira_rolante', 1, 'centro', 0.6), ('carrinho_correspondencia', 2, 'livre', 0.9), ('saco_correio', 3, 'livre', 0.9), ('relogio_ponto', 1, 'muro', 0.6),
                ('paleteira', 1, 'livre', 0.3)] + S,
    'delegacia': [('mesa_maquina_escrever', 2, 'parede', 1), ('arquivo_aco', 2, 'parede', 1), ('quadro_procurados', 1, 'muro', 1), ('banco_espera', 1, 'parede', 0.8), ('armario_armas', 1, 'parede', 0.7),
                  ('papeis_espalhados', 1, 'livre', 0.8), ('mural_desaparecidos', 1, 'muro', 0.5)] + S + S_PAREDE,
    'cela': [('colchao_chao', 1, 'parede', 0.8), ('vaso_sanitario', 1, 'parede', 0.6), ('contagem_dias', 1, 'muro', 0.7), ('mancha_sangue', 1, 'livre', 0.3)],
    'clinica': [('maca', 1, 'parede', 1), ('armario_remedios', 1, 'parede', 1), ('suporte_soro', 1, 'livre', 0.8), ('biombo', 1, 'parede', 0.6), ('balanca_medica', 1, 'parede', 0.6), ('carrinho_emergencia', 1, 'parede', 0.6),
                ('cadeira_rodas', 1, 'livre', 0.5), ('kit_medico', 1, 'livre', 0.3), ('atadura', 1, 'livre', 0.4)] + S,
    'espera': [('banco_espera', 3, 'parede', 1), ('balcao_recepcao', 1, 'parede', 0.7), ('cadeira_rodas', 1, 'livre', 0.5), ('vaso_planta_morta', 1, 'parede', 0.5), ('mural_desaparecidos', 1, 'muro', 0.6),
               ('relogio_parede', 1, 'muro', 0.5), ('maquina_lanches', 1, 'parede', 0.3)] + S + S_PAREDE,
    'banco': [('pedestal_fila', 3, 'centro', 1), ('mesa_escritorio', 2, 'parede', 1), ('banco_espera', 1, 'parede', 0.7), ('arquivo_aco', 1, 'parede', 0.6), ('vaso_planta_morta', 1, 'parede', 0.5),
              ('papeis_espalhados', 1, 'livre', 0.8), ('relogio_parede', 1, 'muro', 0.5)] + S + S_PAREDE,
    'cofre': [('cofres_aluguel', 1, 'muro', 1), ('caixa_madeira', 1, 'parede', 0.4), ('papeis_espalhados', 1, 'livre', 0.6)],
    'quartel': [('armario_bombeiro', 2, 'parede', 1), ('carretel_mangueira', 1, 'parede', 1), ('extintor', 2, 'livre', 0.8), ('bancada_trabalho', 1, 'parede', 0.5), ('estante_metal', 1, 'parede', 0.6),
                ('quadro_tarefas', 1, 'muro', 0.5), ('pe_de_cabra', 1, 'livre', 0.3), ('machado', 1, 'livre', 0.3)] + S,
    'alojamento': [('beliche', 3, 'parede', 1), ('armario_vestiario', 2, 'parede', 0.9), ('mala_viagem', 1, 'livre', 0.4), ('roupas', 1, 'livre', 0.5), ('relogio_parede', 1, 'muro', 0.4)] + S,
    'refeitorio': [('mesa_jantar', 2, 'centro', 1), ('geladeira', 1, 'parede', 0.8), ('fogao', 1, 'parede', 0.7), ('balcao_pia', 1, 'parede', 0.7), ('tv_tubo', 1, 'parede', 0.4)] + S,
    'vestiario': [('armario_vestiario', 3, 'parede', 1), ('banco_praca', 1, 'centro', 0.3), ('roupas', 1, 'livre', 0.5), ('sabao', 1, 'livre', 0.4)] + S,
    'cinema_sala': [('poltronas_cinema', 8, 'centro', 1), ('lixo_espalhado', 1, 'livre', 0.7), ('mancha_sangue', 1, 'livre', 0.2)],
    'cinema_foyer': [('carrinho_pipoca', 1, 'parede', 1), ('balcao_caixa', 1, 'parede', 0.9), ('maquina_refrigerante', 1, 'parede', 0.8), ('banco_espera', 1, 'parede', 0.6), ('maquina_lanches', 1, 'parede', 0.4),
                     ('cartaz_evacuacao', 1, 'muro', 0.6)] + S + S_PAREDE,
    'projecao': [('projetor_filme', 1, 'parede', 1), ('caixa_papelao', 2, 'parede', 0.7), ('estante_metal', 1, 'parede', 0.6)],
    'galpao': [('porta_pallet', 2, 'parede', 1), ('paleteira', 1, 'livre', 0.9), ('empilhadeira', 1, 'livre', 0.6), ('pallet', 3, 'livre', 0.9), ('caixa_madeira', 3, 'livre', 0.8), ('tambor_200l', 2, 'parede', 0.7),
               ('relogio_ponto', 1, 'muro', 0.4), ('estante_metal', 2, 'parede', 0.6)] + S,
    'fabrica': [('torno_mecanico', 2, 'centro', 1), ('esteira_rolante', 1, 'centro', 0.9), ('bancada_trabalho', 2, 'parede', 1), ('painel_ferramentas', 1, 'muro', 0.9), ('relogio_ponto', 1, 'muro', 0.9),
                ('carrinho_ferramentas', 1, 'parede', 0.8), ('compressor_ar', 1, 'parede', 0.6), ('tambor_200l', 2, 'parede', 0.7), ('paleteira', 1, 'livre', 0.5), ('pallet', 2, 'livre', 0.6), ('gerador', 1, 'parede', 0.4)] + S,
    'serraria': [('serra_fita', 1, 'centro', 1), ('pilha_tabuas', 2, 'parede', 1), ('pilha_toras', 1, 'livre', 0.9), ('cavalete_serra', 2, 'livre', 0.9), ('bancada_trabalho', 1, 'parede', 0.7),
                 ('painel_ferramentas', 1, 'muro', 0.7), ('serrote', 1, 'livre', 0.5), ('lenha', 1, 'livre', 0.5)] + S,
    'celeiro': [('fardo_feno', 5, 'parede', 1), ('carrinho_mao', 1, 'livre', 0.9), ('tarro_leite', 2, 'parede', 0.8), ('saco_racao', 2, 'livre', 0.9), ('cocho', 1, 'parede', 0.7), ('painel_ferramentas', 1, 'muro', 0.5),
                ('enxada', 1, 'livre', 0.5), ('pa', 1, 'livre', 0.4), ('saco_sementes', 1, 'livre', 0.5)],
    'fazenda_patio': [('galinheiro', 1, 'parede', 0.9), ('espantalho', 1, 'livre', 0.8), ('bomba_agua_manual', 1, 'livre', 0.8), ('cocho', 1, 'livre', 0.6), ('fardo_feno', 2, 'livre', 0.6), ('carrinho_mao', 1, 'livre', 0.5),
                      ('canteiro_horta', 1, 'livre', 0.4), ('toco_lenha', 1, 'livre', 0.4)],
    'ferro_velho': [('carcaca_carro', 3, 'livre', 1), ('pilha_calotas', 2, 'livre', 1), ('pilha_pneus', 2, 'livre', 1), ('pilha_sucata', 3, 'livre', 1), ('tambor_200l', 2, 'livre', 0.7), ('macaco_jacare', 1, 'livre', 0.5),
                    ('peca_motor', 1, 'livre', 0.5), ('chapa_metal', 1, 'livre', 0.5)],
    'patio': [('lixeira', 1, 'parede', 0.6), ('lixo_espalhado', 1, 'livre', 0.6), ('carro_abandonado', 1, 'livre', 0.3), ('cone_transito', 2, 'livre', 0.4), ('banco_praca', 1, 'parede', 0.3), ('cavalete_bloqueio', 1, 'livre', 0.2)],
    'praca': [('banco_praca', 3, 'livre', 1), ('lixeira', 2, 'livre', 0.9), ('balanco', 1, 'livre', 0.5), ('carrinho_bebe', 1, 'livre', 0.4), ('bicicleta', 1, 'livre', 0.4), ('lixo_espalhado', 1, 'livre', 0.5),
              ('mural_desaparecidos', 1, 'livre', 0.2), ('barraca_camping', 1, 'livre', 0.4), ('fogueira', 1, 'livre', 0.3)],
    'casa_barcos': [('canoa', 2, 'parede', 1), ('remo', 2, 'livre', 0.9), ('boia_salva_vidas', 2, 'muro', 1), ('colete_salva_vidas', 2, 'livre', 0.8), ('bancada_trabalho', 1, 'parede', 0.5), ('tambor_200l', 1, 'parede', 0.4),
                    ('painel_ferramentas', 1, 'muro', 0.4)],
    'observatorio': [('telescopio', 1, 'centro', 1), ('mapa_estrelas', 2, 'muro', 1), ('mesa_escritorio', 1, 'parede', 0.8), ('estante_livros', 1, 'parede', 0.7), ('globo_terrestre', 1, 'parede', 0.5),
                     ('pilha_livros', 1, 'livre', 0.5), ('papeis_espalhados', 1, 'livre', 0.5)] + S,
    'piscina': [('espreguicadeira', 4, 'parede', 1), ('cadeira_salva_vidas', 1, 'livre', 0.9), ('guarda_sol', 2, 'livre', 0.9), ('boia_piscina', 1, 'livre', 0.7), ('placa_regras_piscina', 1, 'muro', 0.8),
                ('boia_salva_vidas', 1, 'muro', 0.7), ('lixeira', 1, 'parede', 0.5)],
    'skate': [('skate', 2, 'livre', 1), ('banco_praca', 2, 'livre', 0.8), ('cone_transito', 2, 'livre', 0.6), ('lixeira', 1, 'livre', 0.6), ('bicicleta', 1, 'livre', 0.4), ('lixo_espalhado', 1, 'livre', 0.5)],
    'minigolfe': [('bandeira_buraco', 4, 'livre', 1), ('taco_golfe', 2, 'livre', 1), ('banco_praca', 1, 'livre', 0.6), ('lixeira', 1, 'livre', 0.6), ('guarda_sol', 1, 'livre', 0.3)],
    'concha': [('cadeira_dobravel', 10, 'centro', 1), ('caixa_som', 2, 'livre', 1), ('microfone_pedestal', 1, 'livre', 1), ('estante_partitura', 3, 'livre', 0.9), ('lixo_espalhado', 1, 'livre', 0.5)],
    'drivein': [('poste_som_drivein', 6, 'livre', 1), ('carro_abandonado', 2, 'livre', 0.9), ('lixo_espalhado', 1, 'livre', 0.6), ('carrinho_pipoca', 1, 'livre', 0.4), ('cone_transito', 1, 'livre', 0.4)],
    'trailer': [('cama_solteiro', 1, 'parede', 0.8), ('fogareiro', 1, 'parede', 0.6), ('mesa_jantar', 1, 'centro', 0.3), ('roupas', 1, 'livre', 0.5), ('lata_sardinha', 1, 'livre', 0.4), ('garrafa_vidro', 1, 'livre', 0.4)] + S,
    'caixa_dagua': [('bomba_agua_manual', 1, 'livre', 0.8), ('tambor_200l', 2, 'parede', 0.8), ('coletor_chuva', 1, 'livre', 0.5), ('galao_agua', 2, 'livre', 0.7), ('painel_ferramentas', 1, 'muro', 0.4)],
    'palco_bastidores': [('caixa_som', 2, 'parede', 0.9), ('estante_partitura', 2, 'parede', 0.7), ('caixa_papelao', 2, 'parede', 0.7), ('cadeira_dobravel', 3, 'livre', 0.7), ('microfone_pedestal', 1, 'livre', 0.5)],
    'galeria': [('banco_praca', 2, 'centro', 0.8), ('vaso_planta_morta', 2, 'parede', 0.8), ('lixeira', 2, 'parede', 0.8), ('orelhao', 1, 'parede', 0.4), ('maquina_lanches', 1, 'parede', 0.5), ('mural_desaparecidos', 1, 'muro', 0.6)] + S + S_PAREDE,
    'arquivo': [('arquivo_aco', 4, 'parede', 1), ('estante_metal', 1, 'parede', 0.7), ('caixa_papelao', 2, 'parede', 0.8), ('papeis_espalhados', 2, 'livre', 0.9), ('fichario_catalogo', 1, 'parede', 0.4)] + S,
    'vazio': [],
}


def _rot(rotY):
    t = math.radians(rotY); return np.array([[math.cos(t), math.sin(t)], [-math.sin(t), math.cos(t)]])   # (x,z) local -> mundo


class Comodo:
    def __init__(s, res, an, rid):
        s.res, s.an = res, an; s.dentro = an['rotulo'] == rid
        s.ocup = np.zeros_like(s.dentro)
        # faixa de 0,9 m na frente das portas deste comodo
        por = an['porta']; viz = np.zeros_like(por)
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)): viz |= np.roll(s.dentro, (dx, dz), (0, 1)) & por
        s.reserva = np.zeros_like(por); ii = np.argwhere(viz); r = int(0.9 / CM.CEL)
        for a, b in ii: s.reserva[max(0, a - r):a + r + 1, max(0, b - r):b + r + 1] = True
        s.reserva &= s.dentro
        s.muros = []   # (ix, iz, dir) celulas de borda com parede: dir = normal para dentro do comodo

        nx, nz = s.dentro.shape
        for a, b in np.argwhere(s.dentro):
            for (dx, dz), rot in (((-1, 0), 90), ((1, 0), -90), ((0, -1), 0), ((0, 1), 180)):
                u, v = a + dx, b + dz
                fora = not (0 <= u < nx and 0 <= v < nz) or not s.dentro[u, v]
                if fora and not (0 <= u < nx and 0 <= v < nz and por[u, v]): s.muros.append((a, b, rot))

    def celulas(s, cx, cz, w, d, rotY, folga=0.0):
        R = _rot(rotY); hx, hz = w / 2 + folga, d / 2 + folga
        cant = np.array([[-hx, -hz], [hx, -hz], [hx, hz], [-hx, hz]]) @ R.T + [cx, cz]
        x0, z0 = cant.min(0); x1, z1 = cant.max(0); res = s.res
        i0, i1 = int(math.floor((x0 - res['x0']) / CM.CEL)), int(math.floor((x1 - res['x0'] - 1e-6) / CM.CEL))
        k0, k1 = int(math.floor((z0 - res['z0']) / CM.CEL)), int(math.floor((z1 - res['z0'] - 1e-6) / CM.CEL))
        return i0, i1, k0, k1

    def cabe(s, cx, cz, w, d, rotY, folga=0.05, reserva=True, ocup=True):
        i0, i1, k0, k1 = s.celulas(cx, cz, w, d, rotY, -folga if folga < 0 else 0.0)
        nx, nz = s.dentro.shape
        if i0 < 0 or k0 < 0 or i1 >= nx or k1 >= nz: return False
        b = (slice(i0, i1 + 1), slice(k0, k1 + 1))
        if not s.dentro[b].all() or (ocup and s.ocup[b].any()): return False
        if reserva and s.reserva[b].any(): return False
        return True

    def marca(s, cx, cz, w, d, rotY):
        i0, i1, k0, k1 = s.celulas(cx, cz, w, d, rotY); s.ocup[i0:i1 + 1, k0:k1 + 1] = True


def _pos_celula(res, a, b): return res['xs'][a], res['zs'][b]


def colocar(com, it, regra, rng, y):
    w, h, d = it['tamanho_m']; res = com.res
    if regra == 'muro' or it['montagem'] == 'wall':
        cand = list(com.muros); rng.shuffle(cand)
        for a, b, rot in cand[:400]:
            x, z = _pos_celula(res, a, b); n = _rot(rot) @ np.array([0, 1.0])
            px, pz = x - n[0] * CM.CEL / 2, z - n[1] * CM.CEL / 2            # na face da parede
            if com.reserva[a, b]: continue
            ok = True
            for t in np.linspace(-w / 2, w / 2, max(2, int(w / CM.CEL) + 1)):
                q = _rot(rot) @ np.array([t, 0.0]); u = int((px + q[0] + n[0] * 0.1 - res['x0']) / CM.CEL); v = int((pz + q[1] + n[1] * 0.1 - res['z0']) / CM.CEL)
                if not (0 <= u < com.dentro.shape[0] and 0 <= v < com.dentro.shape[1]) or not com.dentro[u, v] or com.reserva[u, v]: ok = False; break
            if not ok or any(abs(px - m[0]) + abs(pz - m[1]) < max(w, 0.6) for m in com.paredes_usadas): continue
            com.paredes_usadas.append((px, pz))
            return [round(px, 3), round(y + it.get('altura_sugerida_m', 1.4), 3), round(pz, 3)], rot
        return None
    if regra == 'parede':
        cand = list(com.muros); rng.shuffle(cand)
        for a, b, rot in cand[:600]:
            x, z = _pos_celula(res, a, b); n = _rot(rot) @ np.array([0, 1.0])
            px, pz = x - n[0] * CM.CEL / 2 + n[0] * (d / 2 + 0.03), z - n[1] * CM.CEL / 2 + n[1] * (d / 2 + 0.03)
            if com.cabe(px, pz, w, d, rot):
                com.marca(px, pz, w, d, rot); return [round(px, 3), round(y, 3), round(pz, 3)], rot
        return None
    cel = np.argwhere(com.dentro & ~com.ocup & ~com.reserva)
    if not len(cel): return None
    if regra == 'centro':
        c = cel.mean(0); ordem = np.argsort(((cel - c) ** 2).sum(1) + rng.uniform(0, 4, len(cel)))
        folga = 0.6
    else:
        ordem = rng.permutation(len(cel)); folga = 0.1
    for k in ordem[:500]:
        a, b = cel[k]; x, z = _pos_celula(res, a, b)
        rot = int(rng.choice([0, 90, 180, -90])) if regra == 'livre' else (0 if (com.dentro.sum(1) > 0).sum() <= (com.dentro.sum(0) > 0).sum() else 90)
        if com.cabe(x, z, w + 2 * folga, d + 2 * folga, rot):
            com.marca(x, z, w + (2 * folga if regra == 'centro' else 0), d + (2 * folga if regra == 'centro' else 0), rot)
            return [round(x, 3), round(y, 3), round(z, 3)], rot
    return None


# Para os kits que ja trazem os moveis na geometria (kits 55 a 61): nada de movel, so sinais do fim e loot solto.
SO_SINAIS = S + S_PAREDE + [('lixo_espalhado', 1, 'livre', 0.3), ('louca_quebrada', 1, 'livre', 0.15), ('roupas', 1, 'livre', 0.25), ('lata_feijao', 1, 'livre', 0.25),
                            ('garrafa_agua', 1, 'livre', 0.2), ('frasco_remedio', 1, 'livre', 0.12), ('pilha_livros', 1, 'livre', 0.15), ('mochila', 1, 'livre', 0.06),
                            ('lanterna', 1, 'livre', 0.05), ('vela_fosforos', 1, 'livre', 0.08), ('bilhete', 1, 'livre', 0.08), ('salgadinho', 1, 'livre', 0.12)]
SO_SINAIS_FORA = [('lixo_espalhado', 1, 'livre', 0.5), ('mancha_sangue', 1, 'livre', 0.12), ('papeis_espalhados', 1, 'livre', 0.3), ('cacos_vidro', 1, 'livre', 0.2)]


# ---- Modo "mobiliado" (kits.json: "mobiliado": true): casa montada como casa de verdade, cada cômodo com o
# conjunto completo de móveis e decoração na parede, sem tralha jogada no chão (cacos, papéis, sangue, latas).
# O saque continua nas gavetas e armários (o jogo sorteia o de cada um).
MOBILIADO = {
    'sala': [('sofa', 1, 'parede', 1), ('poltrona', 2, 'parede', 1), ('rack_tv', 1, 'parede', 1), ('tv_tubo', 1, 'parede', 0.9), ('tapete_sala', 1, 'centro', 1),
             ('estante_livros', 1, 'parede', 1), ('abajur', 1, 'parede', 0.9), ('vitrola', 1, 'parede', 0.4), ('vaso_planta_morta', 1, 'parede', 0.8), ('aquecedor', 1, 'parede', 0.3),
             ('quadro_familia', 2, 'muro', 1), ('relogio_parede', 1, 'muro', 0.8)],
    'cozinha': [('geladeira', 1, 'parede', 1), ('fogao', 1, 'parede', 1), ('balcao_pia', 2, 'parede', 1), ('armario_aereo', 2, 'muro', 1), ('mesa_jantar', 1, 'centro', 0.8),
                ('lixeira', 1, 'parede', 0.8), ('calendario_parede', 1, 'muro', 0.9), ('relogio_parede', 1, 'muro', 0.4)],
    'jantar': [('mesa_jantar', 1, 'centro', 1), ('estante_livros', 1, 'parede', 0.7), ('aquecedor', 1, 'parede', 0.3), ('vaso_planta_morta', 1, 'parede', 0.7), ('tapete_sala', 1, 'centro', 0.4),
               ('quadro_familia', 2, 'muro', 1), ('relogio_parede', 1, 'muro', 0.6)],
    'quarto': [('cama_casal', 1, 'parede', 1), ('criado_mudo', 2, 'parede', 1), ('guarda_roupa', 1, 'parede', 1), ('comoda', 1, 'parede', 1), ('abajur', 1, 'parede', 0.8),
               ('poltrona', 1, 'parede', 0.4), ('tapete_sala', 1, 'centro', 0.5), ('vaso_planta_morta', 1, 'parede', 0.3), ('quadro_familia', 2, 'muro', 1)],
    'quarto_crianca': [('cama_solteiro', 1, 'parede', 1), ('criado_mudo', 1, 'parede', 1), ('comoda', 1, 'parede', 1), ('guarda_roupa', 1, 'parede', 0.8), ('estante_livros', 1, 'parede', 0.6),
                       ('berco', 1, 'parede', 0.2), ('tapete_sala', 1, 'centro', 0.6), ('desenho_crianca', 2, 'muro', 1), ('quadro_familia', 1, 'muro', 0.4)],
    'quarto_solteiro': [('cama_solteiro', 1, 'parede', 1), ('criado_mudo', 1, 'parede', 1), ('guarda_roupa', 1, 'parede', 1), ('escrivaninha', 1, 'parede', 0.8), ('comoda', 1, 'parede', 0.5),
                        ('abajur', 1, 'parede', 0.5), ('quadro_familia', 1, 'muro', 0.7)],
    'banheiro': [('vaso_sanitario', 1, 'parede', 1), ('pia_banheiro', 1, 'parede', 1), ('banheira', 1, 'parede', 0.8), ('armario_banheiro', 1, 'muro', 1)],
    'lavabo': [('vaso_sanitario', 1, 'parede', 1), ('pia_banheiro', 1, 'parede', 1), ('armario_banheiro', 1, 'muro', 0.8)],
    'lavanderia': [('maquina_lavar', 1, 'parede', 1), ('estante_metal', 1, 'parede', 0.7), ('caixa_papelao', 1, 'parede', 0.5), ('varal_roupas', 1, 'centro', 0.4), ('calendario_parede', 1, 'muro', 0.3)],
    'escritorio': [('mesa_escritorio', 1, 'parede', 1), ('estante_livros', 2, 'parede', 1), ('arquivo_aco', 1, 'parede', 0.7), ('poltrona', 1, 'parede', 0.6), ('abajur', 1, 'parede', 0.5),
                   ('globo_terrestre', 1, 'parede', 0.3), ('quadro_familia', 1, 'muro', 0.7), ('calendario_parede', 1, 'muro', 0.6), ('relogio_parede', 1, 'muro', 0.5)],
    'corredor': [('vaso_planta_morta', 1, 'parede', 0.6), ('aquecedor', 1, 'parede', 0.3), ('quadro_familia', 2, 'muro', 0.9), ('relogio_parede', 1, 'muro', 0.4)],
    'garagem': [('bancada_trabalho', 1, 'parede', 1), ('painel_ferramentas', 1, 'muro', 1), ('estante_metal', 2, 'parede', 1), ('bicicleta', 1, 'parede', 0.6), ('carrinho_mao', 1, 'parede', 0.4),
                ('caixa_papelao', 2, 'parede', 0.8), ('pilha_pneus', 1, 'parede', 0.4), ('mangueira_jardim', 1, 'parede', 0.5), ('caixa_ferramentas', 1, 'parede', 0.6)],
    'deposito': [('estante_metal', 2, 'parede', 1), ('caixa_papelao', 3, 'parede', 1), ('caixa_madeira', 1, 'parede', 0.6), ('mala_viagem', 1, 'parede', 0.4)],
    'sotao': [('caixa_papelao', 3, 'parede', 1), ('mala_viagem', 2, 'parede', 0.8), ('comoda', 1, 'parede', 0.5), ('poltrona', 1, 'parede', 0.4), ('estante_livros', 1, 'parede', 0.4)],
    'varanda': [('cadeira', 2, 'parede', 1), ('vaso_planta_morta', 2, 'parede', 0.8), ('banco_praca', 1, 'parede', 0.3)],
}
# Fora do modo mobiliado ficam estes; no mobiliado saem (é a tralha jogada que o Bruno não quer na casa normal).
TRALHA = {e[0] for e in S} | {'lixo_espalhado', 'louca_quebrada', 'fruteira_podre', 'pichacao_infectados', 'pichacao_nao_entre'}


# Sala grande (planta aberta, sem cozinha separada): ganha a cozinha e a mesa de jantar num canto.
SALA_INTEGRADA = [('geladeira', 1, 'parede', 1), ('fogao', 1, 'parede', 1), ('balcao_pia', 2, 'parede', 1), ('armario_aereo', 2, 'muro', 0.9), ('mesa_jantar', 1, 'centro', 1)]


def lista_mobiliada(tipo, area=0.0, tem_cozinha=True):
    """Cômodo da casa: o conjunto completo. Outros (loja, clínica...): a lista normal sem a tralha e sem loot no chão."""
    if tipo in MOBILIADO:
        return list(MOBILIADO[tipo]) + (SALA_INTEGRADA if tipo == 'sala' and area > 35 and not tem_cozinha else [])
    fica = []
    for e in TIPOS[tipo]:
        if e[0] in TRALHA or e[0] not in CAT:
            continue
        if e[2] == 'livre' and CAT[e[0]]['grupo'] == 'loot':
            continue
        fica.append(e if e[0] != 'marca_busca' else (e[0], e[1], e[2], e[3] * 0.4))
    return fica


SEQ_CASA_TERREO = ['sala', 'cozinha', 'jantar', 'lavanderia', 'escritorio', 'deposito']
SEQ_CASA_CIMA = ['quarto', 'quarto_crianca', 'quarto_solteiro', 'escritorio', 'quarto_solteiro', 'deposito']
SEQS = {'apto': ['sala', 'quarto', 'cozinha', 'quarto_crianca', 'quarto_solteiro', 'escritorio', 'deposito'], 'terreo': SEQ_CASA_TERREO, 'cima': SEQ_CASA_CIMA,
        'casa_terrea': ['sala', 'quarto', 'cozinha', 'quarto_crianca', 'jantar', 'quarto_solteiro', 'lavanderia', 'deposito']}


def rotular(res, cfg):
    """Tipo automatico de cada comodo: pequeno = banheiro, estreito = corredor, de fora = patio; o resto
    pela ordem de tamanho, com a sequencia do perfil (casa ou comercial) e do andar."""
    perfil = cfg.get('perfil', 'comercial'); n_and = len(res['andares']); tipos = {}
    for an in res['andares']:
        a = an['andar']; acfg = dict(cfg)
        for k, v in cfg.get('andares', {}).items():
            if k == str(a) or (k.endswith('+') and a >= int(k[:-1])): acfg.update(v)
        grupos = {}
        for c in an['comodos']:
            cel = np.argwhere(an['rotulo'] == c['id']); w = (np.ptp(cel[:, 0]) + 1) * CM.CEL; d = (np.ptp(cel[:, 1]) + 1) * CM.CEL
            externo = cel[:, 0].min() <= 1 or cel[:, 1].min() <= 1 or cel[:, 0].max() >= res['nx'] - 2 or cel[:, 1].max() >= res['nz'] - 2
            piso = c.get('piso', '')
            if piso.startswith('roof') or '_roof' in piso: tipos[(a, c['id'])] = acfg.get('telhado', 'vazio'); continue
            if externo: tipos[(a, c['id'])] = acfg.get('externo', 'patio'); continue
            if 'porch' in piso or 'deck' in piso or 'stoop' in piso: tipos[(a, c['id'])] = acfg.get('varanda', 'varanda' if perfil == 'casa' else 'patio'); continue
            if perfil == 'casa' and 'garage' in piso and c['area'] >= 8: tipos[(a, c['id'])] = 'garagem'; continue
            if c['area'] < 2.0: tipos[(a, c['id'])] = 'vazio'; continue
            if any(t in piso for t in ('bath', 'wet')) and c['area'] <= 7.5: tipos[(a, c['id'])] = 'banheiro' if perfil == 'casa' else acfg.get('pequeno', 'lavabo'); continue
            if min(w, d) <= 2.3 and max(w, d) / max(min(w, d), 0.1) >= 2.2 and c['area'] < 30: tipos[(a, c['id'])] = acfg.get('estreito', 'corredor'); continue
            if c['area'] <= acfg.get('pequeno_m2', 5.5): tipos[(a, c['id'])] = acfg.get('pequeno', 'banheiro' if perfil == 'casa' else 'lavabo'); continue
            g = 0
            for k, (g0, g1) in enumerate(cfg.get('casas_x', [])):
                if g0 <= c['centro'][0] < g1: g = k
            for k, (g0, g1) in enumerate(cfg.get('casas_z', [])):
                if g0 <= c['centro'][1] < g1: g = k
            grupos.setdefault(g, []).append(c)
        for g, cs in grupos.items():
            cs.sort(key=lambda c: -c['area'])
            molhado = [c for c in cs if any(t in c.get('piso', '') for t in ('bath', 'kitchen', 'wet'))]
            tem_cozinha = False
            if perfil == 'casa' and 'tipo' not in acfg and not (a == n_and - 1 and cfg.get('sotao')):
                for c in molhado:
                    if c['area'] <= 7.5: tipos[(a, c['id'])] = 'banheiro'
                    elif not tem_cozinha and a == cfg.get('andar_social', 0) or (not tem_cozinha and acfg.get('seq') in ('apto', 'casa_terrea')): tipos[(a, c['id'])] = 'cozinha'; tem_cozinha = True
                    elif c['area'] <= 12: tipos[(a, c['id'])] = 'lavanderia' if a == cfg.get('andar_social', 0) else 'banheiro'
                    else: continue
                cs = [c for c in cs if (a, c['id']) not in tipos]
            if 'tipo' in acfg: seq = [acfg['tipo']]
            elif perfil == 'casa' and 'seq' in acfg and 'principal' not in acfg: seq = SEQS.get(acfg['seq'], acfg['seq']) if isinstance(acfg['seq'], str) else acfg['seq']
            elif perfil == 'casa':
                seq = ['sotao'] if (a == n_and - 1 and cfg.get('sotao')) else (SEQ_CASA_TERREO if a == cfg.get('andar_social', 0) else SEQ_CASA_CIMA)
            else: seq = [acfg.get('principal', 'deposito')] + list(acfg.get('seq', ['escritorio', 'deposito']))
            if tem_cozinha: seq = [t for t in seq if t != 'cozinha'] or ['sala']
            for i, c in enumerate(cs): tipos[(a, c['id'])] = seq[min(i, len(seq) - 1)]
    return tipos


CADEIRAS = {'mesa_jantar': 4, 'mesa_leitura': 4, 'mesa_escritorio': 1, 'mesa_professor': 1, 'escrivaninha': 1, 'mesa_maquina_escrever': 1}


def cadeiras(com, mesa, pos, rot, n, rng):
    """Cadeiras em volta da mesa, viradas para ela (de frente, de tras e nas cabeceiras)."""
    w, h, d = mesa['tamanho_m']; cad = CAT['cadeira']; cw, _, cd = cad['tamanho_m']; out = []
    lados = [(0, d / 2 + 0.25, 180), (0, -d / 2 - 0.25, 0), (w / 2 + 0.25, 0, -90), (-w / 2 - 0.25, 0, 90)]
    if n == 1: lados = [(0, d / 2 + 0.35, 180)]
    if n >= 4 and w >= 1.4: lados = [(-w / 4, d / 2 + 0.25, 180), (w / 4, d / 2 + 0.25, 180), (-w / 4, -d / 2 - 0.25, 0), (w / 4, -d / 2 - 0.25, 0)]
    R = _rot(rot)
    for lx, lz, r in lados[:n]:
        q = R @ np.array([lx, lz]); x, z = pos[0] + q[0], pos[2] + q[1]; rr = rot + r + int(rng.integers(-8, 9))
        if com.cabe(x, z, cw, cd, rr, ocup=False, reserva=False):
            com.marca(x, z, cw, cd, rr); out.append(([round(x, 3), pos[1], round(z, 3)], rr))
    return out


def ambientar(kit, cfg, semente=0):
    res = CM.analisar(os.path.join(RAIZ, 'kits', kit)); rng = np.random.default_rng(abs(hash(kit)) % 2 ** 31 + semente)
    regras = cfg.get('comodos', []); tipos = rotular(res, cfg)
    saida, resumo = [], []
    for an in res['andares']:
        if an['andar'] in cfg.get('ignorar_andares', []): continue
        for c in an['comodos']:
            tipo = None
            for r in regras:
                if r.get('andar', an['andar']) != an['andar']: continue
                u = int((r['ponto'][0] - res['x0']) / CM.CEL); v = int((r['ponto'][1] - res['z0']) / CM.CEL)
                if 0 <= u < res['nx'] and 0 <= v < res['nz'] and an['rotulo'][u, v] == c['id']: tipo = r['tipo']; break
            if tipo is None: tipo = tipos[(an['andar'], c['id'])]
            com = Comodo(res, an, c['id']); com.paredes_usadas = []
            if cfg.get('ja_mobiliado'):            # kit que ja vem com os moveis na geometria: so os sinais do fim e o loot
                lista = [] if tipo == 'vazio' else (list(SO_SINAIS_FORA) if tipo in ('patio', 'quintal', 'estacionamento', 'varanda') else list(SO_SINAIS))
            elif cfg.get('mobiliado'):
                lista = lista_mobiliada(tipo, c['area'], 'cozinha' in tipos.values() or any(r.get('tipo') == 'cozinha' for r in regras))
            else:
                lista = list(TIPOS[tipo])
            lista += [tuple(e) for e in cfg.get('extras', {}).get(tipo, [])]
            n_ok = 0
            for item, n, regra, prob in sorted(lista, key=lambda e: -(CAT[e[0]]['tamanho_m'][0] * CAT[e[0]]['tamanho_m'][2]) if e[0] in CAT else 0):
                if item not in CAT: print('  item desconhecido', item); continue
                # No mobiliado o cômodo de casa leva o conjunto certo (2 criados-mudos, não 5), sem crescer com a área.
                fixo = cfg.get('mobiliado') and tipo in MOBILIADO
                reps = n if (n == 1 or fixo) else int(round(n * min(3.0, max(1.0, c['area'] / 20.0))))
                for _ in range(reps):
                    if rng.random() > prob: continue
                    r = colocar(com, CAT[item], regra, rng, an['y'])
                    if r is None: continue
                    pos, rot = r; n_ok += 1
                    saida.append(dict(item=item, grupo=CAT[item]['grupo'], arquivo=f"props/{CAT[item]['arquivo']}", pos=pos, rotY=rot, andar=an['andar'], comodo=tipo))
                    if item in CADEIRAS:
                        for p2, r2 in cadeiras(com, CAT[item], pos, rot, CADEIRAS[item], rng):
                            n_ok += 1; saida.append(dict(item='cadeira', grupo='mobilias', arquivo=f"props/{CAT['cadeira']['arquivo']}", pos=p2, rotY=r2, andar=an['andar'], comodo=tipo))
            resumo.append(dict(andar=an['andar'], comodo=c['id'], tipo=tipo, area_m2=c['area'], centro=[float(v) for v in c['centro']], itens=n_ok))
    return res, saida, resumo


def main(kits):
    cfgs = json.load(open(os.path.join(os.path.dirname(__file__), 'kits.json'), encoding='utf-8'))
    forcar = '--forcar' in kits; kits = [k for k in kits if k != '--forcar']
    for k in kits or [k for k in cfgs if not k.startswith('_')]:
        arq = os.path.join(RAIZ, 'kits', k, 'ambientacao.json')
        # arrumado a mão no Modo Mobiliar do GameAssets.exe: não sorteia por cima (só com --forcar)
        if not forcar and os.path.exists(arq) and json.load(open(arq, encoding='utf-8')).get('editado_a_mao'):
            print(f'{k}: arrumado a mão, mantido (use --forcar para sortear de novo)'); continue
        res, itens, resumo = ambientar(k, cfgs[k])
        out = dict(kit=k, gerado_por='scripts/ambientacao/ambientar.py', convencao='pos em metros no espaço do prédio (mesmo do building_layout.json); rotY em graus; '
                   'itens de parede (montagem wall) têm o pivô na face de trás, já na altura sugerida', niveis={a['andar']: a['y'] for a in res['andares']}, comodos=resumo, itens=itens)
        json.dump(out, open(os.path.join(RAIZ, 'kits', k, 'ambientacao.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f'{k}: {len(resumo)} cômodos, {len(itens)} itens')


if __name__ == '__main__':
    main(sys.argv[1:])
