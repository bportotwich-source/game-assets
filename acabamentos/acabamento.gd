# Aplica o acabamento por cômodo (kits/<kit>/acabamento.json) num prédio já montado.
# Uso: const Acabamento = preload("res://acabamentos/acabamento.gd"); var mats := Acabamento.aplicar(predio, "bangalo")   -> devolve os ShaderMaterial criados
extends RefCounted

const SHADER := preload("res://acabamentos/acabamento.gdshader")
static var _arrays := {}          # "albedo"/"normal"/"orm" -> Texture2DArray
static var _estilos := {}


static func _preparar() -> bool:
	if not _arrays.is_empty():
		return true
	var f := FileAccess.get_file_as_string("res://acabamentos/estilos.json")
	if f == "":
		return false
	_estilos = JSON.parse_string(f)
	for tipo in ["albedo", "normal", "orm"]:
		var imgs: Array[Image] = []
		for nome in _estilos["camadas"]:
			var tex: Texture2D = load("res://acabamentos/%s_%s.png" % [nome, tipo])
			var img := tex.get_image()
			if img.is_compressed():
				img.decompress()
			img.convert(Image.FORMAT_RGBA8)
			img.generate_mipmaps()
			imgs.append(img)
		var arr := Texture2DArray.new()
		arr.create_from_images(imgs)
		_arrays[tipo] = arr
	return true


static func aplicar(predio: Node3D, kit: String) -> Array:
	var path := "res://kits/%s/acabamento.json" % kit
	if not FileAccess.file_exists(path) or not _preparar():
		return []
	var d: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(path))
	var bytes := Marshalls.base64_to_raw(d["mapa"])
	var nx := int(d["nx"])
	var nz := int(d["nz"])
	var niveis: Array = d["niveis"]
	var img := Image.create_from_data(nx, nz * niveis.size(), false, Image.FORMAT_RGBA8, bytes)
	var mapa := ImageTexture.create_from_image(img)
	var niv := PackedFloat32Array()
	niv.resize(48)
	for i in niveis.size():
		niv[i] = float(niveis[i])
	var pdef := PackedVector4Array()
	var pcc := PackedVector3Array()
	var pcb := PackedVector3Array()
	for p in _estilos["paredes"]:
		pdef.append(Vector4(p["cima"], p["baixo"], p["altura"], (1 if p["rodape"] else 0) + (2 if p["sanca"] else 0)))
		pcc.append(Vector3(p["cor_cima"][0], p["cor_cima"][1], p["cor_cima"][2]))
		pcb.append(Vector3(p["cor_baixo"][0], p["cor_baixo"][1], p["cor_baixo"][2]))
	pdef.resize(32)
	pcc.resize(32)
	pcb.resize(32)
	var fcam := PackedInt32Array()
	var fcor := PackedVector3Array()
	for p in _estilos["pisos"]:
		fcam.append(int(p["camada"]))
		fcor.append(Vector3(p["cor"][0], p["cor"][1], p["cor"][2]))
	fcam.resize(16)
	fcor.resize(16)
	var paredes: Array = d["materiais"]["paredes"]
	var pisos: Array = d["materiais"]["pisos"]
	var feitos := {}
	for mi in predio.find_children("*", "MeshInstance3D", true, false):
		if mi.mesh == null:
			continue
		for s in mi.mesh.get_surface_count():
			var m = mi.mesh.surface_get_material(s)
			if not (m is BaseMaterial3D):
				continue
			var eh_parede := paredes.has(m.resource_name)
			var eh_piso := pisos.has(m.resource_name)
			if not (eh_parede or eh_piso):
				continue
			if not feitos.has(m):
				var sm := ShaderMaterial.new()
				sm.shader = SHADER
				sm.set_shader_parameter("orig_albedo", m.albedo_texture)
				sm.set_shader_parameter("orig_cor", m.albedo_color)
				sm.set_shader_parameter("orig_uv_escala", m.uv1_scale)
				sm.set_shader_parameter("orig_tem_normal", m.normal_enabled and m.normal_texture != null)
				sm.set_shader_parameter("orig_normal", m.normal_texture)
				sm.set_shader_parameter("orig_tem_orm", m.roughness_texture != null)
				sm.set_shader_parameter("orig_orm", m.roughness_texture)
				sm.set_shader_parameter("orig_rugosidade", m.roughness)
				sm.set_shader_parameter("mapa", mapa)
				sm.set_shader_parameter("mapa_origem", Vector2(d["x0"], d["z0"]))
				sm.set_shader_parameter("mapa_cel", float(d["cel"]))
				sm.set_shader_parameter("mapa_tam", Vector2i(nx, nz))
				sm.set_shader_parameter("n_niveis", niveis.size())
				sm.set_shader_parameter("niveis", niv)
				sm.set_shader_parameter("eh_piso", eh_piso)
				sm.set_shader_parameter("acab_albedo", _arrays["albedo"])
				sm.set_shader_parameter("acab_normal", _arrays["normal"])
				sm.set_shader_parameter("acab_orm", _arrays["orm"])
				sm.set_shader_parameter("parede_def", pdef)
				sm.set_shader_parameter("parede_cor_cima", pcc)
				sm.set_shader_parameter("parede_cor_baixo", pcb)
				sm.set_shader_parameter("piso_camada", fcam)
				sm.set_shader_parameter("piso_cor", fcor)
				feitos[m] = sm
			mi.set_surface_override_material(s, feitos[m])
	return feitos.values()
