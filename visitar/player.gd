# Jogador em primeira pessoa no padrão do pacote: 1,8 m de altura, raio 0,3 m,
# olhos a 1,65 m. A cápsula "flutua" 0,35 m acima dos pés e raios para baixo
# acham o chão, então soleiras, degraus e escadas rolantes não travam o passo.
extends CharacterBody3D

const WALK := 4.0
const RUN := 7.5
const JUMP := 4.2
const GRAVITY := 9.8
const STEP := 0.35        # degrau mais alto que ele sobe sem pular
const PROBE := 0.7
const SENS := 0.0025

var flying := false
var _cam: Camera3D
var _ray: RayCast3D
var _shape: CollisionShape3D


func _ready() -> void:
	_shape = CollisionShape3D.new()
	var cap := CapsuleShape3D.new()
	cap.radius = 0.3
	cap.height = 1.8 - STEP
	_shape.shape = cap
	_shape.position.y = STEP + cap.height * 0.5
	add_child(_shape)

	_cam = Camera3D.new()
	_cam.position.y = 1.65
	_cam.fov = 75.0
	_cam.near = 0.05
	_cam.current = true
	add_child(_cam)

	_ray = RayCast3D.new()
	_ray.target_position = Vector3(0, 0, -2.5)
	_ray.add_exception(self)
	_cam.add_child(_ray)

	motion_mode = CharacterBody3D.MOTION_MODE_FLOATING
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func respawn(pos: Vector3) -> void:
	global_position = pos
	rotation = Vector3.ZERO
	_cam.rotation = Vector3.ZERO
	velocity = Vector3.ZERO


func _unhandled_input(event: InputEvent) -> void:
	var captured := Input.mouse_mode == Input.MOUSE_MODE_CAPTURED
	if event is InputEventMouseMotion and captured:
		rotate_y(-event.relative.x * SENS)
		_cam.rotation.x = clampf(_cam.rotation.x - event.relative.y * SENS, -1.5, 1.5)
	elif event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		if captured:
			_interact()
		else:
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	elif event is InputEventKey and event.pressed and not event.echo:
		match event.physical_keycode:
			KEY_ESCAPE:
				Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
			KEY_E:
				_interact()
			KEY_F:
				flying = not flying
				_shape.disabled = flying
				velocity = Vector3.ZERO


func _interact() -> void:
	_ray.force_raycast_update()
	if not _ray.is_colliding():
		return
	var n: Node = _ray.get_collider()
	while n and not n.has_method("interact"):
		n = n.get_parent()
	if n:
		n.interact()


func _input_dir() -> Vector3:
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
	var speed := RUN if Input.is_physical_key_pressed(KEY_SHIFT) else WALK
	var dir := _input_dir()

	if flying:
		var v := _cam.global_transform.basis * dir * speed * 2.0
		if Input.is_physical_key_pressed(KEY_SPACE):
			v.y += speed * 2.0
		if Input.is_physical_key_pressed(KEY_Q):
			v.y -= speed * 2.0
		global_position += v * delta
		return

	var move := global_transform.basis * dir * speed
	velocity.x = move.x
	velocity.z = move.z
	var floor_y = _floor_height()
	var feet := global_position.y
	if floor_y != null and velocity.y <= 0.0 and feet - floor_y <= STEP:
		# No chão: acompanha a altura do piso (sobe e desce degraus suavemente).
		global_position.y = lerpf(feet, floor_y, minf(1.0, 18.0 * delta))
		velocity.y = JUMP if Input.is_physical_key_pressed(KEY_SPACE) else 0.0
	else:
		velocity.y -= GRAVITY * delta
	move_and_slide()
	if global_position.y < -20.0:
		global_position = Vector3(global_position.x, 2.0, global_position.z)
		velocity = Vector3.ZERO


# Maior altura de piso sob o jogador (centro e 4 pontos em volta), ou null.
func _floor_height():
	var space := get_world_3d().direct_space_state
	var best = null
	for o in [Vector2.ZERO, Vector2(0.2, 0), Vector2(-0.2, 0), Vector2(0, 0.2), Vector2(0, -0.2)]:
		var from := global_position + Vector3(o.x, PROBE, o.y)
		var q := PhysicsRayQueryParameters3D.create(from, from - Vector3(0, PROBE + STEP, 0))
		q.exclude = [get_rid()]
		var hit := space.intersect_ray(q)
		if hit and hit.normal.y > 0.6:
			if best == null or hit.position.y > best:
				best = hit.position.y
	return best
