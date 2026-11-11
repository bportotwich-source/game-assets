# Modo Mobiliar: abre um prédio pronto com os móveis dele e deixa arrumar com o
# mouse. Catálogo por cômodo embaixo, peça escolhida à direita, barra em cima.
# Móvel de chão anda numa grade de 25 cm e encosta de costas na parede mais
# perto; item de parede (quadro, relógio, armário aéreo) gruda na face real da
# parede, na altura sugerida, e não aceita janela nem porta. Verde = cabe,
# vermelho = não cabe. Salvar grava o ambientacao.json que o jogo lê.
extends Node3D

const Montador = preload("res://editor/montador.gd")
const Estilo = preload("res://mobiliar/estilo.gd")
const Arquivo = preload("res://mobiliar/arquivo.gd")

const CAM_PREDIO := 1      # paredes, pisos e portas do prédio
const CAM_PECA := 2        # caixa de cada móvel, para clicar nele
const CAM_PORTA := 4       # passagem na frente de cada porta
const CAM_SOLIDO := 8      # móveis que ocupam lugar (tapete e mancha não)
const GRADE := 0.25
const UNDO_MAX := 60
const ALTURA_PISO := 2.3   # o que começa acima disso some (teto, andar de cima, telhado)

const ABAS := [
	["Sala", ["sala"]], ["Quarto", ["quarto"]], ["Cozinha", ["cozinha"]],
	["Banheiro", ["banheiro", "lavanderia"]], ["Escritório", ["escritorio"]],
	["Parede", []], ["Decoração", ["lembrancas"]],
	["Comércio", ["loja", "diner", "padaria", "posto", "concessionaria", "banco", "hotel", "cinema", "correios"]],
	["Serviços", ["saude", "delegacia", "quartel", "igreja", "biblioteca", "escolinha", "estacao"]],
	["Oficina", ["oficina", "deposito", "armazenamento", "armazem", "fabrica", "serraria", "ferrovelho", "energia"]],
	["Abrigo", ["abrigo", "defesa", "barricadas", "comunidade", "agricultura", "agua"]],
	["Rua", ["rua", "cidade", "piscina", "fazenda", "barcos", "concha", "minigolfe", "drivein", "observatorio"]],
	["Fim do mundo", ["sinais"]], ["Itens soltos", []], ["Tudo", []],
]


class Peca:
	var d: Dictionary        # a entrada do ambientacao.json
	var no: Node3D
	var corpo: StaticBody3D
	var caixa: AABB          # no espaço da peça
	var parede := false
	var fino := false        # tapete, mancha, item solto: não ocupa lugar
	var motivo := ""         # por que está mal colocada ("" = certo)


var kits := PackedStringArray()
var kit := ""
var _cat := {}               # id -> entrada do catálogo (mobílias e loot)
var _cenas := {}
var _doc := {}
var _pecas: Array[Peca] = []
var _niveis: Array[float] = [0.0]
var _andar := 0
var _cortar := true
var _sujo := false
var _undo: Array = []

var _predio: Node3D
var _moveis: Node3D
var _partes: Array = []      # peças do prédio: {no, caixa, corpos, parede}
var _excluir: Array[RID] = []

var _sel: Peca
var _fant: Node3D            # peça na mão
var _fant_id := ""
var _fant_d := {}
var _fant_caixa := AABB()
var _fant_ok := false
var _giro := 0.0
var _auto := true            # vira de costas para a parede sozinho
var _alt_extra := 0.0
var _movendo := false
var _com_grade := true
var _revalidar := 0
var _visao_suja := true

var _cam: Camera3D
var _target := Vector3.ZERO
var _yaw := 0.6
var _pitch := 1.0
var _dist := 22.0
var _orbitando := false
var _arrastando := false

var _mat_ok: StandardMaterial3D
var _mat_ruim: StandardMaterial3D
var _mat_sel: StandardMaterial3D
var _mat_prob: StandardMaterial3D

# Interface
var _raiz_ui: Control
var _paineis: Array[Control] = []
var _kit_opt: OptionButton
var _andar_lbl: Label
var _paredes_btn: Button
var _prob_btn: Button
var _estado: Label
var _peca_box: VBoxContainer
var _abas_box: HFlowContainer
var _slots_box: HFlowContainer
var _busca: LineEdit
var _aba := "Sala"
var _slots := {}
var _restaurar_btn: Button

# Miniaturas do catálogo
var _mini_vp: SubViewport
var _mini_cam: Camera3D
var _mini_raiz: Node3D
var _mini_tex := {}
var _mini_fila: Array = []
var _mini_id := ""
var _mini_espera := 0


func _ready() -> void:
	Montador.make_world(self)
	_mat_ok = _overlay(Color(0.3, 1.0, 0.45, 0.4))
	_mat_ruim = _overlay(Color(1.0, 0.25, 0.2, 0.5))
	_mat_sel = _overlay(Color(1.0, 0.7, 0.15, 0.4))
	_mat_prob = _overlay(Color(1.0, 0.2, 0.15, 0.3))
	_cam = Camera3D.new()
	_cam.fov = 55.0
	_cam.far = 800.0
	add_child(_cam)
	_cam.current = true
	_ler_catalogo()
	_fazer_miniaturas()
	_fazer_ui()
	kits = Montador.kit_list()
	for k in kits:
		_kit_opt.add_item(k)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	if kits.size() > 0:
		var i := maxi(kits.find("bangalo"), 0)
		_kit_opt.select(i)
		_abrir(kits[i])


func _overlay(c: Color) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.albedo_color = c
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	return m


func _pintar(n: Node, m: Material) -> void:
	for mi in n.find_children("*", "MeshInstance3D", true, false):
		mi.material_overlay = m


# ---------------------------------------------------------------- catálogo

func _ler_catalogo() -> void:
	for g in ["mobilias", "loot"]:
		var data = Montador.read_json("res://props/%s/catalogo.json" % g)
		if not (data is Dictionary):
			continue
		for it in data.get("itens", []):
			var e: Dictionary = it
			e["grupo"] = g
			e["aba"] = _aba_de(e)
			_cat[e["id"]] = e


func _aba_de(e: Dictionary) -> String:
	if e["grupo"] == "loot":
		return "Itens soltos"
	var c: String = e.get("categoria", "")
	for a in ABAS:
		if c in a[1]:
			return a[0]
	return "Tudo"


