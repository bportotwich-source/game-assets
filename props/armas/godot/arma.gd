class_name ArmaRecomeco
extends Node3D
## Monta uma arma do catálogo (props/armas/catalogo.json): instancia o GLB, põe os acessórios nos encaixes
## e toca as animações embutidas. Exemplo:
##   var a := ArmaRecomeco.new(); a.id = "pistola_9mm"; $Mao.add_child(a)
##   a.por_acessorio("encaixe_boca", "supressor_9mm"); a.atirar()

const RAIZ := "res://props/armas/"

@export var id := "pistola_9mm"
## Acessórios iniciais: { "encaixe_mira": "mira_ponto_vermelho_compacta", ... }
@export var acessorios := {}

var dados: Dictionary
var modelo: Node3D
var anim: AnimationPlayer
var municao := 0
var instalados := {}          # encaixe -> id do acessório

static var _cat := {}


static func catalogo() -> Dictionary:
	if _cat.is_empty():
		_cat = JSON.parse_string(FileAccess.get_file_as_string(RAIZ + "catalogo.json"))
	return _cat


static func item(item_id: String) -> Dictionary:
	var c := catalogo()
	for g in ["armas", "acessorios", "municao", "efeitos"]:
		for r in c[g]:
			if r["id"] == item_id:
				return r
	return {}


func _ready() -> void:
	dados = item(id)
	modelo = load(RAIZ + dados["arquivo"]).instantiate()
	add_child(modelo)
	anim = modelo.find_child("AnimationPlayer", true, false)
	municao = int(dados.get("capacidade", 0))
	for e in dados.get("encaixes", []):
		if e.has("padrao"):
			por_acessorio(e["no"], e["padrao"])
	for enc in acessorios:
		por_acessorio(enc, acessorios[enc])


func encaixe(no: String) -> Dictionary:
	for e in dados.get("encaixes", []):
		if e["no"] == no:
			return e
	return {}


## Põe (ou tira, com acessorio_id = "") um acessório num encaixe. Devolve false se não for compatível.
func por_acessorio(no: String, acessorio_id: String) -> bool:
	var e := encaixe(no)
	if e.is_empty():
		return false
	if acessorio_id != "" and not (acessorio_id in e.get("aceita", [])):
		return false
	for k in e.get("requer", {}):    # ex.: mira na tampa com trilho só existe com essa tampa instalada (valor: id ou lista de ids)
		var r = e["requer"][k]
		var ok: bool = (instalados.get(k, "") in r) if r is Array else (instalados.get(k, "") == r)
		if acessorio_id != "" and not ok:
			return false
	if acessorio_id != "":
		for k in e.get("exclui", []):   # ex.: ponte de mira da pistola e mira no ferrolho ocupam o mesmo lugar
			if instalados.has(k):
				por_acessorio(k, "")
	var alvo: Node3D = modelo.find_child(no, true, false)
	for c in alvo.get_children():
		c.queue_free()
	if e.has("substitui"):            # ex.: carregador estendido esconde o carregador que vem na arma
		for c in modelo.find_child(e["substitui"], true, false).get_children():
			if c is MeshInstance3D:
				c.visible = acessorio_id == ""
	instalados.erase(no)
	if acessorio_id == "":
		_rebater_miras()
		return true
	instalados[no] = acessorio_id
	var a := item(acessorio_id)
	alvo.add_child(load(RAIZ + a["arquivo"]).instantiate())
	_rebater_miras()
	return true


## Miras de ferro rebatíveis (encaixes com "rebate_com"): deitam quando há mira/luneta naquele encaixe e levantam quando sai.
func _rebater_miras() -> void:
	for e in dados.get("encaixes", []):
		if not e.has("rebate_com") or not instalados.has(e["no"]):
			continue
		var deitar := instalados.has(e["rebate_com"])
		var alvo: Node3D = modelo.find_child(e["no"], true, false)
		if alvo.get_child_count() == 0:
			continue
		var ap: AnimationPlayer = alvo.get_child(alvo.get_child_count() - 1).find_child("AnimationPlayer", true, false)
		if ap == null or not ap.has_animation("dobrar") or alvo.get_meta("deitada", false) == deitar:
			continue
		alvo.set_meta("deitada", deitar)
		if deitar:
			ap.play("dobrar")
		else:
			ap.play_backwards("dobrar")


