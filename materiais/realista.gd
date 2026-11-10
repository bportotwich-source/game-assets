# Troca os materiais simples de um prédio já montado pelos materiais realistas
# compartilhados desta pasta (materiais/<nome>_albedo|normal|orm.webp).
# O que trocar vem de kits/<kit>/materiais.json: nome do material da peça ->
# material da biblioteca. As peças dos kits não mudam.
#
# Uso (antes do acabamento por cômodo, que lê as texturas do material da peça):
#   const Realista = preload("res://materiais/realista.gd")
#   var trocados := Realista.aplicar(predio, "bangalo")
#   Realista.ligar(trocados, false)   # volta ao material original
extends RefCounted

const PASTA := "res://materiais/"
const PROPS := [
	"albedo_texture", "albedo_color", "normal_enabled", "normal_texture", "normal_scale",
	"roughness_texture", "roughness_texture_channel", "roughness",
	"ao_enabled", "ao_texture", "ao_texture_channel", "ao_light_affect",
	"uv1_triplanar", "uv1_world_triplanar", "uv1_scale", "uv1_offset", "texture_filter",
]
static var _tex := {}


static func _textura(nome: String, tipo: String) -> Texture2D:
	var k := "%s_%s" % [nome, tipo]
	if not _tex.has(k):
		var p := "%s%s.webp" % [PASTA, k]
		_tex[k] = load(p) if ResourceLoader.exists(p) else null
	return _tex[k]


# Devolve os materiais trocados (os mesmos BaseMaterial3D das peças, alterados no lugar).
static func aplicar(predio: Node3D, kit: String) -> Array:
	var path := "res://kits/%s/materiais.json" % kit
	if not FileAccess.file_exists(path):
		return []
	var d = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not (d is Dictionary) or not d.has("materiais"):
		return []
	var mapa: Dictionary = d["materiais"]
	var feitos := {}
	for mi in predio.find_children("*", "MeshInstance3D", true, false):
		if mi.mesh == null:
			continue
		for s in mi.mesh.get_surface_count():
			var m = mi.mesh.surface_get_material(s)
			if not (m is BaseMaterial3D) or feitos.has(m) or not mapa.has(m.resource_name):
				continue
			if not m.has_meta("realista_novo"):
				var novo := _valores(m, mapa[m.resource_name])
				if novo.is_empty():
					continue
				var orig := {}
				for p in PROPS:
					orig[p] = m.get(p)
				m.set_meta("realista_orig", orig)
				m.set_meta("realista_novo", novo)
			feitos[m] = true
	var lista := feitos.keys()
	ligar(lista, true)
	return lista


static func ligar(lista: Array, ligado: bool) -> void:
	for m in lista:
		var v: Dictionary = m.get_meta("realista_novo" if ligado else "realista_orig", {})
		for p in v:
			m.set(p, v[p])


static func _valores(m: BaseMaterial3D, def: Dictionary) -> Dictionary:
	var nome := String(def.get("material", ""))
	var albedo := _textura(nome, "albedo")
	if albedo == null:
		push_warning("Material realista não encontrado: " + nome)
		return {}
	var normal := _textura(nome, "normal")
	var orm := _textura(nome, "orm")
	var cor := Color.WHITE
	if def.has("cor"):
		cor = Color(def["cor"][0], def["cor"][1], def["cor"][2])
	var v := {
		"albedo_texture": albedo, "albedo_color": cor,
		"normal_enabled": normal != null, "normal_texture": normal, "normal_scale": 1.0,
		"texture_filter": BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC,
	}
	if orm != null:
		v["roughness_texture"] = orm
		v["roughness_texture_channel"] = BaseMaterial3D.TEXTURE_CHANNEL_GREEN
		v["roughness"] = 1.0
		v["ao_enabled"] = true
		v["ao_texture"] = orm
		v["ao_texture_channel"] = BaseMaterial3D.TEXTURE_CHANNEL_RED
		v["ao_light_affect"] = 0.3
	# Peças sem UV (molduras, caixilhos, portas): projeta o ladrilho pelas três faces, na medida da peça.
	if bool(def.get("sem_uv", false)):
		v["uv1_triplanar"] = true
		v["uv1_world_triplanar"] = false
		v["uv1_scale"] = Vector3(0.5, 0.5, 0.5)
		v["uv1_offset"] = Vector3.ZERO
	return v