func _cena(arquivo: String) -> PackedScene:
	if _cenas.has(arquivo):
		return _cenas[arquivo]
	var ps: PackedScene = null
	if ResourceLoader.exists("res://" + arquivo):
		ps = load("res://" + arquivo)
	_cenas[arquivo] = ps
	return ps


func _nome(id: String) -> String:
	return _cat[id]["nome"] if _cat.has(id) else id


func _e_parede(id: String) -> bool:
	return _cat.has(id) and _cat[id].get("montagem", "floor") == "wall"


static func _caixa_local(raiz: Node3D) -> AABB:
	var box := AABB()
	var primeiro := true
	var inv := raiz.global_transform.affine_inverse()
	for mi in raiz.find_children("*", "MeshInstance3D", true, false):
		if mi.mesh == null:
			continue
		var b: AABB = (inv * mi.global_transform) * mi.get_aabb()
		box = b if primeiro else box.merge(b)
		primeiro = false
	return box


# ---------------------------------------------------------------- prédio

func _abrir(k: String, so_original := false) -> void:
	kit = k
	_soltar()
	_sel = null
	_undo.clear()
	_sujo = false
	if _predio:
		_predio.queue_free()
	if _moveis:
		_moveis.queue_free()
	_pecas.clear()
	_partes.clear()
	_predio = Node3D.new()
	_predio.name = "Predio"
	add_child(_predio)
	_moveis = Node3D.new()
	_moveis.name = "Moveis"
	add_child(_moveis)
	Montador.build_walkable(Montador.kit_layout(k), _predio, k)
	var tudo := AABB()
	var primeiro := true
	for c in _predio.get_children():
		var n: Node3D = c
		var cx: AABB = n.global_transform * _caixa_local(n)
		var corpos: Array[RID] = []
		for b in n.find_children("*", "CollisionObject3D", true, false):
			corpos.append(b.get_rid())
		var porta := n.has_method("interact")
		_partes.append({"no": n, "caixa": cx, "corpos": corpos,
			"parede": cx.size.y >= 1.5 and minf(cx.size.x, cx.size.z) <= 0.8})
		if porta:
			_zona_porta(cx)
		tudo = cx if primeiro else tudo.merge(cx)
		primeiro = false
	_doc = Arquivo.ler(k, so_original)
	_niveis.clear()
	var niv: Dictionary = _doc.get("niveis", {})
	var chaves := niv.keys()
	chaves.sort_custom(func(a, b): return int(a) < int(b))
	for c in chaves:
		_niveis.append(float(niv[c]))
	if _niveis.is_empty():
		_niveis.append(0.0)
	_andar = 0
	for it in _doc.get("itens", []):
		_criar(it)
	_target = tudo.get_center()
	_target.y = _niveis[0]
	_dist = clampf(Vector2(tudo.size.x, tudo.size.z).length() * 0.85, 10.0, 90.0)
	_visao_suja = true
	_revalidar = 3
	_atualizar_topo()
	_painel_peca()
	_restaurar_btn.visible = Arquivo.tem_editado(k)
	_dizer("Clique num móvel para escolher, ou pegue um no catálogo.")


# Faixa livre na frente de cada porta: móvel não pode ficar ali.
func _zona_porta(cx: AABB) -> void:
	var sb := StaticBody3D.new()
	sb.collision_layer = CAM_PORTA
	sb.collision_mask = 0
	var cs := CollisionShape3D.new()
	var cil := CylinderShape3D.new()
	cil.radius = 0.5
	cil.height = 1.6
	cs.shape = cil
	sb.add_child(cs)
	_predio.add_child(sb)
	sb.global_position = Vector3(cx.get_center().x, cx.position.y + 1.0, cx.get_center().z)


func _criar(d: Dictionary) -> Peca:
	var ps := _cena(str(d.get("arquivo", "")))
	if ps == null:
		return null
	var p := Peca.new()
	p.d = d
	p.no = ps.instantiate()
	_moveis.add_child(p.no)
	var pos: Array = d["pos"]
	p.no.position = Vector3(pos[0], pos[1], pos[2])
	p.no.rotation.y = deg_to_rad(float(d.get("rotY", 0.0)))
	p.caixa = _caixa_local(p.no)
	p.parede = _e_parede(str(d["item"]))
	p.fino = d.get("grupo", "") == "loot" or p.caixa.size.y < 0.08
	p.corpo = StaticBody3D.new()
	p.corpo.collision_mask = 0
	var cs := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = p.caixa.size.max(Vector3(0.05, 0.05, 0.05))
	cs.shape = box
	cs.position = p.caixa.get_center()
	p.corpo.add_child(cs)
	p.no.add_child(p.corpo)
	_pecas.append(p)
	_camada(p)
	return p


func _camada(p: Peca) -> void:
	var aqui := int(p.d.get("andar", 0)) == _andar
	p.no.visible = int(p.d.get("andar", 0)) <= _andar
	p.corpo.collision_layer = (CAM_PECA | (0 if p.fino else CAM_SOLIDO)) if aqui else 0


# Esconde o que fica acima do andar e, com as paredes cortadas, as paredes que
# estão entre a câmera e o ponto para onde ela olha. O que some não é clicável.
func _atualizar_visao() -> void:
	_visao_suja = false
	var y0: float = _niveis[_andar]
	var lado := Vector3(sin(_yaw), 0, cos(_yaw))
	_excluir.clear()
	for pt in _partes:
		var cx: AABB = pt["caixa"]
		var vis := cx.position.y < y0 + ALTURA_PISO
		if vis and _cortar and pt["parede"] and cx.end.y > y0 + 1.2:
			vis = (cx.get_center() - _target).dot(lado) < 0.6
		var n: Node3D = pt["no"]
		n.visible = vis
		if not vis:
			_excluir.append_array(pt["corpos"])
	for p in _pecas:
		_camada(p)
		if p.parede and p.no.visible and not _excluir.is_empty():
			# quadro em parede que sumiu some junto
			var c := p.no.global_transform * p.caixa.get_center()
			var n := p.no.global_transform.basis.z
			var h := _raio(c + n * 0.1, c - n * 0.7, CAM_PREDIO)
			if not h.is_empty() and _excluir.has(h["rid"]):
				p.no.visible = false
				p.corpo.collision_layer = 0


