# Onde ficam os móveis de cada prédio (ambientacao.json) e como ler e gravar.
# Rodando pelo código-fonte, grava direto em kits/<kit>/ambientacao.json.
# No .exe a pasta do jogo não aceita escrita: grava em mobilias/<kit>/ambientacao.json
# ao lado do .exe, e essa versão passa a valer no lugar da que veio no kit.
extends RefCounted


static func no_exe() -> bool:
	return not OS.has_feature("editor")


static func pasta_editada() -> String:
	return OS.get_executable_path().get_base_dir().path_join("mobilias")


static func caminho_editado(kit: String) -> String:
	return pasta_editada().path_join(kit).path_join("ambientacao.json")


static func caminho_original(kit: String) -> String:
	return "res://kits/%s/ambientacao.json" % kit


static func tem_editado(kit: String) -> bool:
	return no_exe() and FileAccess.file_exists(caminho_editado(kit))


static func ler(kit: String, so_original := false) -> Dictionary:
	var caminho := caminho_original(kit)
	if not so_original and tem_editado(kit):
		caminho = caminho_editado(kit)
	if FileAccess.file_exists(caminho):
		var data = JSON.parse_string(FileAccess.get_file_as_string(caminho))
		if data is Dictionary and data.has("itens"):
			return data
	return {"kit": kit, "niveis": {}, "comodos": [], "itens": []}


# Devolve o caminho gravado, ou "" se não deu.
static func gravar(kit: String, doc: Dictionary) -> String:
	var caminho := caminho_original(kit)
	if no_exe():
		caminho = caminho_editado(kit)
		DirAccess.make_dir_recursive_absolute(caminho.get_base_dir())
	var f := FileAccess.open(caminho, FileAccess.WRITE)
	if f == null:
		return ""
	f.store_string(JSON.stringify(_limpo(doc), " ", false) + "\n")
	f.close()
	return ProjectSettings.globalize_path(caminho)


static func apagar_editado(kit: String) -> void:
	if tem_editado(kit):
		DirAccess.remove_absolute(caminho_editado(kit))


# O JSON do Godot lê todo número como decimal: os inteiros voltam a ser inteiros.
static func _limpo(v):
	if v is float and v == floorf(v) and absf(v) < 1e9:
		return int(v)
	if v is Array:
		var a := []
		for x in v:
			a.append(_limpo(x))
		return a
	if v is Dictionary:
		var d := {}
		for k in v:
			d[k] = _limpo(v[k])
		return d
	return v
