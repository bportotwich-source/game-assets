# Recomeço, marco M0 (fundação): o mapa de teste com 5 kits em ruínas, o
# sobrevivente e as 3 vistas. Ainda não há zumbis, saque nem necessidades:
# isso começa no M1. Ver docs/plano-jogo-sobrevivencia.md.
extends Node3D

const Predio = preload("res://jogo/mundo/predio.gd")
const Ruinas = preload("res://jogo/mundo/ruinas.gd")
const Ruas = preload("res://jogo/mundo/ruas.gd")
const Sobrevivente = preload("res://jogo/personagem/sobrevivente.gd")
const Vistas = preload("res://jogo/cameras/vistas.gd")
const Natureza = preload("res://jogo/mundo/natureza.gd")

const DIST_LOD := 220.0

var mapa := {}
var dados := {}
var predios := []
var sobrevivente
var vistas
var _hud: Label
var _fps: Label
var _mira: Label
var _cartao: PanelContainer
var _cartao_txt: Label
var _pausa: Control
var _grade: MeshInstance3D
var _cursor: MeshInstance3D
var _girando := false


func _ready() -> void:
	mapa = _ler_json("res://jogo/dados/mapa_teste.json")
	dados = _ler_json("res://jogo/dados/predios.json")
	_ambiente()
	Ruas.montar(self, mapa)
	_montar_predios()
	_espalhar_lixo_rua()
	var nx: Array = mapa["comprimento_x"]
	var nz: Array = mapa["comprimento_z"]
	Natureza.espalhar(self, AABB(Vector3(nx[0], 0, nz[0]), Vector3(nx[1] - nx[0], 0, nz[1] - nz[0])), _livre, _fresta, int(mapa.get("semente_natureza", 7)))

	sobrevivente = Sobrevivente.new()
	sobrevivente.name = "Sobrevivente"
	add_child(sobrevivente)
	var ini: Dictionary = mapa["inicio"]
	sobrevivente.global_position = Vector3(ini["pos"][0], ini["pos"][1], ini["pos"][2])
	sobrevivente.rotation.y = deg_to_rad(float(ini["olhando_graus"]))

	vistas = Vistas.new()
	vistas.name = "Vistas"
	vistas.sobrevivente = sobrevivente
	var lx: Array = mapa["comprimento_x"]
	var lz: Array = mapa["comprimento_z"]
	vistas.limites = AABB(Vector3(lx[0], 0, lz[0]), Vector3(lx[1] - lx[0], 0, lz[1] - lz[0]))
	add_child(vistas)
	vistas.vista_mudou.connect(_vista_mudou)

	_criar_grade()
	_criar_hud()
	_vista_mudou(vistas.vista)


func _ler_json(path: String) -> Dictionary:
	var f := FileAccess.open(path, FileAccess.READ)
	return JSON.parse_string(f.get_as_text()) if f else {}


# ---------------------------------------------------------------- mundo

func _ambiente() -> void:
	var ceu_mat := ProceduralSkyMaterial.new()
	# Céu de fim de mundo: pálido, meio amarelado, sem azul forte.
	ceu_mat.sky_top_color = Color(0.46, 0.53, 0.6)
	ceu_mat.sky_horizon_color = Color(0.78, 0.74, 0.66)
	ceu_mat.ground_horizon_color = Color(0.55, 0.52, 0.47)
	ceu_mat.ground_bottom_color = Color(0.3, 0.29, 0.27)
	var ceu := Sky.new()
	ceu.sky_material = ceu_mat
	var env := Environment.new()
	env.background_mode = Environment.BG_SKY
	env.sky = ceu
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.9, 0.87, 0.82)
	env.ambient_light_energy = 0.5
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.ssao_enabled = true
	env.fog_enabled = true
	env.fog_light_color = Color(0.72, 0.7, 0.64)
	env.fog_density = 0.004
	env.fog_sky_affect = 0.3
	env.adjustment_enabled = true
	env.adjustment_saturation = 0.8
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)

	var sol := DirectionalLight3D.new()
	sol.name = "Sol"
	sol.rotation_degrees = Vector3(-48, -38, 0)
	sol.light_energy = 1.05
	sol.light_color = Color(1.0, 0.95, 0.86)
	sol.shadow_enabled = true
	sol.directional_shadow_max_distance = 140.0
	add_child(sol)