# ---------------------------------------------------------------- física

func _raio(a: Vector3, b: Vector3, mask: int, excluir: Array[RID] = []) -> Dictionary:
	var q := PhysicsRayQueryParameters3D.create(a, b, mask)
	q.exclude = excluir
	return get_world_3d().direct_space_state.intersect_ray(q)


func _raio_mouse(mask: int, excluir: Array[RID]) -> Dictionary:
	var mp := get_viewport().get_mouse_position()
	var o := _cam.project_ray_origin(mp)
	return _raio(o, o + _cam.project_ray_normal(mp) * 600.0, mask, excluir)


func _bate(tam: Vector3, xf: Transform3D, mask: int, excluir: Array[RID]) -> bool:
	var q := PhysicsShapeQueryParameters3D.new()
	var box := BoxShape3D.new()
	box.size = tam
	q.shape = box
	q.transform = xf
	q.collision_mask = mask
	q.exclude = excluir
	return not get_world_3d().direct_space_state.intersect_shape(q, 1).is_empty()


func _piso_em(p: Vector3) -> float:
	var y0: float = _niveis[_andar]
	var h := _raio(Vector3(p.x, y0 + 1.0, p.z), Vector3(p.x, y0 - 1.5, p.z), CAM_PREDIO)
	return h["position"].y if not h.is_empty() else y0


# Por que a peça não pode ficar onde está ("" = pode).
func _motivo(caixa: AABB, parede: bool, fino: bool, xf: Transform3D, excluir: Array[RID]) -> String:
	if fino:
		return ""
	var centro := xf * caixa.get_center()
	var giro := Transform3D(xf.basis, centro)
	if parede:
		var n := xf.basis.z
		for u in [Vector2(0.5, 0.5), Vector2(0, 0), Vector2(1, 0), Vector2(0, 1), Vector2(1, 1)]:
			var lx := lerpf(caixa.position.x + 0.03, caixa.end.x - 0.03, u.x)
			var ly := lerpf(caixa.position.y + 0.03, caixa.end.y - 0.03, u.y)
			var pt := xf * Vector3(lx, ly, 0)
			var h := _raio(pt + n * 0.25, pt - n * 0.25, CAM_PREDIO)
			if h.is_empty() or absf(h["position"].distance_to(pt + n * 0.25) - 0.25) > 0.035 or h["normal"].dot(n) < 0.9:
				return "fora da parede, ou em cima de janela ou porta"
		var t := (caixa.size - Vector3(0.04, 0.04, 0.0)).max(Vector3(0.02, 0.02, 0.02))
		giro.origin += n * 0.02
		if _bate(t, giro, CAM_SOLIDO, excluir):
			return "em cima de outra peça"
		return ""
	var tam := (caixa.size - Vector3(0.1, 0.12, 0.1)).max(Vector3(0.05, 0.05, 0.05))
	giro.origin.y += 0.04
	if _bate(tam, giro, CAM_PREDIO, []):
		return "atravessa a parede"
	if _bate(tam, giro, CAM_PORTA, []):
		return "na passagem da porta"
	if _bate(tam, giro, CAM_SOLIDO, excluir):
		return "em cima de outro móvel"
	return ""


func _validar_tudo() -> void:
	var n := 0
	for p in _pecas:
		var ex: Array[RID] = [p.corpo.get_rid()]
		p.motivo = _motivo(p.caixa, p.parede, p.fino, p.no.global_transform, ex)
		if p.motivo != "":
			n += 1
		_pintar(p.no, _mat_sel if p == _sel else (_mat_prob if p.motivo != "" else null))
	_prob_btn.text = "%d com problema" % n
	_prob_btn.visible = n > 0
	if _sel:
		_painel_peca()


# ---------------------------------------------------------------- peça na mão

func _pegar(id: String, d := {}) -> void:
	if not _cat.has(id) and d.is_empty():
		return
	var arq: String = d.get("arquivo", "props/" + str(_cat.get(id, {}).get("arquivo", "")))
	var ps := _cena(arq)
	if ps == null:
		_dizer("Não achei o modelo de %s." % id, false)
		return
	var era_movendo := _movendo
	_soltar(false)
	_movendo = era_movendo
	_escolher(null)
	_fant = ps.instantiate()
	add_child(_fant)
	_fant_caixa = _caixa_local(_fant)
	_fant_id = id
	_fant_d = d.duplicate(true)
	if _fant_d.is_empty():
		_fant_d = {"item": id, "grupo": _cat[id]["grupo"], "arquivo": arq, "comodo": ""}
	_giro = float(d.get("rotY", 0.0))
	_auto = d.is_empty()
	_alt_extra = 0.0
	_fant.visible = false
	_marcar_slot()
	_painel_peca()


func _soltar(cancelar := true) -> void:
	if _fant:
		_fant.queue_free()
		_fant = null
	if _movendo and cancelar:
		_movendo = false
		_desfazer()
	_movendo = false
	_fant_id = ""
	_marcar_slot()
	_painel_peca()


func _fino_id(id: String, caixa: AABB) -> bool:
	return (_cat.has(id) and _cat[id]["grupo"] == "loot") or caixa.size.y < 0.08


