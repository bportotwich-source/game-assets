# O sobrevivente controlado pelo jogador, no padrão do pacote: 1,8 m de altura,
# raio 0,3 m, olhos a 1,65 m. Mesma física do passeio (visitar/player.gd): a
# cápsula flutua 0,35 m e raios acham o chão, então degraus e soleiras não
# travam. As câmeras ficam em jogo/cameras/vistas.gd; aqui só o corpo.
# O boneco é provisório (player_scale_ref dos kits) até entrar o pacote CC0.
extends CharacterBody3D

const ANDAR := 4.0
const CORRER := 7.5
const AGACHADO := 1.8
const PULO := 4.2
const GRAVIDADE := 9.8
const DEGRAU := 0.35
const SONDA := 0.7
const SENS := 0.0025
const OLHOS := 1.65
const CAMADA_CORPO := 2     # camada de render do boneco (a 1ª pessoa não desenha)

var ativo := true           # falso na vista de cima: fica parado esperando
var cabeca: Node3D          # gira em X (olhar para cima e para baixo)
var corpo: Node3D
var _forma: CollisionShape3D


func _ready() -> void:
	_forma = CollisionShape3D.new()
	var cap := CapsuleShape3D.new()
	cap.radius = 0.3
	cap.height = 1.8 - DEGRAU
	_forma.shape = cap
	_forma.position.y = DEGRAU + cap.height * 0.5
	add_child(_forma)

	cabeca = Node3D.new()
	cabeca.name = "Cabeca"
	cabeca.position.y = OLHOS
	add_child(cabeca)

	var cena: PackedScene = load("res://kits/padaria/pieces/player_scale_ref.glb")
	if cena:
		corpo = cena.instantiate()
		corpo.name = "Corpo"
		add_child(corpo)
		for mi in corpo.find_children("*", "MeshInstance3D", true, false):
			mi.layers = 1 << (CAMADA_CORPO - 1)
	motion_mode = CharacterBody3D.MOTION_MODE_FLOATING


func olhar(rel: Vector2) -> void:
	rotate_y(-rel.x * SENS)
	cabeca.rotation.x = clampf(cabeca.rotation.x - rel.y * SENS, -1.45, 1.45)


func _direcao() -> Vector3:
	var v := Vector3.ZERO
	if Input.is_physical_key_pressed(KEY_W) or Input.is_physical_key_pressed(KEY_UP):
		v.z -= 1
	if Input.is_physical_key_pressed(KEY_S) or Input.is_physical_key_pressed(KEY_DOWN):
		v.z += 1
	if Input.is_physical_key_pressed(KEY_A) or Input.is_physical_key_pressed(KEY_LEFT):
		v.x -= 1
	if Input.is_physical_key_pressed(KEY_D) or Input.is_physical_key_pressed(KEY_RIGHT):
		v.x += 1
	return v.normalized()


func _physics_process(delta: float) -> void:
	var dir := _direcao() if ativo else Vector3.ZERO
	var vel := ANDAR
	if ativo and Input.is_physical_key_pressed(KEY_SHIFT):
		vel = CORRER
	elif ativo and Input.is_physical_key_pressed(KEY_CTRL):
		vel = AGACHADO
	var mov := global_transform.basis * dir * vel
	velocity.x = mov.x
	velocity.z = mov.z
	var piso = _altura_piso()
	var pes := global_position.y
	if piso != null and velocity.y <= 0.0 and pes - piso <= DEGRAU:
		global_position.y = lerpf(pes, piso, minf(1.0, 18.0 * delta))
		velocity.y = PULO if ativo and Input.is_physical_key_pressed(KEY_SPACE) else 0.0
	else:
		velocity.y -= GRAVIDADE * delta
	move_and_slide()
	if global_position.y < -20.0:
		global_position = Vector3(global_position.x, 2.0, global_position.z)
		velocity = Vector3.ZERO


func _altura_piso():
	var space := get_world_3d().direct_space_state
	var melhor = null
	for o in [Vector2.ZERO, Vector2(0.2, 0), Vector2(-0.2, 0), Vector2(0, 0.2), Vector2(0, -0.2)]:
		var de := global_position + Vector3(o.x, SONDA, o.y)
		var q := PhysicsRayQueryParameters3D.create(de, de - Vector3(0, SONDA + DEGRAU, 0))
		q.exclude = [get_rid()]
		var hit := space.intersect_ray(q)
		if hit and hit.normal.y > 0.6:
			if melhor == null or hit.position.y > melhor:
				melhor = hit.position.y
	return melhor
