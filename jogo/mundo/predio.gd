# Monta um kit do pacote (kits/<nome>/building_layout.json) como um prédio do
# mundo do jogo: peças com colisão exata, portas que abrem e, se pedido, a
# variante em ruínas (ver ruinas.gd). O nó guarda em metadados o que foi
# removido pela ruína, para o reparo do M2 poder recolocar peça por peça.
extends Node3D

const KitDoorScript = preload("res://scripts/godot/door.gd")
const Ruinas = preload("res://jogo/mundo/ruinas.gd")

var kit := ""
var dados := {}            # linha de jogo/dados/predios.json
var caixa := AABB()        # caixa das malhas, em coordenadas locais do prédio
var pecas_removidas := []  # placements tirados pela ruína (para reparo)
var pisos := []            # posições locais de pisos do térreo (para espalhar entulho)

static var _cenas := {}
static var _formas := {}


func montar(nome_kit: String, ruina: float, semente: int) -> void:
	kit = nome_kit
	name = "Predio_" + nome_kit
	var f := FileAccess.open("res://kits/%s/building_layout.json" % kit, FileAccess.READ)
	if f == null:
		push_error("Layout não encontrado para o kit " + kit)
		return
	var layout: Dictionary = JSON.parse_string(f.get_as_text())
	var rng := RandomNumberGenerator.new()
	rng.seed = semente
	var lista: Array = layout["placements"]
	if ruina > 0.0:
		lista = Ruinas.filtrar_pecas(lista, ruina, rng, pecas_removidas)
	for p in lista:
		if p["piece"] == "player_scale_ref":
			continue
		var ps := _peca(p["piece"])
		if ps == null:
			continue
		var inst: Node3D = ps.instantiate()
		var pos := Vector3(p["pos"][0], p["pos"][1], p["pos"][2])
		var tags: Array = p.get("tags", [])
		if "floor0" in tags and String(p["piece"]).contains("floor"):
			pisos.append(pos)
		if p.has("door"):
			var d = KitDoorScript.new()
			d.name = "Porta_%s" % p["piece"]
			d.position = pos
			d.rotation.y = deg_to_rad(float(p["door"]["closed"]))
			d.open_angle_deg = float(p["door"]["open"]) - float(p["door"]["closed"])
			# Na cidade abandonada algumas portas ficaram abertas.
			d.start_open = ruina > 0.0 and rng.randf() < 0.35 * ruina
			add_child(d)
			var body := AnimatableBody3D.new()
			body.sync_to_physics = false
			d.add_child(body)
			body.add_child(inst)
			_colisao(inst, body)
		else:
			inst.position = pos
			inst.rotation.y = deg_to_rad(float(p["rotY"]))
			add_child(inst)
			var sb := StaticBody3D.new()
			inst.add_child(sb)
			_colisao(inst, sb)
	caixa = _caixa_malhas()
	if ruina > 0.0:
		Ruinas.estragar_visual(self, ruina, rng)


func _peca(nome: String) -> PackedScene:
	var path := "res://kits/%s/pieces/%s.glb" % [kit, nome]
	if _cenas.has(path):
		return _cenas[path]
	var ps: PackedScene = null
	if ResourceLoader.exists(path):
		ps = load(path)
	else:
		push_warning("Peça não encontrada: " + path)
	_cenas[path] = ps
	return ps


# Colisão exata (trimesh) por malha, reaproveitada entre peças iguais.
func _colisao(inst: Node3D, body: CollisionObject3D) -> void:
	for mi in inst.find_children("*", "MeshInstance3D", true, false):
		if mi.mesh == null:
			continue
		var forma: Shape3D = _formas.get(mi.mesh)
		if forma == null:
			forma = mi.mesh.create_trimesh_shape()
			_formas[mi.mesh] = forma
		var cs := CollisionShape3D.new()
		cs.shape = forma
		cs.transform = _local(body).affine_inverse() * _local(mi)
		body.add_child(cs)


# Transformação relativa a este prédio (funciona antes de entrar na árvore).
func _local(n: Node3D) -> Transform3D:
	var t := Transform3D.IDENTITY
	while n and n != self:
		t = n.transform * t
		n = n.get_parent() as Node3D
	return t


func _caixa_malhas() -> AABB:
	var cx := AABB()
	var primeiro := true
	for mi in find_children("*", "MeshInstance3D", true, false):
		if mi.mesh == null:
			continue
		var b: AABB = _local(mi) * mi.mesh.get_aabb()
		cx = b if primeiro else cx.merge(b)
		primeiro = false
	return cx


# Distância de visão: longe da câmera o prédio vira um bloco simples (LOD
# grosso para a vista de cima). Os LODs finos das malhas o Godot já gera na
# importação dos GLB.
func aplicar_lod(distancia: float) -> void:
	for mi in find_children("*", "MeshInstance3D", true, false):
		mi.visibility_range_end = distancia
		mi.visibility_range_end_margin = 10.0
		mi.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_SELF
	var bloco := MeshInstance3D.new()
	bloco.name = "LOD_bloco"
	var bm := BoxMesh.new()
	bm.size = caixa.size
	bloco.mesh = bm
	bloco.position = caixa.get_center()
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(dados.get("cor_lod", "8a7d6b"))
	mat.roughness = 1.0
	bloco.material_override = mat
	bloco.visibility_range_begin = distancia
	bloco.visibility_range_begin_margin = 10.0
	bloco.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_SELF
	add_child(bloco)