func _mover_fantasma() -> void:
	var livre := Input.is_key_pressed(KEY_ALT)
	var hit := _raio_mouse(CAM_PREDIO, _excluir)
	if hit.is_empty():
		_fant.visible = false
		return
	_fant.visible = true
	var y0: float = _niveis[_andar]
	var p: Vector3 = hit["position"]
	var nrm: Vector3 = hit["normal"]
	var na_parede := absf(nrm.y) < 0.3
	var parede := _e_parede(_fant_id)
	var dica := ""
	if parede:
		var alt := float(_cat[_fant_id].get("altura_sugerida_m", 1.4)) + _alt_extra
		var achou := na_parede
		var w := p
		var n := Vector3(nrm.x, 0, nrm.z).normalized()
		if not na_parede:
			# o mouse está no chão: procura a parede mais perto, na altura da peça
			var yc := _piso_em(p) + alt + _fant_caixa.size.y * 0.5
			var melhor := 1.6
			for a in [0.0, 90.0, 180.0, 270.0]:
				var dir := Vector3(sin(deg_to_rad(a)), 0, cos(deg_to_rad(a)))
				var o := Vector3(p.x, yc, p.z)
				var h := _raio(o, o + dir * 1.6, CAM_PREDIO)
				if not h.is_empty() and absf(h["normal"].y) < 0.3 and o.distance_to(h["position"]) < melhor:
					melhor = o.distance_to(h["position"])
					w = h["position"]
					n = Vector3(h["normal"].x, 0, h["normal"].z).normalized()
					achou = true
		if achou:
			var chao := _piso_em(w + n * 0.45)
			var tg := Vector3.UP.cross(n)
			if not livre:
				w += tg * (snappedf(w.dot(tg), 0.05) - w.dot(tg))
			w.y = chao + alt
			# cola na face real da parede na altura do meio da peça
			var meio := w + Vector3.UP * (_fant_caixa.size.y * 0.5)
			var h2 := _raio(meio + n * 0.3, meio - n * 0.3, CAM_PREDIO)
			if not h2.is_empty() and h2["normal"].dot(n) > 0.9:
				w.x = h2["position"].x
				w.z = h2["position"].z
			_fant.global_position = w
			_fant.rotation.y = atan2(n.x, n.z)
			dica = "Na parede, a %s m do chão. Shift + roda muda a altura." % _num(alt)
		else:
			_fant.global_position = p
			_fant.rotation.y = deg_to_rad(_giro)
			_fant_ok = false
			_pintar(_fant, _mat_ruim)
			_dizer("Leve o %s até uma parede." % _nome(_fant_id).to_lower(), false)
			return
	else:
		var fino := _fino_id(_fant_id, _fant_caixa)
		if na_parede or p.y > y0 + 1.5:
			var q := p + Vector3(nrm.x, 0, nrm.z) * 0.3
			p = Vector3(q.x, _piso_em(q), q.z)
		var pos := p
		if _com_grade and not livre:
			pos.x = snappedf(p.x, GRADE)
			pos.z = snappedf(p.z, GRADE)
		var rot := _giro
		var colado := false
		if _auto and not livre and not fino:
			var fundo := -_fant_caixa.position.z
			var melhor := 0.7 + fundo
			var wp := Vector3.ZERO
			var wn := Vector3.ZERO
			var o := pos + Vector3.UP * 0.25
			for a in [0.0, 90.0, 180.0, 270.0]:
				var dir := Vector3(sin(deg_to_rad(a)), 0, cos(deg_to_rad(a)))
				var h := _raio(o, o + dir * (0.7 + fundo), CAM_PREDIO)
				if not h.is_empty() and absf(h["normal"].y) < 0.3 and o.distance_to(h["position"]) < melhor:
					melhor = o.distance_to(h["position"])
					wp = h["position"]
					wn = Vector3(h["normal"].x, 0, h["normal"].z).normalized()
					colado = true
			if colado:
				rot = rad_to_deg(atan2(wn.x, wn.z))
				pos += wn * (fundo + 0.02 - (pos - wp).dot(wn))
				# não entra na parede do lado, no canto
				var tg := Vector3.UP.cross(wn)
				for s in [-1.0, 1.0]:
					var meia: float = (_fant_caixa.end.x if s > 0 else -_fant_caixa.position.x) + 0.02
					var o2 := pos + Vector3.UP * 0.25 + wn * 0.05
					var h := _raio(o2, o2 + tg * s * meia, CAM_PREDIO)
					if not h.is_empty():
						pos -= tg * s * (meia - o2.distance_to(h["position"]))
		_fant.global_position = pos
		_fant.rotation.y = deg_to_rad(rot)
		dica = "Encostado na parede." if colado else ("Sem encaixe." if livre else "Grade de 25 cm.")
	var m := _motivo(_fant_caixa, parede, _fino_id(_fant_id, _fant_caixa), _fant.global_transform, [])
	_fant_ok = m == ""
	_pintar(_fant, _mat_ok if _fant_ok else _mat_ruim)
	if _fant_ok:
		_dizer(dica + " Clique para colocar.", true)
	else:
		_dizer("Não cabe: %s." % m, false)


func _colocar() -> void:
	if _fant == null or not _fant.visible:
		return
	if not _fant_ok:
		return
	if not _movendo:
		_guardar()
	var d := _fant_d.duplicate(true)
	var gp := _fant.global_position
	d["pos"] = [snappedf(gp.x, 0.001), snappedf(gp.y, 0.001), snappedf(gp.z, 0.001)]
	d["rotY"] = snappedf(wrapf(rad_to_deg(_fant.rotation.y), -180.0, 180.0), 0.1)
	d["andar"] = _andar
	var p := _criar(d)
	_mudou()
	if _movendo:
		_movendo = false
		_soltar(false)
		_escolher(p)


# ---------------------------------------------------------------- seleção e edição

func _escolher(p: Peca) -> void:
	if _sel and is_instance_valid(_sel.no):
		_pintar(_sel.no, _mat_prob if _sel.motivo != "" else null)
	_sel = p
	if p:
		_pintar(p.no, _mat_sel)
	_painel_peca()


func _peca_no_mouse() -> Peca:
	var hit := _raio_mouse(CAM_PECA, [])
	if hit.is_empty():
		return null
	for p in _pecas:
		if p.corpo == hit["collider"]:
			return p
	return null


func _tirar(p: Peca) -> void:
	_pecas.erase(p)
	p.no.queue_free()
	if _sel == p:
		_sel = null


func _apagar() -> void:
	if _sel == null:
		return
	_guardar()
	_tirar(_sel)
	_mudou()
	_painel_peca()


func _mover_sel() -> void:
	if _sel == null:
		return
	_guardar()
	var d := _sel.d
	_tirar(_sel)
	_movendo = true
	_pegar(str(d["item"]), d)
	_revalidar = 2


func _duplicar() -> void:
	if _sel == null:
		return
	var d := _sel.d.duplicate(true)
	_pegar(str(d["item"]), d)
	_auto = false


