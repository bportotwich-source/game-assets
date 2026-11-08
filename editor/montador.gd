# Funções comuns do editor de montagem: acha os kits e as peças, carrega as
# cenas, descobre que folha de porta vai em cada parede com vão e monta uma
# lista de peças (com colisão e portas que abrem) para o modo de andar.
extends RefCounted


const KitDoorScript = preload("res://scripts/godot/door.gd")

const GRID_STEP := 1.0      # grade de encaixe do PADRAO_METRICAS.md
const MODULE := 2.0         # largura do módulo de parede
const FLOOR_H := 3.0        # andar a andar

static var _scenes := {}
static var _shapes := {}
static var _companions := {}
static var _pieces := {}


# Pastas em res://kits que têm peças.
static func kit_list() -> PackedStringArray:
	var out := PackedStringArray()
	var d := DirAccess.open("res://kits")
	if d == null:
		return out
	for k in d.get_directories():
		if DirAccess.dir_exists_absolute("res://kits/%s/pieces" % k):
			out.append(k)
	out.sort()
	return out


# Nomes das peças de um kit. No .exe exportado os .glb aparecem como
# .glb.import / .glb.remap, então tiramos o sufixo.
static func piece_list(kit: String) -> PackedStringArray:
	if _pieces.has(kit):
		return _pieces[kit]
	var names := {}
	var d := DirAccess.open("res://kits/%s/pieces" % kit)
	if d:
		for f in d.get_files():
			for suf in [".import", ".remap"]:
				if f.ends_with(suf):
					f = f.left(f.length() - suf.length())
			if f.ends_with(".glb"):
				names[f.get_basename()] = true
	if names.is_empty():
		# Sem listagem de pasta: usa as peças que o layout do kit cita.
		for p in kit_layout(kit):
			names[p["piece"]] = true
	var out := PackedStringArray(names.keys())
	out.sort()
	_pieces[kit] = out
	return out


static func piece_scene(kit: String, piece: String) -> PackedScene:
	var key := kit + "/" + piece
	if _scenes.has(key):
		return _scenes[key]
	var path := "res://kits/%s/pieces/%s.glb" % [kit, piece]
	var ps: PackedScene = null
	if ResourceLoader.exists(path):
		ps = load(path)
	else:
		push_warning("Peça não encontrada: " + path)
	_scenes[key] = ps
	return ps


static func is_door_leaf(piece: String) -> bool:
	return piece.contains("door_leaf") or piece.ends_with("_leaf") or piece.contains("_leaf_")


static func read_json(path: String):
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return null
	return JSON.parse_string(f.get_as_text())


static func kit_layout(kit: String) -> Array:
	var data = read_json("res://kits/%s/building_layout.json" % kit)
	if data is Dictionary and data.has("placements"):
		return data["placements"]
	return []


# Para cada parede com vão de porta, a folha que o kit põe nela e onde fica
# (no espaço da parede). Aprendido do building_layout.json do kit.
# Resultado: { "parede": {"leaf": "door_leaf_x", "offset": Vector3, "rot": graus, "open": graus} }
static func door_companions(kit: String) -> Dictionary:
	if _companions.has(kit):
		return _companions[kit]
	var res := {}
	var ps := kit_layout(kit)
	var walls := []
	for p in ps:
		var n: String = p["piece"]
		if p.has("door") or is_door_leaf(n) or n.contains("steps") or n.contains("stair"):
			continue
		if n.contains("door") or n.contains("entry") or n.contains("gate") or n.contains("_bay"):
			walls.append(p)
	for d in ps:
		if not d.has("door"):
			continue
		var dp := _v(d["pos"])
		var best = null
		var best_dist := 1.8
		for w in walls:
			var wp := _v(w["pos"])
			if absf(wp.y - dp.y) > 0.6:
				continue
			var dist := Vector2(wp.x - dp.x, wp.z - dp.z).length()
			if dist < best_dist:
				best_dist = dist
				best = w
		if best == null or res.has(best["piece"]):
			continue
		var wrot := float(best["rotY"])
		var local := Basis(Vector3.UP, deg_to_rad(-wrot)) * (dp - _v(best["pos"]))
		res[best["piece"]] = {
			"leaf": d["piece"],
			"offset": local,
			"rot": float(d["door"]["closed"]) - wrot,
			"open": float(d["door"]["open"]) - float(d["door"]["closed"]),
		}
	_companions[kit] = res
	return res


static func _v(a) -> Vector3:
	return Vector3(float(a[0]), float(a[1]), float(a[2]))


# Monta as peças (formato do layout, com "kit" em cada uma) dentro de parent,
# com colisão exata e portas que abrem. Devolve a caixa que envolve tudo.
static func build_walkable(placements: Array, parent: Node3D, default_kit: String = "") -> AABB:
	var box := AABB()
	var first := true
	for p in placements:
		var piece: String = p["piece"]
		if piece == "player_scale_ref":
			continue
		var ps := piece_scene(p.get("kit", default_kit), piece)
		if ps == null:
			continue
		var inst: Node3D = ps.instantiate()
		var pos := _v(p["pos"])
		if first:
			box = AABB(pos, Vector3.ZERO)
			first = false
		else:
			box = box.expand(pos)
		if p.has("door"):
			var d = KitDoorScript.new()
			d.position = pos
			d.rotation.y = deg_to_rad(float(p["door"]["closed"]))
			d.open_angle_deg = float(p["door"]["open"]) - float(p["door"]["closed"])
			parent.add_child(d)
			var body := AnimatableBody3D.new()
			body.sync_to_physics = false
			d.add_child(body)
			body.add_child(inst)
			add_shapes(inst, body)
		else:
			inst.position = pos
			inst.rotation.y = deg_to_rad(float(p.get("rotY", 0.0)))
			parent.add_child(inst)
			var sb := StaticBody3D.new()
			inst.add_child(sb)
			add_shapes(inst, sb)
	return box


# Colisão exata (trimesh) para cada malha da peça, reaproveitada entre peças iguais.
static func add_shapes(inst: Node3D, body: CollisionObject3D) -> void:
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


# Céu, sol, luz ambiente e chão, iguais aos do modo de visitar.
static func make_world(parent: Node) -> void:
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
	env.ambient_light_energy = 0.55
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.ssao_enabled = true
	var we := WorldEnvironment.new()
	we.environment = env
	parent.add_child(we)

	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-52, -35, 0)
	sun.light_energy = 1.1
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 120.0
	parent.add_child(sun)

	var ground := StaticBody3D.new()
	ground.name = "Chao"
	var cs := CollisionShape3D.new()
	cs.shape = WorldBoundaryShape3D.new()
	ground.add_child(cs)
	var mi := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(400, 400)
	mi.mesh = plane
	var gm := StandardMaterial3D.new()
	gm.albedo_color = Color(0.45, 0.5, 0.42)
	gm.roughness = 1.0
	mi.material_override = gm
	mi.position.y = -0.005
	ground.add_child(mi)
	parent.add_child(ground)
