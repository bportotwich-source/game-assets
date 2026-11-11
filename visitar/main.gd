# Monta um kit do pacote a partir do building_layout.json e coloca um jogador
# em primeira pessoa na frente da entrada. [ e ] trocam de prédio (1 a 9 e 0 vão direto aos 10 primeiros).
extends Node3D

const ArquivoMoveis = preload("res://mobiliar/arquivo.gd")
const KitDoorScript = preload("res://scripts/godot/door.gd")
const PlayerScript = preload("res://visitar/player.gd")
const Acabamento = preload("res://acabamentos/acabamento.gd")
const Realista = preload("res://materiais/realista.gd")

const KITS := [
	"predio-tijolos", "predio-mansarda", "padaria", "casa-enxaimel",
	"torre-escalonada", "casa-de-campo", "bangalo", "supermercado", "galeria",
	"casa-americana", "duplex", "diner", "brownstones", "quartel-bombeiros", "posto-gasolina", "casas-shotgun", "igreja", "motel", "biblioteca", "escolinha", "three-flats", "correios", "estacao", "armazem", "patio-missoes", "vila-urbana", "casa-modernista", "delegacia", "fabrica", "cinema", "casas-vitorianas", "casa-reboco", "clinica", "banco", "casa-barcos", "lanchonete", "hotel", "mansao", "rodoviaria", "observatorio", "caixa-dagua", "banco-googie", "cinema-drive-in", "fazenda", "piscina-publica", "torre-art-deco", "concessionaria", "concha-acustica", "serraria", "minigolfe", "pista-skate", "ferro-velho", "parque-trailers", "garagem-vertical", "loft-industrial", "apartamentos-patio", "campo-beisebol", "hospital", "condominio", "predio-lojas", "casas-vitorianas-geminadas",
]

@export var kit: String = "galeria"
@export var start_doors_open: bool = false

var _scenes := {}
var _shapes := {}
var _props := {}
var _building: Node3D
var _ambiente: Node3D
var _mostrar_ambiente := true
var _player
var _hud: Label
# Iluminação dos interiores (kits/<kit>/luzes.json, gerado por scripts/iluminacao/luzes.py).
const SOMBRAS_PERTO := 4          # só as luzes mais perto do jogador fazem sombra (sombra de luz pontual é cara)
var _luzes: Node3D
var _luzes_ligadas := true
var _ilum_nova := true
var _env: Environment
var _sun: DirectionalLight3D
var _mats_lampada := {}           # material original -> cópia que brilha
var _tom: ShaderMaterial          # variação de tom em coordenadas do mundo (next_pass das paredes, pisos e tetos)
var _relogio_sombra := 0.0
var _acab: Array = []             # materiais do acabamento por cômodo (acabamentos/acabamento.gd)
var _acab_ligado := true
var _real: Array = []             # materiais trocados pelos realistas (materiais/realista.gd)
var _real_ligado := true
var _plafon_base: Mesh            # plafon simples nos cômodos que não têm luminária no kit
var _plafon_vidro: Mesh
var _plafon_vidro_mat: StandardMaterial3D


func _ready() -> void:
	_make_world()
	_player = PlayerScript.new()
	_player.name = "Jogador"
	add_child(_player)
	_make_hud()
	_load_kit(kit)


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		var cur := KITS.find(kit)
		match event.physical_keycode:
			KEY_M:
				_mostrar_ambiente = not _mostrar_ambiente
				if _ambiente:
					_ambiente.visible = _mostrar_ambiente
					for b in _ambiente.find_children("*", "StaticBody3D", true, false):
						b.collision_layer = 1 if _mostrar_ambiente else 0
				_update_hud()
				return
			KEY_L:
				_luzes_ligadas = not _luzes_ligadas
				_aplicar_iluminacao()
				return
			KEY_I:
				_ilum_nova = not _ilum_nova
				_aplicar_iluminacao()
				return
			KEY_K:
				_acab_ligado = not _acab_ligado
				for sm in _acab:
					sm.set_shader_parameter("ligado", _acab_ligado)
				_update_hud()
				return
			KEY_R:
				_real_ligado = not _real_ligado
				Realista.ligar(_real, _real_ligado)
				# o acabamento por cômodo guarda as texturas do material da peça: refaz com as de agora
				_acab = Acabamento.aplicar(_building, kit)
				for sm in _acab:
					sm.set_shader_parameter("ligado", _acab_ligado)
				_variacao_tom()
				_update_hud()
				return
			KEY_BRACKETRIGHT, KEY_PAGEDOWN:
				_load_kit(KITS[(cur + 1) % KITS.size()])
				return
			KEY_BRACKETLEFT, KEY_PAGEUP:
				_load_kit(KITS[(cur - 1 + KITS.size()) % KITS.size()])
				return
		var i: int = 9 if event.physical_keycode == KEY_0 else event.physical_keycode - KEY_1
		if i >= 0 and i < mini(10, KITS.size()):
			_load_kit(KITS[i])