func _girar(graus: float) -> void:
	if _fant:
		if not _e_parede(_fant_id):
			_giro = wrapf((rad_to_deg(_fant.rotation.y) if _auto else _giro) + graus, -180.0, 180.0)
			_auto = false
		return
	if _sel == null or _sel.parede:
		return
	_guardar()
	var centro := _sel.no.global_transform * Vector3(_sel.caixa.get_center().x, 0, _sel.caixa.get_center().z)
	_sel.no.rotate_y(deg_to_rad(graus))
	_sel.no.global_position += centro - _sel.no.global_transform * Vector3(_sel.caixa.get_center().x, 0, _sel.caixa.get_center().z)
	_gravar_pos(_sel)
	_mudou()


func _empurrar(dv: Vector3) -> void:
	if _sel == null:
		return
	_guardar()
	_sel.no.global_position += dv
	_gravar_pos(_sel)
	_mudou()


func _gravar_pos(p: Peca) -> void:
	var gp := p.no.global_position
	p.d["pos"] = [snappedf(gp.x, 0.001), snappedf(gp.y, 0.001), snappedf(gp.z, 0.001)]
	p.d["rotY"] = snappedf(wrapf(rad_to_deg(p.no.rotation.y), -180.0, 180.0), 0.1)


func _itens() -> Array:
	var a := []
	for p in _pecas:
		a.append(p.d.duplicate(true))
	return a


func _guardar() -> void:
	_undo.append(_itens())
	if _undo.size() > UNDO_MAX:
		_undo.pop_front()


func _desfazer() -> void:
	if _undo.is_empty():
		return
	if _fant:
		_movendo = false
		_soltar(false)
	var lista: Array = _undo.pop_back()
	for p in _pecas:
		p.no.queue_free()
	_pecas.clear()
	_sel = null
	for d in lista:
		_criar(d)
	_mudou()
	_painel_peca()


func _mudou() -> void:
	_sujo = true
	_revalidar = 2
	_atualizar_topo()


func _salvar() -> void:
	if _fant:
		_soltar()
	_doc["kit"] = kit
	_doc["itens"] = _itens()
	_doc["editado_a_mao"] = true
	var onde := Arquivo.gravar(kit, _doc)
	if onde == "":
		_dizer("Não consegui gravar o arquivo.", false)
		return
	_sujo = false
	_atualizar_topo()
	_restaurar_btn.visible = Arquivo.tem_editado(kit)
	_dizer("Salvo: %d peças em %s" % [_pecas.size(), onde], true)


# Leva para a face real da parede o que foi posto perto dela: itens de parede
# que ficaram soltos no ar e móveis de costas para a parede com um vão atrás.
# Só mexe se a peça ficar bem colocada depois; o resto continua marcado.
func _encostar_tudo() -> void:
	if _fant:
		_soltar()
	_guardar()
	var feitos := 0
	for p in _pecas:
		if p.fino:
			continue
		var xf := p.no.global_transform
		var n := xf.basis.z
		var ex: Array[RID] = [p.corpo.get_rid()]
		var passo := Vector3.ZERO
		if p.parede:
			var c := xf * Vector3(p.caixa.get_center().x, p.caixa.get_center().y, 0)
			var h := _raio(c + n * 0.3, c - n * 0.6, CAM_PREDIO)
			if h.is_empty() or h["normal"].dot(n) < 0.9:
				continue
			passo = n * (h["position"] - c).dot(n)
		else:
			var fundo := -p.caixa.position.z
			var c := xf * Vector3(p.caixa.get_center().x, 0.25, p.caixa.get_center().z)
			var h := _raio(c, c - n * (fundo + 0.6), CAM_PREDIO)
			if h.is_empty() or h["normal"].dot(n) < 0.95:
				continue
			passo = n * ((h["position"] - c).dot(n) + p.caixa.get_center().z + fundo + 0.02)
		if passo.length() < 0.005:
			continue
		var novo := xf.translated(passo)
		if _motivo(p.caixa, p.parede, p.fino, novo, ex) != "":
			continue
		p.no.global_transform = novo
		_gravar_pos(p)
		feitos += 1
	if feitos == 0:
		_undo.pop_back()
		_dizer("Nada para encostar.")
		return
	_mudou()
	_dizer("%d peças encostadas na parede. Ctrl+Z desfaz." % feitos, true)


func _prox_problema() -> void:
	var ruins: Array[Peca] = []
	for p in _pecas:
		if p.motivo != "":
			ruins.append(p)
	if ruins.is_empty():
		return
	var i := (ruins.find(_sel) + 1) % ruins.size()
	var p := ruins[i]
	if _fant:
		_soltar()
	_andar = int(p.d.get("andar", 0))
	_target = p.no.global_position
	_target.y = _niveis[_andar]
	_dist = 7.0
	_visao_suja = true
	_atualizar_topo()
	_escolher(p)


func _mudar_andar(d: int) -> void:
	var novo := clampi(_andar + d, 0, _niveis.size() - 1)
	if novo == _andar:
		return
	_andar = novo
	_target.y = _niveis[_andar]
	_escolher(null)
	_visao_suja = true
	_atualizar_topo()


# ---------------------------------------------------------------- miniaturas

func _fazer_miniaturas() -> void:
	_mini_vp = SubViewport.new()
	_mini_vp.size = Vector2i(128, 128)
	_mini_vp.own_world_3d = true
	_mini_vp.transparent_bg = true
	_mini_vp.render_target_update_mode = SubViewport.UPDATE_DISABLED
	add_child(_mini_vp)
	var env := Environment.new()
	env.background_mode = Environment.BG_CLEAR_COLOR
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(1, 0.98, 0.94)
	env.ambient_light_energy = 0.7
	var we := WorldEnvironment.new()
	we.environment = env
	_mini_vp.add_child(we)
	var sol := DirectionalLight3D.new()
	sol.rotation_degrees = Vector3(-45, -35, 0)
	_mini_vp.add_child(sol)
	_mini_raiz = Node3D.new()
	_mini_vp.add_child(_mini_raiz)
	_mini_cam = Camera3D.new()
	_mini_cam.fov = 30.0
	_mini_vp.add_child(_mini_cam)


