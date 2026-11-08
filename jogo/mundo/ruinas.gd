# Variante em ruínas de um prédio, gerada na hora a partir do kit intacto e
# de uma semente (o mesmo prédio sempre estraga do mesmo jeito):
#   1. tira algumas peças de telhado (buracos que o reparo do M2 recoloca);
#   2. quebra parte dos vidros;
#   3. suja tudo com uma camada de encardido (mais forte perto do chão);
#   4. espalha entulho e lixo dos pacotes props/mobilias e props/loot.
# "ruina" vai de 0 (intacto) a 1 (bem destruído).
extends RefCounted

const ENCARDIDO = preload("res://jogo/mundo/encardido.gdshader")

# Peças "de miolo" de telhado que podem cair sem deixar o prédio esquisito.
const TELHAS := ["roof_tile_flat", "roof_tile", "roof_slope"]
const ENTULHO_FORA := ["pilha_sucata", "caixa_papelao", "lixeira", "tabua", "pallet", "garrafa_vidro", "tambor_200l"]
const ENTULHO_DENTRO := ["caixa_papelao", "tabua", "garrafa_vidro", "livro", "roupas", "lata_feijao", "cadeira"]

static var _sujos := {}
static var _vidro_quebrado: StandardMaterial3D
static var _props := {}


static func filtrar_pecas(lista: Array, ruina: float, rng: RandomNumberGenerator, removidas: Array) -> Array:
	var fica := []
	for p in lista:
		if String(p["piece"]) in TELHAS and rng.randf() < 0.12 * ruina:
			removidas.append(p)
			continue
		fica.append(p)
	return fica


static func estragar_visual(predio: Node3D, ruina: float, rng: RandomNumberGenerator) -> void:
	if _vidro_quebrado == null:
		_vidro_quebrado = StandardMaterial3D.new()
		_vidro_quebrado.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		_vidro_quebrado.albedo_color = Color(0, 0, 0, 0)
		_vidro_quebrado.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	for mi in predio.find_children("*", "MeshInstance3D", true, false):
		var mesh: Mesh = mi.mesh
		if mesh == null:
			continue
		var quebra := rng.randf() < 0.55 * ruina
		var nivel := clampi(int(round(ruina * rng.randf_range(0.8, 1.15) * 4.0)), 1, 5)
		for s in mesh.get_surface_count():
			var m: Material = mesh.surface_get_material(s)
			if m == null:
				continue
			if m.resource_name == "glass":
				if quebra:
					mi.set_surface_override_material(s, _vidro_quebrado)
			else:
				mi.set_surface_override_material(s, _sujo(m, nivel))


# Cópia do material com o encardido como segunda passada (vidro fica de fora).
# A força vem em 5 níveis (0,25 a 1,25), para reaproveitar as cópias entre peças.
static func _sujo(m: Material, nivel: int) -> Material:
	var chave := [m, nivel]
	if _sujos.has(chave):
		return _sujos[chave]
	var c: Material = m.duplicate()
	var sm := ShaderMaterial.new()
	sm.shader = ENCARDIDO
	sm.set_shader_parameter("forca", nivel * 0.25)
	c.next_pass = sm
	_sujos[chave] = c
	return c


# Entulho na calçada em frente ao prédio e alguns objetos largados lá dentro.
static func espalhar_entulho(predio, ruina: float, rng: RandomNumberGenerator) -> void:
	var cx: AABB = predio.caixa
	var n_fora := int(round(6 * ruina))
	for i in n_fora:
		var nome: String = ENTULHO_FORA[rng.randi() % ENTULHO_FORA.size()]
		var pos := Vector3(rng.randf_range(cx.position.x + 0.5, cx.end.x - 0.5), 0.0, cx.end.z + rng.randf_range(0.6, 2.2))
		_soltar(predio, nome, pos, rng)
	if predio.pisos.is_empty():
		return
	var n_dentro := int(round(8 * ruina))
	for i in n_dentro:
		var nome: String = ENTULHO_DENTRO[rng.randi() % ENTULHO_DENTRO.size()]
		var base: Vector3 = predio.pisos[rng.randi() % predio.pisos.size()]
		var pos := base + Vector3(rng.randf_range(-0.6, 0.6), 0.0, rng.randf_range(-0.6, 0.6))
		_soltar(predio, nome, pos, rng)


static func _soltar(predio: Node3D, nome: String, pos: Vector3, rng: RandomNumberGenerator) -> void:
	var cena := prop(nome)
	if cena == null:
		return
	var inst: Node3D = cena.instantiate()
	inst.position = pos
	inst.rotation.y = rng.randf() * TAU
	inst.name = "Entulho_" + nome
	predio.add_child(inst)
	for mi in inst.find_children("*", "MeshInstance3D", true, false):
		# Objeto pequeno: some de longe (não pesa na vista de cima).
		mi.visibility_range_end = 70.0
		mi.visibility_range_end_margin = 5.0
		mi.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_SELF


# Carrega um item de props/mobilias ou props/loot pelo id do catálogo.
static func prop(nome: String) -> PackedScene:
	if _props.has(nome):
		return _props[nome]
	var cena: PackedScene = null
	for pasta in ["mobilias", "loot"]:
		var path := "res://props/%s/%s.glb" % [pasta, nome]
		if ResourceLoader.exists(path):
			cena = load(path)
			break
	if cena == null:
		push_warning("Item não encontrado: " + nome)
	_props[nome] = cena
	return cena