func _load_kit(k: String) -> void:
	kit = k
	if _building:
		_building.queue_free()
	if _ambiente:
		_ambiente.queue_free()
		_ambiente = null
	if _luzes:
		_luzes.queue_free()
		_luzes = null
	_scenes.clear()
	_shapes.clear()
	var box := _build_kit(k)
	_real = Realista.aplicar(_building, k)
	if not _real_ligado:
		Realista.ligar(_real, false)
	_acab = Acabamento.aplicar(_building, k)
	for sm in _acab:
		sm.set_shader_parameter("ligado", _acab_ligado)
	_ambientar(k)
	_iluminar(k)
	var spawn := Vector3(_front_door_x(box), 0.1, box.end.z + 6.0)
	_player.respawn(spawn)
	_update_hud()


# X da porta da frente mais perto do centro da fachada, para o jogador nascer de frente para ela.
func _front_door_x(box: AABB) -> float:
	var mid := (box.position.x + box.end.x) * 0.5
	var best := mid
	var best_d := INF
	var front := -INF
	for d in _building.get_children():
		if d.has_method("interact"):
			front = maxf(front, d.position.z)
	for d in _building.get_children():
		if not d.has_method("interact") or d.position.z < front - 1.0:
			continue
		var c: Vector3 = d.position + Basis(Vector3.UP, d.rotation.y) * Vector3(0.45, 0, 0)
		if absf(c.x - mid) < best_d:
			best_d = absf(c.x - mid)
			best = c.x
	return best


func _make_world() -> void:
	var sky_mat := ProceduralSkyMaterial.new()
	sky_mat.sky_top_color = Color(0.36, 0.56, 0.86)
	sky_mat.sky_horizon_color = Color(0.72, 0.8, 0.9)
	sky_mat.ground_horizon_color = Color(0.6, 0.62, 0.6)
	var sky := Sky.new()
	sky.sky_material = sky_mat
	var env := Environment.new()
	env.background_mode = Environment.BG_SKY
	env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.92, 0.9, 0.86)
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.ssao_enabled = true
	_env = env
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)

	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-52, -35, 0)
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 90.0
	_sun = sun
	add_child(sun)
	_tom = ShaderMaterial.new()
	_tom.shader = load("res://visitar/variacao_tom.gdshader")

	var ground := StaticBody3D.new()
	ground.name = "Chao"
	var cs := CollisionShape3D.new()
	cs.shape = WorldBoundaryShape3D.new()
	ground.add_child(cs)
	var mi := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(300, 300)
	mi.mesh = plane
	var gm := StandardMaterial3D.new()
	gm.albedo_color = Color(0.45, 0.5, 0.42)
	gm.roughness = 1.0
	mi.material_override = gm
	mi.position.y = -0.005
	ground.add_child(mi)
	add_child(ground)


func _make_hud() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	_hud = Label.new()
	_hud.position = Vector2(16, 12)
	_hud.add_theme_color_override("font_outline_color", Color.BLACK)
	_hud.add_theme_constant_override("outline_size", 6)
	layer.add_child(_hud)
	var cross := Label.new()
	cross.text = "+"
	cross.set_anchors_preset(Control.PRESET_CENTER)
	cross.add_theme_color_override("font_outline_color", Color.BLACK)
	cross.add_theme_constant_override("outline_size", 4)
	layer.add_child(cross)


