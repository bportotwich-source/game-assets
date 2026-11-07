# Monta um kit do pacote a partir do building_layout.json e coloca um jogador
# em primeira pessoa na frente da entrada. Teclas 1 a 9 trocam de prédio.
extends Node3D

const KitDoorScript = preload("res://scripts/godot/door.gd")
const PlayerScript = preload("res://visitar/player.gd")

const KITS := [
	"predio-tijolos", "predio-mansarda", "padaria", "casa-enxaimel",
	"torre-escalonada", "casa-de-campo", "bangalo", "supermercado", "galeria",
]

@export var kit: String = "galeria"
@export var start_doors_open: bool = false

var _scenes := {}
var _shapes := {}
var _building: Node3D
var _player
var _hud: Label


func _ready() -> void:
	_make_world()
	_player = PlayerScript.new()
	_player.name = "Jogador"
	add_child(_player)
	_make_hud()
	_load_kit(kit)


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		var i: int = event.physical_keycode - KEY_1
		if i >= 0 and i < KITS.size():
			_load_kit(KITS[i])


func _load_kit(k: String) -> void:
	kit = k
	if _building:
		_building.queue_free()
	_scenes.clear()
	_shapes.clear()
	var box := _build_kit(k)
	var spawn := Vector3((box.position.x + box.end.x) * 0.5, 0.1, box.end.z + 6.0)
	_player.respawn(spawn)
	_update_hud()


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
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.ambient_light_energy = 0.9
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.ssao_enabled = true
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)

	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-52, -35, 0)
	sun.light_energy = 1.1
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 90.0
	add_child(sun)

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
	var lines := "Prédio: %s\n" % kit
	lines += "Clique: prender o mouse | WASD: andar | Shift: correr | Espaço: pular\n"
	lines += "E ou clique: abrir/fechar porta | F: voar (Espaço sobe, Q desce) | Esc: soltar o mouse\n"
	lines += "Trocar de prédio: "
	for i in KITS.size():
		lines += "%d %s  " % [i + 1, KITS[i]]
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
