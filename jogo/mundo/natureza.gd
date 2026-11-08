# Natureza tomando conta da cidade: árvores, arbustos, mato, flores e pedras
# do pacote props/natureza (Stylized Nature MegaKit, Quaternius, CC0),
# espalhados por semente nos terrenos vazios, com mato também nas frestas da
# calçada e do asfalto. Mato, flores e pedrinhas vão em MultiMesh (um desenho
# por tipo), árvores e pedras grandes como cenas com colisão simples.
extends RefCounted

const PASTA := "res://props/natureza/%s.gltf"

const ARVORES := ["CommonTree_1", "CommonTree_2", "CommonTree_3", "CommonTree_4", "CommonTree_5",
	"DeadTree_1", "DeadTree_2", "DeadTree_3", "Pine_1", "Pine_2", "Pine_3", "Pine_5",
	"Birch_1", "Birch_2", "Birch_4", "TwistedTree_5"]
const ARBUSTOS := ["Bush_Common", "Bush_Common_Flowers", "Bush_Large", "Bush_Long_1", "Bush_Long_2", "Fern_1", "Plant_1_Big", "Plant_2_Big"]
const PEDRAS := ["Rock_Medium_1", "Rock_Medium_2", "Rock_Medium_3", "Rock_Big_1"]
# Tipos miúdos (MultiMesh): nome, quantidade nos terrenos, escala.
const MIUDOS := [
	["Grass_Common_Tall", 260, 0.55], ["Grass_Wispy_Tall", 200, 0.55], ["Grass_Common_Short", 260, 0.6],
	["Grass_Wide_Tall", 120, 0.5], ["Clover_1", 80, 0.7], ["Flower_3_Group", 50, 0.7],
	["Flower_4_Group", 40, 0.7], ["Pebble_Round_1", 60, 0.8], ["Pebble_Square_2", 40, 0.8],
]


# livre(x, z) -> bool diz se o ponto está num terreno (fora de rua e prédio).
# fresta(x, z) -> bool diz se é borda de calçada/asfalto onde nasce mato.
static func espalhar(raiz: Node3D, lim: AABB, livre: Callable, fresta: Callable, semente: int) -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = semente
	var no := Node3D.new()
	no.name = "Natureza"
	raiz.add_child(no)

	# Árvores com distância mínima entre elas.
	var postas: Array[Vector2] = []
	var tentativas := 0
	while postas.size() < 42 and tentativas < 3000:
		tentativas += 1
		var p := _ponto(rng, lim)
		if not livre.call(p.x, p.y, 3.0) or _perto(postas, p, 7.0):
			continue
		postas.append(p)
		var nome: String = ARVORES[rng.randi() % ARVORES.size()]
		_cena(no, nome, p, rng.randf_range(0.75, 1.1), rng, 0.3)
	for i in 70:
		var p := _ponto(rng, lim)
		if livre.call(p.x, p.y, 1.0):
			_cena(no, ARBUSTOS[rng.randi() % ARBUSTOS.size()], p, rng.randf_range(0.7, 1.2), rng, 0.0)
	for i in 12:
		var p := _ponto(rng, lim)
		if livre.call(p.x, p.y, 2.5):
			_cena(no, PEDRAS[rng.randi() % PEDRAS.size()], p, rng.randf_range(0.4, 0.8), rng, -1.0)

	for m in MIUDOS:
		var pts: Array[Transform3D] = []
		var alvo: int = m[1]
		var t := 0
		while pts.size() < alvo and t < alvo * 6:
			t += 1
			var p := _ponto(rng, lim)
			if livre.call(p.x, p.y, 0.3):
				pts.append(_xf(p, 0.0, m[2], rng))
		# Um pouco de mato nas frestas da cidade (beira de calçada e asfalto).
		if String(m[0]).begins_with("Grass"):
			t = 0
			var n_fresta := alvo / 4
			var achados := 0
			while achados < n_fresta and t < n_fresta * 40:
				t += 1
				var p := _ponto(rng, lim)
				if fresta.call(p.x, p.y):
					pts.append(_xf(p, 0.0, m[2] * 0.8, rng))
					achados += 1
		_multimesh(no, m[0], pts)


static func _ponto(rng: RandomNumberGenerator, lim: AABB) -> Vector2:
	return Vector2(rng.randf_range(lim.position.x, lim.end.x), rng.randf_range(lim.position.z, lim.end.z))


static func _perto(lista: Array[Vector2], p: Vector2, d: float) -> bool:
	for q in lista:
		if q.distance_to(p) < d:
			return true
	return false


static func _xf(p: Vector2, y: float, escala: float, rng: RandomNumberGenerator) -> Transform3D:
	var s := escala * rng.randf_range(0.8, 1.25)
	var b := Basis(Vector3.UP, rng.randf() * TAU).scaled(Vector3(s, s, s))
	return Transform3D(b, Vector3(p.x, y, p.y))


# raio_tronco > 0: cilindro de colisão; < 0: colisão convexa (pedra); 0: sem.
static func _cena(pai: Node3D, nome: String, p: Vector2, escala: float, rng: RandomNumberGenerator, raio_tronco: float) -> void:
	var path := PASTA % nome
	if not ResourceLoader.exists(path):
		push_warning("Natureza não encontrada: " + path)
		return
	var inst: Node3D = (load(path) as PackedScene).instantiate()
	inst.name = nome
	inst.transform = _xf(p, 0.0, escala, rng)
	pai.add_child(inst)
	if raio_tronco > 0.0:
		var sb := StaticBody3D.new()
		var cs := CollisionShape3D.new()
		var cil := CylinderShape3D.new()
		cil.radius = raio_tronco
		cil.height = 4.0
		cs.shape = cil
		cs.position.y = 2.0
		sb.add_child(cs)
		inst.add_child(sb)
	elif raio_tronco < 0.0:
		for mi in inst.find_children("*", "MeshInstance3D", true, false):
			var sb := StaticBody3D.new()
			var cs := CollisionShape3D.new()
			cs.shape = mi.mesh.create_convex_shape()
			sb.add_child(cs)
			mi.add_child(sb)
	else:
		for mi in inst.find_children("*", "MeshInstance3D", true, false):
			mi.visibility_range_end = 110.0
			mi.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_SELF


static func _multimesh(pai: Node3D, nome: String, pts: Array[Transform3D]) -> void:
	var path := PASTA % nome
	if pts.is_empty() or not ResourceLoader.exists(path):
		return
	var cena: Node3D = (load(path) as PackedScene).instantiate()
	var mis := cena.find_children("*", "MeshInstance3D", true, false)
	for mi in mis:
		var mm := MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_3D
		mm.mesh = mi.mesh
		mm.instance_count = pts.size()
		for i in pts.size():
			mm.set_instance_transform(i, pts[i] * mi.transform)
		var mmi := MultiMeshInstance3D.new()
		mmi.name = "Miudo_" + nome
		mmi.multimesh = mm
		mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		pai.add_child(mmi)
	cena.free()