func _passo_miniatura() -> void:
	if _mini_espera > 0:
		_mini_espera -= 1
		if _mini_espera == 0:
			var tex := ImageTexture.create_from_image(_mini_vp.get_texture().get_image())
			_mini_tex[_mini_id] = tex
			if _slots.has(_mini_id):
				_slots[_mini_id].icon = tex
			for c in _mini_raiz.get_children():
				c.queue_free()
		return
	while not _mini_fila.is_empty():
		var id: String = _mini_fila.pop_front()
		if _mini_tex.has(id) or not _cat.has(id):
			continue
		var ps := _cena("props/" + str(_cat[id]["arquivo"]))
		if ps == null:
			continue
		var inst: Node3D = ps.instantiate()
		_mini_raiz.add_child(inst)
		var box := _caixa_local(inst)
		inst.position = -box.get_center()
		var r := maxf(box.size.length() * 0.5, 0.08)
		_mini_cam.position = Vector3(0.75, 0.6, 1.5).normalized() * r * 4.0
		_mini_cam.look_at(Vector3.ZERO)
		_mini_cam.near = r * 0.2
		_mini_vp.render_target_update_mode = SubViewport.UPDATE_ONCE
		_mini_id = id
		_mini_espera = 3
		return


# ---------------------------------------------------------------- interface

func _fazer_ui() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	_raiz_ui = Control.new()
	_raiz_ui.set_anchors_preset(Control.PRESET_FULL_RECT)
	_raiz_ui.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_raiz_ui.theme = Estilo.tema()
	layer.add_child(_raiz_ui)

	# barra de cima
	var topo := PanelContainer.new()
	topo.set_anchors_preset(Control.PRESET_TOP_WIDE)
	topo.add_theme_stylebox_override("panel", _caixa_topo())
	_raiz_ui.add_child(topo)
	_paineis.append(topo)
	var h := HBoxContainer.new()
	h.add_theme_constant_override("separation", 8)
	topo.add_child(h)
	h.add_child(Estilo.titulo("Mobiliar"))
	_kit_opt = OptionButton.new()
	_kit_opt.custom_minimum_size = Vector2(230, 0)
	_kit_opt.focus_mode = Control.FOCUS_NONE
	_kit_opt.item_selected.connect(func(i): _abrir(kits[i]))
	h.add_child(_kit_opt)
	h.add_child(_espaco(10))
	h.add_child(Estilo.rotulo("Andar"))
	h.add_child(_botao("▼", func(): _mudar_andar(-1)))
	_andar_lbl = Label.new()
	_andar_lbl.custom_minimum_size = Vector2(80, 0)
	_andar_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_andar_lbl.add_theme_font_override("font", Estilo.fonte("forte"))
	h.add_child(_andar_lbl)
	h.add_child(_botao("▲", func(): _mudar_andar(1)))
	h.add_child(_espaco(10))
	h.add_child(Estilo.rotulo("Paredes"))
	_paredes_btn = _botao("Cortadas", _trocar_paredes)
	_paredes_btn.custom_minimum_size = Vector2(96, 0)
	h.add_child(_paredes_btn)
	var meio := Control.new()
	meio.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	meio.mouse_filter = Control.MOUSE_FILTER_IGNORE
	h.add_child(meio)
	_prob_btn = _botao("", _prox_problema)
	_prob_btn.add_theme_color_override("font_color", Estilo.FALTA)
	_prob_btn.add_theme_color_override("font_hover_color", Estilo.FALTA)
	_prob_btn.tooltip_text = "Vai para a próxima peça mal colocada"
	h.add_child(_prob_btn)
	var enc := _botao("Encostar tudo", _encostar_tudo)
	enc.tooltip_text = "Cola na parede os quadros que ficaram soltos no ar e fecha o vão atrás dos móveis"
	h.add_child(enc)
	h.add_child(_botao("Desfazer", _desfazer))
	var salvar := _botao("Salvar", _salvar)
	Estilo.principal(salvar)
	h.add_child(salvar)
	h.add_child(_botao("Menu", func(): get_tree().change_scene_to_file("res://menu/menu.tscn")))

	# catálogo embaixo
	var baixo := PanelContainer.new()
	baixo.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	baixo.offset_top = -268
	_raiz_ui.add_child(baixo)
	_paineis.append(baixo)
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 8)
	baixo.add_child(v)
	var linha := HBoxContainer.new()
	linha.add_theme_constant_override("separation", 10)
	v.add_child(linha)
	_abas_box = HFlowContainer.new()
	_abas_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_abas_box.add_theme_constant_override("h_separation", 4)
	_abas_box.add_theme_constant_override("v_separation", 4)
	linha.add_child(_abas_box)
	_busca = LineEdit.new()
	_busca.placeholder_text = "Buscar (ex.: cama, quadro)"
	_busca.custom_minimum_size = Vector2(230, 0)
	_busca.clear_button_enabled = true
	_busca.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	_busca.text_changed.connect(func(_t): _encher_slots())
	linha.add_child(_busca)
	var rol := ScrollContainer.new()
	rol.size_flags_vertical = Control.SIZE_EXPAND_FILL
	rol.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	v.add_child(rol)
	_slots_box = HFlowContainer.new()
	_slots_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_slots_box.add_theme_constant_override("h_separation", 6)
	_slots_box.add_theme_constant_override("v_separation", 6)
	rol.add_child(_slots_box)

	# peça escolhida, à direita
	var lado := PanelContainer.new()
	lado.set_anchors_preset(Control.PRESET_RIGHT_WIDE)
	lado.offset_left = -270
	lado.offset_top = 58
	lado.offset_bottom = -276
	_raiz_ui.add_child(lado)
	_paineis.append(lado)
	var lv := VBoxContainer.new()
	lv.add_theme_constant_override("separation", 10)
	lado.add_child(lv)
	_peca_box = VBoxContainer.new()
	_peca_box.add_theme_constant_override("separation", 8)
	lv.add_child(_peca_box)
	var enche := Control.new()
	enche.size_flags_vertical = Control.SIZE_EXPAND_FILL
	lv.add_child(enche)
	var ajuda := Label.new()
	ajuda.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	ajuda.add_theme_font_size_override("font_size", 13)
	ajuda.add_theme_color_override("font_color", Estilo.APAGADO)
	ajuda.text = "R gira · Delete apaga · Esc solta\nSetas empurram 25 cm (Shift: 5 cm)\nAlt: sem encaixe · G: grade\nBotão direito gira a câmera, o do meio arrasta, a roda aproxima\nPage Up / Down: andar · P: paredes\nCtrl+Z desfaz · Ctrl+S salva"
	lv.add_child(ajuda)
	_restaurar_btn = _botao("Voltar ao original do kit", _restaurar)
	_restaurar_btn.tooltip_text = "Apaga a sua versão salva deste prédio e abre a que veio no kit"
	lv.add_child(_restaurar_btn)

	_estado = Label.new()
	_estado.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	_estado.offset_left = 14
	_estado.offset_top = -304
	_estado.offset_bottom = -276
	_estado.add_theme_font_override("font", Estilo.fonte("forte"))
	_estado.add_theme_font_size_override("font_size", 17)
	_estado.add_theme_color_override("font_outline_color", Color.BLACK)
	_estado.add_theme_constant_override("outline_size", 6)
	_raiz_ui.add_child(_estado)

	for a in ABAS:
		var nome: String = a[0]
		var b := _botao(nome, func(): _busca.text = ""; _aba = nome; _encher_slots())
		b.toggle_mode = true
		b.set_meta("aba", nome)
		_abas_box.add_child(b)
	_encher_slots()