# Coloca cada quadra a partir da esquina, com a frente do prédio na calçada.
func _montar_predios() -> void:
	var meia: float = mapa["rua_largura"] * 0.5 + mapa["calcada"]
	var recuo: float = mapa["recuo"]
	var vao: float = mapa["vao_entre_predios"]
	for nome_quadra in mapa["quadras"]:
		var norte: bool = nome_quadra.begins_with("norte")
		var leste: bool = nome_quadra.ends_with("leste")
		var x_borda := meia + recuo     # distância da esquina já ocupada
		for item in mapa["quadras"][nome_quadra]:
			var p = Predio.new()
			p.dados = dados.get(item["kit"], {})
			p.montar(item["kit"], float(item.get("ruina", 0.0)), int(item.get("semente", 1)))
			# Ao norte a frente (+Z do kit) já olha para a rua; ao sul gira 180°.
			var cx: AABB = p.caixa
			var largura := cx.size.x
			var gira := 0.0 if norte else PI
			# Bordas em X depois do giro: norte mantém, sul espelha.
			var x0 := cx.position.x if norte else -cx.end.x
			var x_ini := x_borda if leste else -(x_borda + largura)
			p.rotation.y = gira
			p.position.x = x_ini - x0
			if norte:
				p.position.z = -(meia + recuo) - cx.end.z
			else:
				p.position.z = (meia + recuo) + cx.end.z
			add_child(p)
			Ruinas.espalhar_entulho(p, float(item.get("ruina", 0.0)), _rng(int(item.get("semente", 1)) + 7))
			p.aplicar_lod(DIST_LOD)
			predios.append(p)
			x_borda += largura + vao


# Ponto de terreno: fora das ruas e calçadas e longe dos prédios (margem em m).
func _livre(x: float, z: float, margem: float) -> bool:
	var borda: float = mapa["rua_largura"] * 0.5 + mapa["calcada"] + 0.3
	if absf(z) < borda + margem * 0.5 or absf(x) < borda + margem * 0.5:
		return false
	for p in predios:
		var cx: AABB = p.global_transform * p.caixa
		if x > cx.position.x - margem and x < cx.end.x + margem and z > cx.position.z - margem and z < cx.end.z + margem:
			return false
	return true


# Fresta onde nasce mato: beira do asfalto junto ao meio-fio e beira de fora da calçada.
func _fresta(x: float, z: float) -> bool:
	var meia: float = mapa["rua_largura"] * 0.5
	var fora: float = meia + mapa["calcada"]
	var junto := func(v: float) -> bool:
		var a := absf(v)
		return (a > meia - 0.4 and a < meia - 0.05) or (a > fora + 0.05 and a < fora + 0.5)
	var ok: bool = (junto.call(z) and absf(x) > fora) or (junto.call(x) and absf(z) > fora)
	if not ok:
		return false
	for p in predios:
		var cx: AABB = p.global_transform * p.caixa
		if x > cx.position.x - 0.3 and x < cx.end.x + 0.3 and z > cx.position.z - 0.3 and z < cx.end.z + 0.3:
			return false
	return true


func _rng(s: int) -> RandomNumberGenerator:
	var r := RandomNumberGenerator.new()
	r.seed = s
	return r


func _espalhar_lixo_rua() -> void:
	var rng := _rng(99)
	var itens := ["pilha_sucata", "caixa_papelao", "lixeira", "tambor_200l", "pallet", "carrinho_compras", "garrafa_vidro", "galao_gasolina", "tabua", "mala_viagem"]
	var meia: float = mapa["rua_largura"] * 0.5
	for i in 26:
		var nome: String = itens[rng.randi() % itens.size()]
		var pos: Vector3
		if rng.randf() < 0.6:
			pos = Vector3(rng.randf_range(-60, 60), 0.0, rng.randf_range(-meia + 0.5, meia - 0.5))
		else:
			pos = Vector3(rng.randf_range(-meia + 0.5, meia - 0.5), 0.0, rng.randf_range(-50, 50))
		if pos.length() < 6.0:
			continue
		var cena := Ruinas.prop(nome)
		if cena == null:
			continue
		var inst: Node3D = cena.instantiate()
		inst.position = pos
		inst.rotation.y = rng.randf() * TAU
		add_child(inst)
		# Colisão simples (convexa) para o lixo maior não ser atravessado.
		for mi in inst.find_children("*", "MeshInstance3D", true, false):
			if mi.mesh and mi.mesh.get_aabb().size.y > 0.3:
				var sb := StaticBody3D.new()
				var cs := CollisionShape3D.new()
				cs.shape = mi.mesh.create_convex_shape()
				sb.add_child(cs)
				mi.add_child(sb)


