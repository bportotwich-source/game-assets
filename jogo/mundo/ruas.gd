# Ruas do mapa de teste: um cruzamento de duas ruas com asfalto, faixas,
# calçadas com meio-fio (colisão própria) e postes apagados. Tudo gerado a
# partir dos números de jogo/dados/mapa_teste.json, com as texturas PBR do
# kit banco-googie (asfalto, meio-fio, grama).
extends RefCounted

const TEX := "res://kits/banco-googie/%s_%s.png"


static func montar(raiz: Node3D, mapa: Dictionary) -> void:
	var lx: Array = mapa["comprimento_x"]
	var lz: Array = mapa["comprimento_z"]
	var meia: float = mapa["rua_largura"] * 0.5
	var calc: float = mapa["calcada"]
	var no := Node3D.new()
	no.name = "Ruas"
	raiz.add_child(no)

	# Chão (terra e mato seco) com colisão infinita.
	var chao := StaticBody3D.new()
	chao.name = "Chao"
	var cs := CollisionShape3D.new()
	cs.shape = WorldBoundaryShape3D.new()
	chao.add_child(cs)
	var plano := PlaneMesh.new()
	plano.size = Vector2(400, 400)
	var mi := MeshInstance3D.new()
	mi.mesh = plano
	mi.position.y = -0.03
	mi.material_override = _mat("grass", Color(0.58, 0.56, 0.4), 0.25)
	chao.add_child(mi)
	no.add_child(chao)

	var asfalto := _mat("asphalt", Color(0.62, 0.62, 0.62), 0.25)
	var calcada := _mat("curb", Color(0.66, 0.64, 0.6), 0.5)
	# Asfalto: rua leste-oeste e rua norte-sul (topo em y = 0).
	_caixa(no, Vector3((lx[0] + lx[1]) * 0.5, -0.02, 0), Vector3(lx[1] - lx[0], 0.04, 2 * meia), asfalto, false)
	_caixa(no, Vector3(0, -0.02, (lz[0] + lz[1]) * 0.5), Vector3(2 * meia, 0.039, lz[1] - lz[0]), asfalto, false)

	# Calçadas em L em cada quadrante (15 cm de altura, o passo sobe sozinho).
	var h := 0.15
	for sx in [-1, 1]:
		for sz in [-1, 1]:
			var fim_x: float = lx[1] if sx > 0 else -lx[0]
			var fim_z: float = lz[1] if sz > 0 else -lz[0]
			var cx: float = sx * (meia + fim_x) * 0.5
			_caixa(no, Vector3(cx, h * 0.5, sz * (meia + calc * 0.5)), Vector3(fim_x - meia, h, calc), calcada, true)
			var cz: float = sz * (meia + calc + fim_z) * 0.5
			_caixa(no, Vector3(sx * (meia + calc * 0.5), h * 0.5, cz), Vector3(calc, h, fim_z - meia - calc), calcada, true)

	# Faixas: tracejado amarelo no meio e faixas de pedestre no cruzamento.
	var tinta := StandardMaterial3D.new()
	tinta.albedo_color = Color(0.85, 0.72, 0.3)
	tinta.roughness = 0.9
	var branca := StandardMaterial3D.new()
	branca.albedo_color = Color(0.7, 0.68, 0.64)
	branca.roughness = 0.9
	var x := float(lx[0]) + 1.0
	while x < lx[1]:
		if absf(x) > meia + calc + 1.5:
			_caixa(no, Vector3(x, 0.006, 0), Vector3(2.0, 0.012, 0.14), tinta, false)
		x += 4.0
	var z := float(lz[0]) + 1.0
	while z < lz[1]:
		if absf(z) > meia + calc + 1.5:
			_caixa(no, Vector3(0, 0.006, z), Vector3(0.14, 0.012, 2.0), tinta, false)
		z += 4.0
	for lado in [-1, 1]:
		for i in range(-3, 4):
			var off: float = i * 1.2
			_caixa(no, Vector3(off, 0.006, lado * (meia + 1.4)), Vector3(0.5, 0.012, 2.4), branca, false)
			_caixa(no, Vector3(lado * (meia + 1.4), 0.006, off), Vector3(2.4, 0.012, 0.5), branca, false)

	# Postes apagados na beira das calçadas.
	var metal := StandardMaterial3D.new()
	metal.albedo_color = Color(0.32, 0.33, 0.33)
	metal.metallic = 0.6
	metal.roughness = 0.55
	x = float(lx[0]) + 6.0
	var n := 0
	while x < lx[1]:
		if absf(x) > meia + calc + 3.0:
			var sz: int = 1 if n % 2 == 0 else -1
			_poste(no, Vector3(x, h, sz * (meia + 0.45)), sz, metal)
		x += 14.0
		n += 1


static func _mat(nome: String, tinta: Color, escala: float) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	var alb := TEX % [nome, "albedo"]
	if ResourceLoader.exists(alb):
		m.albedo_texture = load(alb)
		m.normal_enabled = true
		m.normal_texture = load(TEX % [nome, "normal"])
		m.roughness_texture = load(TEX % [nome, "orm"])
		m.roughness_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_GREEN
	m.albedo_color = tinta
	m.roughness = 1.0
	m.uv1_triplanar = true
	m.uv1_world_triplanar = true
	m.uv1_scale = Vector3.ONE * escala
	return m


static func _caixa(pai: Node3D, centro: Vector3, tam: Vector3, mat: Material, colide: bool) -> void:
	var mi := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = tam
	mi.mesh = bm
	mi.material_override = mat
	mi.position = centro
	pai.add_child(mi)
	if colide:
		var sb := StaticBody3D.new()
		var cs := CollisionShape3D.new()
		var bs := BoxShape3D.new()
		bs.size = tam
		cs.shape = bs
		sb.add_child(cs)
		mi.add_child(sb)


static func _poste(pai: Node3D, base: Vector3, lado: int, mat: Material) -> void:
	var p := Node3D.new()
	p.position = base
	pai.add_child(p)
	var haste := MeshInstance3D.new()
	var cil := CylinderMesh.new()
	cil.top_radius = 0.06
	cil.bottom_radius = 0.09
	cil.height = 6.5
	haste.mesh = cil
	haste.position.y = 3.25
	haste.material_override = mat
	p.add_child(haste)
	var braco := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = Vector3(0.08, 0.08, 1.6)
	braco.mesh = bm
	braco.position = Vector3(0, 6.4, -lado * 0.75)
	braco.material_override = mat
	p.add_child(braco)
	var luminaria := MeshInstance3D.new()
	var lm := BoxMesh.new()
	lm.size = Vector3(0.3, 0.12, 0.55)
	luminaria.mesh = lm
	luminaria.position = Vector3(0, 6.32, -lado * 1.45)
	luminaria.material_override = mat
	p.add_child(luminaria)
	var sb := StaticBody3D.new()
	var cs := CollisionShape3D.new()
	var cap := CylinderShape3D.new()
	cap.radius = 0.1
	cap.height = 6.5
	cs.shape = cap
	cs.position.y = 3.25
	sb.add_child(cs)
	p.add_child(sb)
