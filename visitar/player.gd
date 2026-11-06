# Jogador em primeira pessoa no padrão do pacote: cápsula de 1,8 m e raio 0,3 m,
# olhos a 1,65 m. Sobe degraus de até 0,25 m sozinho (escadas e escadas rolantes).
extends CharacterBody3D

const WALK := 4.0
const RUN := 7.5
const JUMP := 4.2
const GRAVITY := 9.8
const STEP := 0.25
const SENS := 0.0025

var flying := false
var _cam: Camera3D
var _ray: RayCast3D
var _shape: CollisionShape3D


func _ready() -> void:
	_shape = CollisionShape3D.new()
	var cap := CapsuleShape3D.new()
	cap.radius = 0.3
	cap.height = 1.8
	_shape.shape = cap
	_shape.position.y = 0.9
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

	floor_snap_length = 0.3
	floor_max_angle = deg_to_rad(46.0)
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
	if is_on_floor():
		if Input.is_physical_key_pressed(KEY_SPACE):
			velocity.y = JUMP
		else:
			_step_up(delta)
	else:
		velocity.y -= GRAVITY * delta
	move_and_slide()
	if global_position.y < -20.0:
		global_position = Vector3(global_position.x, 2.0, global_position.z)
		velocity = Vector3.ZERO


# Se um degrau baixo bloqueia o passo, sobe o jogador para cima dele.
func _step_up(delta: float) -> void:
	var motion := Vector3(velocity.x, 0.0, velocity.z) * delta
	if motion.length() < 0.0005:
		return
	var t := global_transform
	var hit := KinematicCollision3D.new()
	if not test_move(t, motion, hit):
		return
	if hit.get_normal().y > 0.7:
		return
	var up := Vector3(0.0, STEP, 0.0)
	if test_move(t, up):
		return
	var t2 := t.translated(up)
	if test_move(t2, motion):
		return
	t2 = t2.translated(motion)
	var down := KinematicCollision3D.new()
	if not test_move(t2, -up, down):
		return
	if down.get_normal().y < 0.7:
		return
	global_position = t2.origin + down.get_travel()