func _update_hud() -> void:
	var lines := "Prédio %d de %d: %s\n" % [KITS.find(kit) + 1, KITS.size(), kit]
	lines += "Clique: prender o mouse | WASD: andar | Shift: correr | Espaço: pular\n"
	lines += "E ou clique: abrir/fechar porta | F: voar (Espaço sobe, Q desce) | Esc: soltar o mouse\n"
	lines += "M: mostrar/esconder os móveis e itens (%s)\n" % ("ligado" if _mostrar_ambiente else "desligado")
	lines += "K: papel de parede, azulejo e piso por cômodo (%s)\n" % ("ligado" if _acab_ligado else "desligado")
	lines += "R: materiais realistas (%s)\n" % (("ligado" if _real_ligado else "desligado") if not _real.is_empty() else "este prédio ainda não tem")
	lines += "L: acender/apagar as luzes (%s) | I: iluminação %s (I compara com a antiga)\n" % ["acesas" if _luzes_ligadas else "apagadas", "nova" if _ilum_nova else "antiga"]
	lines += "Trocar de prédio: [ anterior | ] próximo (ou Page Up / Page Down; 1 a 9 e 0 vão aos 10 primeiros)"
	_hud.text = lines


func _piece(name: String) -> PackedScene:
	if _scenes.has(name):
		return _scenes[name]
	var path := "res://kits/%s/pieces/%s.glb" % [kit, name]
	var ps: PackedScene = null
	if ResourceLoader.exists(path):
		ps = load(path)
	else:
		push_warning("Peça não encontrada: " + path)
	_scenes[name] = ps
	return ps


func _build_kit(k: String) -> AABB:
	_building = Node3D.new()
	_building.name = "Predio"
	add_child(_building)
	var f := FileAccess.open("res://kits/%s/building_layout.json" % k, FileAccess.READ)
	if f == null:
		push_error("Layout não encontrado para o kit " + k)
		return AABB(Vector3(-5, 0, -5), Vector3(10, 1, 10))
	var data: Dictionary = JSON.parse_string(f.get_as_text())
	var lo := Vector3(INF, INF, INF)
	var hi := Vector3(-INF, -INF, -INF)
	for p in data["placements"]:
		if p["piece"] == "player_scale_ref":
			continue   # boneco de escala, só para as prévias
		var ps := _piece(p["piece"])
		if ps == null:
			continue
		var inst: Node3D = ps.instantiate()
		var pos := Vector3(p["pos"][0], p["pos"][1], p["pos"][2])
		lo = Vector3(minf(lo.x, pos.x), minf(lo.y, pos.y), minf(lo.z, pos.z))
		hi = Vector3(maxf(hi.x, pos.x), maxf(hi.y, pos.y), maxf(hi.z, pos.z))
		if p.has("door"):
			# Porta: nó KitDoor na dobradiça, com corpo próprio que gira junto.
			var d = KitDoorScript.new()
			d.name = "Porta_%s" % p["piece"]
			d.position = pos
			d.rotation.y = deg_to_rad(float(p["door"]["closed"]))
			d.open_angle_deg = float(p["door"]["open"]) - float(p["door"]["closed"])
			d.start_open = start_doors_open
			_building.add_child(d)
			var body := AnimatableBody3D.new()
			body.sync_to_physics = false
			d.add_child(body)
			body.add_child(inst)
			_add_shapes(inst, body)
		else:
			inst.position = pos
			inst.rotation.y = deg_to_rad(float(p["rotY"]))
			_building.add_child(inst)
			var sb := StaticBody3D.new()
			inst.add_child(sb)
			_add_shapes(inst, sb)
	return AABB(lo, hi - lo)


# Cria colisão exata (trimesh) para cada malha da peça. A forma é
# reaproveitada entre peças iguais.
func _add_shapes(inst: Node3D, body: CollisionObject3D) -> void:
	for mi in inst.find_children("*", "MeshInstance3D", true, false):
		if mi.mesh == null:
			continue
		var shape: Shape3D = _shapes.get(mi.mesh)
		if shape == null:
			shape = mi.mesh.create_trimesh_shape()
			_shapes[mi.mesh] = shape
		var cs := CollisionShape3D.new()
		cs.shape = shape
		cs.transform = body.global_transform.affine_inverse() * mi.global_transform
		body.add_child(cs)