func _caixa_topo() -> StyleBoxFlat:
	var s := Estilo.caixa(Estilo.PAINEL, Estilo.FERRUGEM, 8, 0)
	s.border_width_bottom = 2
	s.set_corner_radius_all(0)
	return s


func _espaco(w: int) -> Control:
	var c := Control.new()
	c.custom_minimum_size = Vector2(w, 0)
	return c


func _botao(texto: String, cb: Callable) -> Button:
	var b := Button.new()
	b.text = texto
	b.pressed.connect(cb)
	b.focus_mode = Control.FOCUS_NONE
	return b


func _encher_slots() -> void:
	for c in _slots_box.get_children():
		c.queue_free()
	_slots.clear()
	_mini_fila.clear()
	var busca := _busca.text.strip_edges().to_lower()
	for b in _abas_box.get_children():
		b.button_pressed = busca == "" and b.get_meta("aba") == _aba
	var ids := []
	for id in _cat:
		var e: Dictionary = _cat[id]
		var entra := false
		if busca != "":
			entra = str(e["nome"]).to_lower().contains(busca) or str(id).contains(busca.replace(" ", "_"))
		elif _aba == "Tudo":
			entra = e["grupo"] == "mobilias"
		elif _aba == "Parede":
			entra = e.get("montagem", "") == "wall"
		else:
			entra = e["aba"] == _aba
		if entra:
			ids.append(id)
	ids.sort_custom(func(a, b): return str(_cat[a]["nome"]).naturalnocasecmp_to(str(_cat[b]["nome"])) < 0)
	for id in ids:
		var e: Dictionary = _cat[id]
		var b := Button.new()
		b.focus_mode = Control.FOCUS_NONE
		b.toggle_mode = true
		b.custom_minimum_size = Vector2(118, 112)
		b.text = e["nome"]
		b.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		b.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
		b.clip_text = true
		b.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
		b.vertical_icon_alignment = VERTICAL_ALIGNMENT_TOP
		b.expand_icon = true
		b.add_theme_constant_override("icon_max_width", 60)
		b.add_theme_font_override("font", Estilo.fonte())
		b.add_theme_font_size_override("font_size", 13)
		b.add_theme_stylebox_override("normal", Estilo.caixa(Estilo.SLOT, Estilo.LINHA, 5))
		var t: Array = e.get("tamanho_m", [0, 0, 0])
		b.tooltip_text = "%s\n%s × %s × %s m (largura × altura × fundo)%s" % [e["nome"], _num(t[0]), _num(t[1]), _num(t[2]),
			"\nVai na parede" if e.get("montagem", "") == "wall" else ""]
		b.pressed.connect(_clicou_slot.bind(id))
		if _mini_tex.has(id):
			b.icon = _mini_tex[id]
		else:
			_mini_fila.append(id)
		_slots_box.add_child(b)
		_slots[id] = b
	_marcar_slot()


func _clicou_slot(id: String) -> void:
	if _fant_id == id and not _movendo:
		_soltar()
	else:
		if _movendo:
			_soltar()
		_pegar(id)


func _marcar_slot() -> void:
	for id in _slots:
		_slots[id].button_pressed = id == _fant_id


func _painel_peca() -> void:
	if _peca_box == null:
		return
	for c in _peca_box.get_children():
		c.queue_free()
	var id := _fant_id
	if id == "" and _sel:
		id = str(_sel.d["item"])
	if id == "":
		_peca_box.add_child(Estilo.rotulo("Peça"))
		var l := Label.new()
		l.text = "Nenhuma peça escolhida."
		l.add_theme_color_override("font_color", Estilo.APAGADO)
		_peca_box.add_child(l)
		return
	_peca_box.add_child(Estilo.rotulo("Colocando" if _fant else "Peça escolhida"))
	var n := Estilo.titulo(_nome(id), 22, Estilo.TEXTO)
	n.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_peca_box.add_child(n)
	var e: Dictionary = _cat.get(id, {})
	var t: Array = e.get("tamanho_m", [0, 0, 0])
	var parede := _e_parede(id)
	var info := Label.new()
	info.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	info.add_theme_font_size_override("font_size", 14)
	info.text = "%s × %s × %s m\n%s" % [_num(t[0]), _num(t[1]), _num(t[2]),
		("Parede, a %s m do chão" % _num(float(e.get("altura_sugerida_m", 1.4)))) if parede else "Chão, encosta na parede"]
	_peca_box.add_child(info)
	if _sel and not _fant and _sel.motivo != "":
		var m := Label.new()
		m.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		m.add_theme_color_override("font_color", Estilo.FALTA)
		m.text = "Mal colocada: %s." % _sel.motivo
		_peca_box.add_child(m)
	var g := HFlowContainer.new()
	g.add_theme_constant_override("h_separation", 6)
	g.add_theme_constant_override("v_separation", 6)
	_peca_box.add_child(g)
	if _fant:
		g.add_child(_botao("Soltar (Esc)", _soltar))
		if not parede:
			g.add_child(_botao("Girar (R)", func(): _girar(90.0)))
	else:
		g.add_child(_botao("Mover", _mover_sel))
		if not parede:
			g.add_child(_botao("Girar (R)", func(): _girar(90.0)))
		g.add_child(_botao("Duplicar", _duplicar))
		g.add_child(_botao("Apagar", _apagar))


