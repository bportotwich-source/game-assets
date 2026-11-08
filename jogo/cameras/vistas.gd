# As 3 vistas do Recomeço sobre o mesmo mundo, com uma câmera só que desliza
# de uma posição para outra:
#   1ª pessoa: nos olhos do sobrevivente.
#   3ª pessoa: atrás do ombro direito; encostada em parede, aproxima sozinha.
#   Vista de cima (modo prefeito): inclinada, gira, aproxima e anda pelo mapa.
# V troca 1ª <-> 3ª. Tab sobe para a vista de cima e volta para a vista a pé.
extends Node3D

signal vista_mudou(vista: int)

enum { PRIMEIRA, TERCEIRA, CIMA }

const TRANSICAO := 0.6
const OMBRO := Vector3(0.55, 0.1, 3.0)   # direita, cima, trás (a partir do pivô)
const PIVO_ALTURA := 1.6
const CIMA_INCLINACAO := deg_to_rad(-55.0)
const CIMA_DIST_MIN := 12.0
const CIMA_DIST_MAX := 120.0

var vista := PRIMEIRA
var vista_a_pe := PRIMEIRA
var sobrevivente: CharacterBody3D
var camera: Camera3D

var foco := Vector3.ZERO        # ponto do chão no centro da vista de cima
var cima_giro := 0.0
var cima_dist := 45.0
var limites := AABB(Vector3(-80, 0, -80), Vector3(160, 0, 160))

var _de := Transform3D.IDENTITY
var _t := 1.0


func _ready() -> void:
	camera = Camera3D.new()
	camera.fov = 75.0
	camera.near = 0.05
	camera.far = 600.0
	camera.current = true
	add_child(camera)
	_aplicar_mascara()


func trocar(nova: int) -> void:
	if nova == vista:
		return
	_de = camera.global_transform
	_t = 0.0
	if nova == CIMA:
		foco = Vector3(sobrevivente.global_position.x, 0, sobrevivente.global_position.z)
		cima_giro = sobrevivente.rotation.y
	else:
		vista_a_pe = nova
	vista = nova
	sobrevivente.ativo = nova != CIMA
	_aplicar_mascara()
	vista_mudou.emit(vista)


func alternar_pe() -> void:
	if vista == CIMA:
		return
	trocar(TERCEIRA if vista == PRIMEIRA else PRIMEIRA)


func alternar_cima() -> void:
	trocar(vista_a_pe if vista == CIMA else CIMA)


func _aplicar_mascara() -> void:
	if camera == null:
		return
	# Na 1ª pessoa o boneco não aparece (só a sombra dele).
	camera.set_cull_mask_value(2, vista != PRIMEIRA)
	camera.fov = 75.0 if vista == PRIMEIRA else 70.0 if vista == TERCEIRA else 50.0


# Controles da vista de cima (chamado por jogo.gd).
func girar_cima(rad: float) -> void:
	cima_giro += rad


func zoom_cima(fator: float) -> void:
	cima_dist = clampf(cima_dist * fator, CIMA_DIST_MIN, CIMA_DIST_MAX)


func mover_cima(dir: Vector2, delta: float) -> void:
	var v := Basis(Vector3.UP, cima_giro) * Vector3(dir.x, 0, dir.y)
	foco += v * cima_dist * 0.9 * delta
	foco.x = clampf(foco.x, limites.position.x, limites.end.x)
	foco.z = clampf(foco.z, limites.position.z, limites.end.z)


func centralizar() -> void:
	foco = Vector3(sobrevivente.global_position.x, 0, sobrevivente.global_position.z)


func _process(delta: float) -> void:
	if sobrevivente == null:
		return
	var alvo := _alvo()
	if _t < 1.0:
		_t = minf(1.0, _t + delta / TRANSICAO)
		var k := smoothstep(0.0, 1.0, _t)
		camera.global_transform = _de.interpolate_with(alvo, k)
	else:
		camera.global_transform = alvo


func _alvo() -> Transform3D:
	match vista:
		PRIMEIRA:
			return sobrevivente.cabeca.global_transform
		TERCEIRA:
			return _alvo_ombro()
		_:
			var b := Basis(Vector3.UP, cima_giro) * Basis(Vector3.RIGHT, CIMA_INCLINACAO)
			return Transform3D(b, foco + b * Vector3(0, 0, cima_dist))


func _alvo_ombro() -> Transform3D:
	var b: Basis = sobrevivente.global_transform.basis * Basis(Vector3.RIGHT, sobrevivente.cabeca.rotation.x)
	var pivo := sobrevivente.global_position + Vector3(0, PIVO_ALTURA, 0)
	var desejado := pivo + b * OMBRO
	# Aproxima a câmera quando há parede entre o ombro e ela.
	var q := PhysicsRayQueryParameters3D.create(pivo, desejado)
	q.exclude = [sobrevivente.get_rid()]
	var hit := get_world_3d().direct_space_state.intersect_ray(q)
	if hit:
		var d := pivo.distance_to(hit.position)
		desejado = pivo + (desejado - pivo).normalized() * maxf(0.25, d - 0.25)
	return Transform3D(b, desejado)


# Raio que sai do centro da tela, para interagir nas vistas a pé.
func raio_centro(alcance: float) -> Dictionary:
	var de := camera.global_position
	var para := de - camera.global_transform.basis.z * (alcance + de.distance_to(sobrevivente.cabeca.global_position))
	var q := PhysicsRayQueryParameters3D.create(de, para)
	q.exclude = [sobrevivente.get_rid()]
	return get_world_3d().direct_space_state.intersect_ray(q)


# Raio que sai do mouse, para a vista de cima.
func raio_mouse(pos_tela: Vector2) -> Dictionary:
	var de := camera.project_ray_origin(pos_tela)
	var para := de + camera.project_ray_normal(pos_tela) * 600.0
	var q := PhysicsRayQueryParameters3D.create(de, para)
	return get_world_3d().direct_space_state.intersect_ray(q)