# Grade de 2 m do modo prefeito, num plano logo acima das calçadas.
func _criar_grade() -> void:
	var lx: Array = mapa["comprimento_x"]
	var lz: Array = mapa["comprimento_z"]
	_grade = MeshInstance3D.new()
	_grade.name = "Grade2m"
	var pm := PlaneMesh.new()
	pm.size = Vector2(lx[1] - lx[0], lz[1] - lz[0])
	_grade.mesh = pm
	_grade.position = Vector3((lx[0] + lx[1]) * 0.5, 0.17, (lz[0] + lz[1]) * 0.5)
	_grade.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var gm := ShaderMaterial.new()
	gm.shader = preload("res://jogo/mundo/grade.gdshader")
	_grade.material_override = gm
	_grade.visible = false
	add_child(_grade)

	_cursor = MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = Vector3(2.0, 0.04, 2.0)
	_cursor.mesh = bm
	var m := StandardMaterial3D.new()
	m.albedo_color = Color(1.0, 0.8, 0.25, 0.45)
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.no_depth_test = true
	_cursor.material_override = m
	_cursor.visible = false
	add_child(_cursor)


# ---------------------------------------------------------------- entrada

func _unhandled_input(event: InputEvent) -> void:
	if _pausa.visible:
		return
	var cima: bool = vistas.vista == vistas.CIMA
	if event is InputEventKey and event.pressed and not event.echo:
		match event.physical_keycode:
			KEY_ESCAPE:
				_pausar(true)
				return
			KEY_V:
				vistas.alternar_pe()
				return
			KEY_TAB:
				vistas.alternar_cima()
				return
			KEY_E:
				if not cima:
					_interagir()
				return
			KEY_SPACE:
				if cima:
					vistas.centralizar()
				return
	if cima:
		_entrada_cima(event)
	else:
		if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
			sobrevivente.olhar(event.relative)
		elif event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
			if Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
				Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
			else:
				_interagir()


func _entrada_cima(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		match event.button_index:
			MOUSE_BUTTON_WHEEL_UP:
				vistas.zoom_cima(0.9)
			MOUSE_BUTTON_WHEEL_DOWN:
				vistas.zoom_cima(1.1)
			MOUSE_BUTTON_MIDDLE, MOUSE_BUTTON_RIGHT:
				_girando = event.pressed
			MOUSE_BUTTON_LEFT:
				if event.pressed:
					_selecionar(event.position)
	elif event is InputEventMouseMotion and _girando:
		vistas.girar_cima(-event.relative.x * 0.006)


func _process(delta: float) -> void:
	_fps.text = "%d fps" % Engine.get_frames_per_second()
	if vistas.vista != vistas.CIMA:
		return
	var d := Vector2.ZERO
	if Input.is_physical_key_pressed(KEY_W) or Input.is_physical_key_pressed(KEY_UP):
		d.y -= 1
	if Input.is_physical_key_pressed(KEY_S) or Input.is_physical_key_pressed(KEY_DOWN):
		d.y += 1
	if Input.is_physical_key_pressed(KEY_A) or Input.is_physical_key_pressed(KEY_LEFT):
		d.x -= 1
	if Input.is_physical_key_pressed(KEY_D) or Input.is_physical_key_pressed(KEY_RIGHT):
		d.x += 1
	if d != Vector2.ZERO:
		vistas.mover_cima(d.normalized(), delta)
	if Input.is_physical_key_pressed(KEY_Q):
		vistas.girar_cima(1.6 * delta)
	if Input.is_physical_key_pressed(KEY_E):
		vistas.girar_cima(-1.6 * delta)
	_grade.material_override.set_shader_parameter("centro", vistas.foco)
	_grade.material_override.set_shader_parameter("raio", vistas.cima_dist * 1.4)
	_atualizar_cursor()


func _atualizar_cursor() -> void:
	var hit: Dictionary = vistas.raio_mouse(get_viewport().get_mouse_position())
	if hit.is_empty():
		_cursor.visible = false
		return
	var p: Vector3 = hit.position
	_cursor.visible = true
	_cursor.global_position = Vector3(floorf(p.x / 2.0) * 2.0 + 1.0, p.y + 0.03, floorf(p.z / 2.0) * 2.0 + 1.0)


func _interagir() -> void:
	var hit: Dictionary = vistas.raio_centro(2.5)
	if hit.is_empty():
		return
	if hit.position.distance_to(sobrevivente.cabeca.global_position) > 3.0:
		return
	var n: Node = hit.collider
	while n and not n.has_method("interact"):
		n = n.get_parent()
	if n:
		n.interact()


func _selecionar(pos_tela: Vector2) -> void:
	var hit: Dictionary = vistas.raio_mouse(pos_tela)
	var n: Node = hit.get("collider")
	while n and not (n is Predio):
		n = n.get_parent()
	if n == null:
		_cartao.visible = false
		return
	var d: Dictionary = n.dados
	var t := "%s\n" % d.get("nome", n.kit)
	t += "%s\n\n" % d.get("funcao", "")
	t += "Saque: %s\n" % ", ".join(d.get("saque", []))
	t += "Cabem: %d moradores%s\n" % [int(d.get("capacidade", 0)), "" if d.get("ocupavel", false) else " (não dá para morar)"]
	t += "Estado: %d peças de telhado faltando\n" % n.pecas_removidas.size()
	var rep: Dictionary = d.get("reparo", {})
	var partes := []
	for k in rep:
		partes.append("%d %s" % [int(rep[k]), k])
	t += "Reparo por peça: %s" % ", ".join(partes)
	_cartao_txt.text = t
	_cartao.visible = true


# ---------------------------------------------------------------- interface

func _criar_hud() -> void:
	var camada := CanvasLayer.new()
	add_child(camada)
	_hud = _rotulo(Vector2(16, 12))
	camada.add_child(_hud)
	_fps = _rotulo(Vector2(0, 12))
	_fps.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	_fps.position = Vector2(-90, 12)
	camada.add_child(_fps)
	_mira = Label.new()
	_mira.text = "+"
	_mira.set_anchors_preset(Control.PRESET_CENTER)
	_mira.add_theme_color_override("font_outline_color", Color.BLACK)
	_mira.add_theme_constant_override("outline_size", 4)
	camada.add_child(_mira)

	_cartao = PanelContainer.new()
	_cartao.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	_cartao.position = Vector2(-380, 48)
	_cartao.custom_minimum_size = Vector2(360, 0)
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.1, 0.1, 0.09, 0.85)
	sb.set_corner_radius_all(6)
	sb.set_content_margin_all(14)
	_cartao.add_theme_stylebox_override("panel", sb)
	_cartao_txt = Label.new()
	_cartao_txt.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_cartao_txt.custom_minimum_size = Vector2(330, 0)
	_cartao.add_child(_cartao_txt)
	_cartao.visible = false
	camada.add_child(_cartao)

	_pausa = _criar_pausa()
	camada.add_child(_pausa)


