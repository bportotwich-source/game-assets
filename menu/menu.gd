# Tela inicial: escolher entre montar um prédio com as peças ou visitar os kits prontos.
extends Control


func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var bg := ColorRect.new()
	bg.color = Color(0.16, 0.19, 0.24)
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	var center := CenterContainer.new()
	center.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(center)
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 18)
	center.add_child(v)
	var title := Label.new()
	title.text = "Game Assets"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 44)
	v.add_child(title)
	var sub := Label.new()
	sub.text = "Peças modulares de prédios, todas na mesma grade"
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(sub)
	v.add_child(_big("Montar um prédio com as peças", "res://editor/editor.tscn"))
	v.add_child(_big("Visitar os prédios prontos", "res://visitar/main.tscn"))
	var quit := _big("Sair", "")
	v.add_child(quit)


func _big(text: String, scene: String) -> Button:
	var b := Button.new()
	b.text = text
	b.custom_minimum_size = Vector2(440, 64)
	b.add_theme_font_size_override("font_size", 22)
	if scene == "":
		b.pressed.connect(func(): get_tree().quit())
	else:
		b.pressed.connect(func(): get_tree().change_scene_to_file(scene))
	return b