func _atualizar_topo() -> void:
	_andar_lbl.text = "Térreo" if _andar == 0 else "%dº andar" % _andar
	_paredes_btn.text = "Cortadas" if _cortar else "Inteiras"
	get_window().title = "Game Assets · Mobiliar %s%s" % [kit, " *" if _sujo else ""]


func _trocar_paredes() -> void:
	_cortar = not _cortar
	_visao_suja = true
	_atualizar_topo()


func _restaurar() -> void:
	if _restaurar_btn.text.begins_with("Voltar"):
		_restaurar_btn.text = "Clique de novo para confirmar"
		return
	_restaurar_btn.text = "Voltar ao original do kit"
	Arquivo.apagar_editado(kit)
	_abrir(kit)


func _dizer(texto: String, bom = null) -> void:
	_estado.text = texto
	_estado.add_theme_color_override("font_color", Estilo.TEXTO if bom == null else (Estilo.OK if bom else Estilo.FALTA))


static func _num(x: float) -> String:
	return ("%.2f" % x).replace(".", ",")


# ---------------------------------------------------------------- câmera e entrada

func _atualizar_cam() -> void:
	_pitch = clampf(_pitch, 0.25, 1.5)
	_dist = clampf(_dist, 2.0, 200.0)
	var dir := Vector3(sin(_yaw) * cos(_pitch), sin(_pitch), cos(_yaw) * cos(_pitch))
	_cam.global_position = _target + dir * _dist
	_cam.look_at(_target)


func _mouse_na_ui() -> bool:
	var mp := get_viewport().get_mouse_position()
	for p in _paineis:
		if p.get_global_rect().has_point(mp):
			return true
	return false


func _process(delta: float) -> void:
	if not (get_viewport().gui_get_focus_owner() is LineEdit) and not Input.is_key_pressed(KEY_CTRL):
		var mv := Vector2(
			float(Input.is_physical_key_pressed(KEY_D)) - float(Input.is_physical_key_pressed(KEY_A)),
			float(Input.is_physical_key_pressed(KEY_W)) - float(Input.is_physical_key_pressed(KEY_S)))
		if mv != Vector2.ZERO:
			var frente := Vector3(-sin(_yaw), 0, -cos(_yaw))
			var dir := Vector3(cos(_yaw), 0, -sin(_yaw))
			_target += (dir * mv.x + frente * mv.y) * delta * _dist * 0.8
			_visao_suja = true
	_atualizar_cam()
	if _visao_suja:
		_atualizar_visao()
	_passo_miniatura()
	if _fant:
		if _mouse_na_ui():
			_fant.visible = false
		else:
			_mover_fantasma()


func _physics_process(_delta: float) -> void:
	if _revalidar > 0:
		_revalidar -= 1
		if _revalidar == 0:
			_validar_tudo()


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		var e: InputEventMouseButton = event
		match e.button_index:
			MOUSE_BUTTON_RIGHT:
				if e.shift_pressed:
					_arrastando = e.pressed
				else:
					_orbitando = e.pressed
					if not e.pressed:
						_arrastando = false
			MOUSE_BUTTON_MIDDLE:
				_arrastando = e.pressed
			MOUSE_BUTTON_WHEEL_UP, MOUSE_BUTTON_WHEEL_DOWN:
				if not e.pressed:
					return
				var cima := e.button_index == MOUSE_BUTTON_WHEEL_UP
				if e.shift_pressed and _fant and _e_parede(_fant_id):
					_alt_extra = clampf(_alt_extra + (0.05 if cima else -0.05), -1.4, 1.5)
				else:
					_dist *= 0.88 if cima else 1.0 / 0.88
			MOUSE_BUTTON_LEFT:
				if not e.pressed:
					return
				get_viewport().gui_release_focus()
				if _fant:
					_colocar()
				else:
					var p := _peca_no_mouse()
					if p and p == _sel:
						_mover_sel()
					else:
						_escolher(p)
	elif event is InputEventMouseMotion:
		if _orbitando:
			_yaw -= event.relative.x * 0.006
			_pitch += event.relative.y * 0.006
			_visao_suja = true
		elif _arrastando:
			var k := _dist * 0.0016
			var frente := Vector3(-sin(_yaw), 0, -cos(_yaw))
			var dir := Vector3(cos(_yaw), 0, -sin(_yaw))
			_target += (-dir * event.relative.x + frente * event.relative.y) * k
			_visao_suja = true
	elif event is InputEventKey and event.pressed:
		_tecla(event)


func _tecla(e: InputEventKey) -> void:
	var k := e.physical_keycode
	if e.ctrl_pressed:
		if e.echo:
			return
		match k:
			KEY_Z: _desfazer()
			KEY_S: _salvar()
			KEY_D: _duplicar()
		return
	if k in [KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT]:
		var passo := 0.05 if e.shift_pressed else GRADE
		# empurra no eixo do mundo mais perto da direção da câmera
		var frente := Vector3(-sin(_yaw), 0, -cos(_yaw))
		frente = Vector3(signf(frente.x), 0, 0) if absf(frente.x) > absf(frente.z) else Vector3(0, 0, signf(frente.z))
		var dir := Vector3(-frente.z, 0, frente.x)
		_empurrar({KEY_UP: frente, KEY_DOWN: -frente, KEY_RIGHT: dir, KEY_LEFT: -dir}[k] * passo)
		return
	if e.echo:
		return
	match k:
		KEY_R, KEY_Q:
			_girar(15.0 if e.shift_pressed else 90.0)
		KEY_E:
			_girar(-15.0 if e.shift_pressed else -90.0)
		KEY_ESCAPE:
			if _fant:
				_soltar()
			else:
				_escolher(null)
		KEY_DELETE, KEY_BACKSPACE, KEY_X:
			if _fant:
				_soltar()
			else:
				_apagar()
		KEY_M:
			_mover_sel()
		KEY_G:
			_com_grade = not _com_grade
			_dizer("Grade de 25 cm ligada." if _com_grade else "Grade desligada.")
		KEY_P:
			_trocar_paredes()
		KEY_PAGEUP:
			_mudar_andar(1)
		KEY_PAGEDOWN:
			_mudar_andar(-1)
		KEY_F:
			_dist = 14.0