# Móveis e itens do prédio (kits/<kit>/ambientacao.json, gerado por scripts/ambientacao/ambientar.py).
# Cada item vira uma cena de props/ com uma caixa de colisão; manchas, cacos e papéis no chão não colidem.
func _ambientar(k: String) -> void:
	# Se o prédio foi arrumado no Modo Mobiliar, vale a versão salva lá.
	var data: Dictionary = ArquivoMoveis.ler(k)
	if data["itens"].is_empty():
		return
	_ambiente = Node3D.new()
	_ambiente.name = "Ambientacao"
	_ambiente.visible = _mostrar_ambiente
	add_child(_ambiente)
	for it in data["itens"]:
		var arq := "res://" + str(it["arquivo"])
		var ps: PackedScene = _props.get(arq)
		if ps == null:
			if not ResourceLoader.exists(arq):
				continue
			ps = load(arq)
			_props[arq] = ps
		var inst: Node3D = ps.instantiate()
		inst.name = str(it["item"])
		inst.position = Vector3(it["pos"][0], it["pos"][1], it["pos"][2])
		inst.rotation.y = deg_to_rad(float(it["rotY"]))
		_ambiente.add_child(inst)
		if it.get("grupo", "") == "loot":
			continue
		var box := AABB()
		var first := true
		for mi in inst.find_children("*", "MeshInstance3D", true, false):
			if mi.mesh == null:
				continue
			var b: AABB = (inst.global_transform.affine_inverse() * mi.global_transform) * mi.get_aabb()
			box = b if first else box.merge(b)
			first = false
		if first or box.size.y < 0.08:
			continue
		var sb := StaticBody3D.new()
		sb.collision_layer = 1 if _mostrar_ambiente else 0
		var cs := CollisionShape3D.new()
		var shape := BoxShape3D.new()
		shape.size = box.size
		cs.shape = shape
		cs.position = box.get_center()
		sb.add_child(cs)
		inst.add_child(sb)



# Uma OmniLight3D por luz do luzes.json. As lâmpadas das luminárias brilham (material com emissão).
func _iluminar(k: String) -> void:
	_mats_lampada.clear()
	var path := "res://kits/%s/luzes.json" % k
	var data = null
	if FileAccess.file_exists(path):
		data = JSON.parse_string(FileAccess.get_file_as_string(path))
	_luzes = Node3D.new()
	_luzes.name = "Luzes"
	add_child(_luzes)
	if typeof(data) == TYPE_DICTIONARY:
		for l in data.get("luzes", []):
			var o := OmniLight3D.new()
			o.position = Vector3(l["pos"][0], l["pos"][1], l["pos"][2])
			o.omni_range = float(l["alcance"])
			o.omni_attenuation = 1.4
			o.light_energy = float(l["energia"]) * 1.6
			o.light_color = Color(l["cor"][0], l["cor"][1], l["cor"][2])
			o.light_size = 0.08
			o.shadow_bias = 0.06
			o.shadow_normal_bias = 1.5
			o.distance_fade_enabled = true
			o.distance_fade_begin = 28.0
			o.distance_fade_length = 8.0
			o.set_meta("externa", l["tipo"] == "externa")
			_luzes.add_child(o)
			if l["tipo"] == "gerada" and l.has("teto"):
				_plafon(Vector3(l["pos"][0], float(l["teto"]), l["pos"][2]))
		var nomes: Array = data.get("materiais", [])
		for mi in _building.find_children("*", "MeshInstance3D", true, false):
			if mi.mesh == null:
				continue
			for s in mi.mesh.get_surface_count():
				var m = mi.mesh.surface_get_material(s)
				if m is BaseMaterial3D and nomes.has(m.resource_name):
					if not _mats_lampada.has(m):
						var g: BaseMaterial3D = m.duplicate()
						g.emission_enabled = true
						g.emission = Color(1.0, 0.86, 0.66)
						g.emission_energy_multiplier = 2.5
						_mats_lampada[m] = g
					mi.set_surface_override_material(s, _mats_lampada[m])
	_variacao_tom()
	_aplicar_iluminacao()