## Ponto de onde a câmera de 1ª pessoa mira: o "olho" da mira/luneta acoplada ou, sem ela, o furo da alça ("mira_ferro").
func linha_de_visada() -> Node3D:
	for e in dados.get("encaixes", []):
		if e["no"] in ["encaixe_mira", "encaixe_ponte"] and instalados.has(e["no"]):
			var olho := modelo.find_child(e["no"], true, false).find_child("olho", true, false)
			if olho:
				return olho
	return modelo.find_child("mira_ferro", true, false)


## Valor final de um atributo com os modificadores dos acessórios (ex.: atributo("ruido_m")).
func atributo(nome: String) -> float:
	var v := float(dados.get(nome, 0.0))
	for no in instalados:
		var a := item(instalados[no])
		for k in a.get("modificadores", {}):
			if k == nome:
				v *= float(a["modificadores"][k])
	return v


## Tiros por carregador, contando um carregador trocado (ex.: estendido de 24).
func capacidade() -> int:
	var extra := 0
	for no in instalados:
		var a := item(instalados[no])
		if a.has("capacidade"):
			return int(a["capacidade"])
		extra += int(a.get("capacidade_extra", 0))     # ex.: prolongador do tubo da espingarda (+1)
	return int(dados.get("capacidade", 0)) + extra


func tocar(nome: String) -> void:
	if anim and anim.has_animation(nome):
		anim.stop()
		anim.play(nome)


func atirar() -> bool:
	if municao <= 0:
		return false
	municao -= 1
	tocar("atirar_ultimo" if municao == 0 and anim.has_animation("atirar_ultimo") else "atirar")
	_clarao()
	get_tree().create_timer(float(dados.get("estojo_s", 0.04))).timeout.connect(_estojo)   # espingarda: casca sai no bombeamento
	return true


func recarregar(quantos := -1) -> void:
	if dados.get("recarga_por_cartucho", false):     # espingarda: um cartucho por vez (a animação "recarregar" é de um cartucho)
		var alvo := capacidade() if quantos < 0 else quantos
		if municao == 0 and anim.has_animation("recarregar_vazia"):
			tocar("recarregar_vazia"); await anim.animation_finished; municao = 1
		while municao < alvo:
			tocar("recarregar"); await anim.animation_finished; municao += 1
		return
	tocar("recarregar_vazia" if municao == 0 and anim.has_animation("recarregar_vazia") else "recarregar")
	municao = capacidade() if quantos < 0 else quantos


func _clarao() -> void:
	var boca: Node3D = modelo.find_child("boca_fogo", true, false)
	if boca == null:
		return
	var f: Node3D = load(RAIZ + "efeitos/clarao_boca.glb").instantiate()
	boca.add_child(f)
	f.rotate_z(randf() * TAU)
	f.scale = Vector3.ONE * randf_range(0.8, 1.2)
	get_tree().create_timer(0.05).timeout.connect(f.queue_free)


func _estojo() -> void:
	var s: Node3D = modelo.find_child("saida_estojo", true, false)
	var mun := item(dados.get("municao", ""))
	if s == null or mun.is_empty():
		return
	var estojo_id := String(mun.get("estojo", String(mun["id"]).replace("municao_", "estojo_")))
	var e := item(estojo_id)
	if e.is_empty():
		return
	var corpo := RigidBody3D.new()
	var forma := CollisionShape3D.new()
	var cap := CapsuleShape3D.new()
	cap.radius = 0.005
	cap.height = 0.02
	forma.shape = cap
	corpo.add_child(forma)
	corpo.add_child(load(RAIZ + e["arquivo"]).instantiate())
	get_tree().current_scene.add_child(corpo)
	corpo.global_transform = s.global_transform
	corpo.linear_velocity = s.global_basis * Vector3(randf_range(1.5, 2.5), randf_range(1.0, 2.0), randf_range(-0.3, 0.3))
	corpo.angular_velocity = Vector3(randf(), randf(), randf()) * 20.0
	get_tree().create_timer(4.0).timeout.connect(corpo.queue_free)
