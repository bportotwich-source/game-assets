# Porta do kit (Godot 4). Coloque este script num Node3D que seja o pai da folha
# (door_leaf_*.glb). O pivô da folha já está na dobradiça, então basta girar em Y.
# O nó precisa de um StaticBody3D/AnimatableBody3D filho com colisor para o jogador esbarrar.
extends Node3D
class_name KitDoor

@export var open_angle_deg: float = 70.0   # use o valor "open - closed" do building_layout.json
@export var duration: float = 0.35
@export var start_open: bool = false
@export var locked: bool = false

var is_open := false
var _closed_y: float
var _tween: Tween

func _ready() -> void:
	_closed_y = rotation.y
	if start_open:
		is_open = true
		rotation.y = _closed_y + deg_to_rad(open_angle_deg)

func interact() -> void:
	if locked:
		return
	set_open(not is_open)

func set_open(value: bool) -> void:
	is_open = value
	if _tween:
		_tween.kill()
	var target := _closed_y + (deg_to_rad(open_angle_deg) if is_open else 0.0)
	_tween = create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	_tween.tween_property(self, "rotation:y", target, duration)
