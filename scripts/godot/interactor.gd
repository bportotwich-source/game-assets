# Coloque num RayCast3D filho da câmera do jogador (target_position = Vector3(0, 0, -2)).
# Crie a ação "interact" no Input Map (ex.: tecla E / botão do controle).
extends RayCast3D

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("interact") and is_colliding():
		var n: Node = get_collider()
		while n and not (n is KitDoor):
			n = n.get_parent()
		if n:
			n.interact()