func _plafon(p: Vector3) -> void:
	if _plafon_base == null:
		var b := CylinderMesh.new()
		b.top_radius = 0.17
		b.bottom_radius = 0.15
		b.height = 0.03
		b.radial_segments = 24
		var bm := StandardMaterial3D.new()
		bm.albedo_color = Color(0.9, 0.89, 0.86)
		bm.roughness = 0.5
		b.material = bm
		_plafon_base = b
		var v := SphereMesh.new()
		v.radius = 0.14
		v.height = 0.14
		v.is_hemisphere = true
		v.radial_segments = 24
		v.rings = 8
		_plafon_vidro_mat = StandardMaterial3D.new()
		_plafon_vidro_mat.albedo_color = Color(0.97, 0.95, 0.9)
		_plafon_vidro_mat.roughness = 0.3
		_plafon_vidro_mat.emission = Color(1.0, 0.88, 0.7)
		_plafon_vidro_mat.emission_energy_multiplier = 2.5
		v.material = _plafon_vidro_mat
		_plafon_vidro = v
	var a := MeshInstance3D.new()
	a.mesh = _plafon_base
	a.position = p - Vector3(0, 0.015, 0)
	a.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_luzes.add_child(a)
	var g := MeshInstance3D.new()
	g.mesh = _plafon_vidro
	g.position = p - Vector3(0, 0.03, 0)
	g.rotation_degrees.x = 180
	g.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_luzes.add_child(g)


# Variação de tom em grande escala (esconde a repetição e tira a cara de "uma cor só") nas paredes, pisos e tetos.
func _variacao_tom() -> void:
	var feitos := {}
	for mi in _building.find_children("*", "MeshInstance3D", true, false):
		if mi.mesh == null:
			continue
		for s in mi.mesh.get_surface_count():
			var m = mi.mesh.surface_get_material(s)
			if not (m is BaseMaterial3D) or _mats_lampada.has(m):
				continue
			if m.transparency != BaseMaterial3D.TRANSPARENCY_DISABLED or m.metallic > 0.5:
				continue
			if not feitos.has(m):
				m.next_pass = _tom if _ilum_nova else null
				feitos[m] = true
	for sm in _acab:
		sm.next_pass = _tom if _ilum_nova else null


func _aplicar_iluminacao() -> void:
	if _env == null:
		return
	if _ilum_nova:
		# Luz ambiente fraca: o que ilumina por dentro são as lâmpadas e o sol pela janela.
		_env.ambient_light_energy = 0.22
		_env.ssao_enabled = true
		_env.ssao_radius = 1.4
		_env.ssao_intensity = 2.4
		_env.ssao_power = 1.6
		_env.ssao_detail = 0.6
		_env.ssil_enabled = true
		_env.ssil_radius = 4.0
		_env.ssil_intensity = 0.5
		_env.glow_enabled = true
		_env.glow_intensity = 0.5
		_env.glow_hdr_threshold = 1.4
		_env.tonemap_mode = Environment.TONE_MAPPER_ACES
		_env.tonemap_exposure = 1.1
		_sun.light_energy = 1.5
	else:
		_env.ambient_light_energy = 0.55
		_env.ssao_enabled = true
		_env.ssao_radius = 1.0
		_env.ssao_intensity = 2.0
		_env.ssao_power = 1.5
		_env.ssao_detail = 0.5
		_env.ssil_enabled = false
		_env.glow_enabled = false
		_env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
		_env.tonemap_exposure = 1.0
		_sun.light_energy = 1.1
	var acesas := _ilum_nova and _luzes_ligadas
	if _luzes:
		_luzes.visible = _ilum_nova
		for o in _luzes.get_children():
			if o is OmniLight3D:
				o.visible = acesas
	if _plafon_vidro_mat:
		_plafon_vidro_mat.emission_enabled = acesas
	for m in _mats_lampada:
		_mats_lampada[m].emission_enabled = acesas
	if _building:
		_variacao_tom()
	_update_hud()


# Só as luzes internas mais perto do jogador ganham sombra; revisto 4 vezes por segundo.
func _process(delta: float) -> void:
	_relogio_sombra -= delta
	if _relogio_sombra > 0.0 or _luzes == null or not (_ilum_nova and _luzes_ligadas) or _player == null:
		return
	_relogio_sombra = 0.25
	var eye: Vector3 = _player.global_position + Vector3(0, 1.65, 0)
	var lista := []
	for o in _luzes.get_children():
		if not (o is OmniLight3D):
			continue
		var d: float = o.global_position.distance_to(eye)
		lista.append([d, o])
		o.shadow_enabled = false
	lista.sort_custom(func(a, b): return a[0] < b[0])
	var n := 0
	for e in lista:
		if n >= SOMBRAS_PERTO or e[0] > e[1].omni_range + 2.0:
			break
		if e[1].get_meta("externa", false):
			continue
		e[1].shadow_enabled = true
		n += 1