func _rotulo(pos: Vector2) -> Label:
	var l := Label.new()
	l.position = pos
	l.add_theme_color_override("font_outline_color", Color.BLACK)
	l.add_theme_constant_override("outline_size", 6)
	return l


func _criar_pausa() -> Control:
	var fundo := ColorRect.new()
	fundo.color = Color(0, 0, 0, 0.55)
	fundo.set_anchors_preset(Control.PRESET_FULL_RECT)
	fundo.process_mode = Node.PROCESS_MODE_ALWAYS
	var c := CenterContainer.new()
	c.set_anchors_preset(Control.PRESET_FULL_RECT)
	fundo.add_child(c)
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 14)
	c.add_child(v)
	var t := Label.new()
	t.text = "Recomeço (pausa)"
	t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	t.add_theme_font_size_override("font_size", 34)
	v.add_child(t)
	v.add_child(_botao("Continuar", func(): _pausar(false)))
	v.add_child(_botao("Voltar ao menu", func():
		get_tree().paused = false
		get_tree().change_scene_to_file("res://menu/menu.tscn")))
	v.add_child(_botao("Sair do jogo", func(): get_tree().quit()))
	fundo.visible = false
	return fundo


func _botao(texto: String, acao: Callable) -> Button:
	var b := Button.new()
	b.text = texto
	b.custom_minimum_size = Vector2(320, 52)
	b.add_theme_font_size_override("font_size", 20)
	b.pressed.connect(acao)
	return b


func _pausar(sim: bool) -> void:
	_pausa.visible = sim
	get_tree().paused = sim
	if sim:
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	else:
		_vista_mudou(vistas.vista)


func _vista_mudou(v: int) -> void:
	var cima: bool = v == vistas.CIMA
	_grade.visible = cima
	_cursor.visible = false
	_mira.visible = not cima
	if not cima:
		_cartao.visible = false
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE if cima else Input.MOUSE_MODE_CAPTURED
	var linhas := ""
	match v:
		vistas.PRIMEIRA:
			linhas = "1ª pessoa\nWASD andar | Shift correr | Ctrl devagar | Espaço pular | E ou clique: portas\nV: 3ª pessoa | Tab: vista de cima | Esc: pausa"
		vistas.TERCEIRA:
			linhas = "3ª pessoa\nWASD andar | Shift correr | Ctrl devagar | Espaço pular | E ou clique: portas\nV: 1ª pessoa | Tab: vista de cima | Esc: pausa"
		_:
			linhas = "Vista de cima (modo prefeito)\nWASD mover | Q/E ou botão direito: girar | Roda: aproximar | Espaço: voltar ao sobrevivente\nClique num prédio: ficha | Tab: voltar a pé | Esc: pausa"
	_hud.text = linhas
