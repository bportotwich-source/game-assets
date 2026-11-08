# Editor de montagem: escolha peças de qualquer kit, encaixe na grade de 1 m
# (módulo de 2 m, andar de 3 m, do PADRAO_METRICAS.md), gire, mova, apague,
# salve e abra a montagem em JSON e entre nela para andar em primeira pessoa.
extends Node3D

const PlayerScript = preload("res://visitar/player.gd")
const Montador = preload("res://editor/montador.gd")

const SNAPS := [1.0, 2.0, 0.5, 0.25, 0.05]
const UNDO_MAX := 60
const AUTOSAVE := "user://montagem_autosave.json"
const PICK_LAYER := 2          # camada só das peças do editor (para clicar nelas)

var kits := PackedStringArray()
var cur_kit := ""
var _pieces_root: Node3D
var _ghost: Node3D
var _ghost_kit := ""
var _ghost_piece := ""
var _rot := 0.0                # graus, em passos de 90 (Shift: 45)
var _selected: Node3D
var _hovered: Node3D
var _level := 0
var _extra_h := 0.0
var _snap_i := 0
var _cursor := Vector3.ZERO
var _cursor_ok := false
var _attach_doors := true
var _undo: Array = []
var _file := ""
var _dirty := false

var _cam: Camera3D
var _target := Vector3(0, 0, 0)
var _yaw := 0.6
var _pitch := 0.75
var _dist := 30.0
var _orbiting := false
var _panning := false

var _grid: MeshInstance3D
var _grid_center := Vector3(INF, INF, INF)
var _marker: MeshInstance3D
var _ghost_mat: StandardMaterial3D
var _sel_mat: StandardMaterial3D
var _hover_mat: StandardMaterial3D

# Interface
var _panel: PanelContainer
var _kit_opt: OptionButton
var _search: LineEdit
var _list: ItemList
var _status: Label
var _help: Label
var _info: Label
var _dialog: FileDialog
var _preview_vp: SubViewport
var _preview_root: Node3D
var _preview_cam: Camera3D
var _preview_key := ""

# Andar
var _walking := false
var _walk_root: Node3D
var _player
var _walk_hud: Label


func _ready() -> void:
	Montador.make_world(self)
	_make_materials()
	_pieces_root = Node3D.new()
	_pieces_root.name = "Pecas"
	add_child(_pieces_root)
	_cam = Camera3D.new()
	_cam.fov = 60.0
	_cam.far = 800.0
	add_child(_cam)
	_cam.current = true
	_make_grid()
	_make_ui()
	kits = Montador.kit_list()
	for k in kits:
		_kit_opt.add_item(k)
	if kits.size() > 0:
		var start := kits.find("bangalo")
		_select_kit(maxi(start, 0))
	if FileAccess.file_exists(AUTOSAVE):
		var data = Montador.read_json(AUTOSAVE)
		if data is Dictionary:
			_deserialize(data.get("placements", []), Vector3.ZERO, true)
			_file = data.get("arquivo", "")
			_frame_all()
	_update_cam()
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE


func _exit_tree() -> void:
	# Durante o passeio as peças do editor ficam fora da árvore: libera aqui.
	if _walking and is_instance_valid(_pieces_root):
		_pieces_root.free()


# ---------------------------------------------------------------- materiais

func _make_materials() -> void:
	_ghost_mat = _overlay(Color(0.2, 1.0, 0.45, 0.35))
	_sel_mat = _overlay(Color(1.0, 0.8, 0.1, 0.4))
	_hover_mat = _overlay(Color(1, 1, 1, 0.18))


func _overlay(c: Color) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.albedo_color = c
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	return m


func _set_overlay(n: Node, m: Material) -> void:
	for mi in n.find_children("*", "MeshInstance3D", true, false):
		mi.material_overlay = m
	if n is MeshInstance3D:
		n.material_overlay = m


# ---------------------------------------------------------------- grade

func _make_grid() -> void:
	_grid = MeshInstance3D.new()
	_grid.mesh = ImmediateMesh.new()
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.vertex_color_use_as_albedo = true
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	_grid.material_override = m
	_grid.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_grid)
	_marker = MeshInstance3D.new()
	var b := BoxMesh.new()
	b.size = Vector3(0.25, 0.04, 0.25)
	_marker.mesh = b
	_marker.material_override = _overlay(Color(1, 0.35, 0.2, 0.9))
	add_child(_marker)


func _rebuild_grid(center: Vector3) -> void:
	var c := Vector3(snappedf(center.x, 2.0), _level_y(), snappedf(center.z, 2.0))
	if c.is_equal_approx(_grid_center):
		return
	_grid_center = c
	var im: ImmediateMesh = _grid.mesh
	im.clear_surfaces()
	im.surface_begin(Mesh.PRIMITIVE_LINES)
	var r := 24
	var y := c.y + 0.012
	for i in range(-r, r + 1):
		var x := c.x + i
		var z := c.z + i
		var major := int(roundf(x)) % 2 == 0
		var col := Color(0.05, 0.08, 0.05, 0.45 if major else 0.18)
		if is_zero_approx(x):
			col = Color(0.3, 0.5, 1.0, 0.8)
		im.surface_set_color(col)
		im.surface_add_vertex(Vector3(x, y, c.z - r))
		im.surface_add_vertex(Vector3(x, y, c.z + r))
		major = int(roundf(z)) % 2 == 0
		col = Color(0.05, 0.08, 0.05, 0.45 if major else 0.18)
		if is_zero_approx(z):
			col = Color(1.0, 0.35, 0.3, 0.8)
		im.surface_set_color(col)
		im.surface_add_vertex(Vector3(c.x - r, y, z))
		im.surface_add_vertex(Vector3(c.x + r, y, z))
	im.surface_end()


func _level_y() -> float:
	return _level * Montador.FLOOR_H + _extra_h


func _snap() -> float:
	return SNAPS[_snap_i]


# ---------------------------------------------------------------- interface

func _make_ui() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)

	_panel = PanelContainer.new()
	_panel.set_anchors_preset(Control.PRESET_LEFT_WIDE)
	_panel.custom_minimum_size = Vector2(330, 0)
	layer.add_child(_panel)
	var margin := MarginContainer.new()
	for s in ["left", "right", "top", "bottom"]:
		margin.add_theme_constant_override("margin_" + s, 10)
	_panel.add_child(margin)
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 6)
	margin.add_child(v)

	var title := Label.new()
	title.text = "Montar prédio"
	title.add_theme_font_size_override("font_size", 22)
	v.add_child(title)

	var files := HBoxContainer.new()
	v.add_child(files)
	files.add_child(_button("Novo", _on_new))
	files.add_child(_button("Abrir…", _on_open))
	files.add_child(_button("Salvar", _on_save))
	files.add_child(_button("Salvar como…", _on_save_as))

	var edit := HBoxContainer.new()
	v.add_child(edit)
	edit.add_child(_button("Desfazer", _on_undo))
	edit.add_child(_button("Apagar", _delete_selected))
	edit.add_child(_button("Enquadrar", _frame_all))

	var kl := Label.new()
	kl.text = "Kit"
	v.add_child(kl)
	_kit_opt = OptionButton.new()
	_kit_opt.item_selected.connect(_select_kit)
	v.add_child(_kit_opt)

	_search = LineEdit.new()
	_search.placeholder_text = "Buscar peça (ex.: wall, door, roof)"
	_search.clear_button_enabled = true
	_search.text_changed.connect(func(_t): _fill_list())
	v.add_child(_search)

	_list = ItemList.new()
	_list.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_list.item_selected.connect(_on_piece_chosen)
	v.add_child(_list)

	var pc := SubViewportContainer.new()
	pc.custom_minimum_size = Vector2(300, 170)
	pc.stretch = true
	v.add_child(pc)
	_preview_vp = SubViewport.new()
	_preview_vp.own_world_3d = true
	_preview_vp.transparent_bg = false
	pc.add_child(_preview_vp)
	var penv := Environment.new()
	penv.background_mode = Environment.BG_COLOR
	penv.background_color = Color(0.2, 0.22, 0.25)
	penv.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	penv.ambient_light_color = Color(0.9, 0.9, 0.9)
	penv.ambient_light_energy = 0.6
	var pwe := WorldEnvironment.new()
	pwe.environment = penv
	_preview_vp.add_child(pwe)
	var pl := DirectionalLight3D.new()
	pl.rotation_degrees = Vector3(-45, -30, 0)
	_preview_vp.add_child(pl)
	_preview_root = Node3D.new()
	_preview_vp.add_child(_preview_root)
	_preview_cam = Camera3D.new()
	_preview_cam.fov = 40.0
	_preview_vp.add_child(_preview_cam)

	_info = Label.new()
	_info.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	v.add_child(_info)

	var cb := CheckBox.new()
	cb.text = "Pôr a folha da porta junto com a parede"
	cb.button_pressed = true
	cb.toggled.connect(func(on): _attach_doors = on; _refresh_ghost())
	v.add_child(cb)

	v.add_child(_button("Inserir o prédio inteiro deste kit no cursor", _insert_whole_kit))
	var walk := _button("Andar dentro (Tab)", _toggle_walk)
	walk.add_theme_font_size_override("font_size", 18)
	v.add_child(walk)
	v.add_child(_button("Voltar ao menu", _to_menu))

	_status = Label.new()
	_status.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_status.offset_left = 345
	_status.offset_top = -56
	_status.offset_bottom = -8
	_status.add_theme_color_override("font_outline_color", Color.BLACK)
	_status.add_theme_constant_override("outline_size", 6)
	layer.add_child(_status)

	_help = Label.new()
	_help.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	_help.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	_help.offset_top = 10
	_help.offset_right = -14
	_help.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_help.add_theme_color_override("font_outline_color", Color.BLACK)
	_help.add_theme_constant_override("outline_size", 6)
	_help.text = "\n".join([
		"Clique numa peça da lista e clique no chão para colocar",
		"Q / E: girar 90° (Shift: 45°) | Esc: soltar a peça",
		"Clique numa peça colocada: selecionar | Delete: apagar",
		"Setas: mover a seleção | M: mover com o mouse | Ctrl+D: duplicar",
		"C: pegar o tipo da peça sob o mouse | H: pegar a altura dela",
		"Page Up / Page Down: andar de cima / de baixo (3 m)",
		"Ctrl + Page Up / Page Down: ajuste fino da altura (5 cm)",
		"G: passo da grade | Ctrl+Z: desfazer | Ctrl+S: salvar",
		"Botão direito: girar a câmera | do meio ou Shift+direito: arrastar",
		"Roda: zoom | WASD: mover a câmera | F: enquadrar tudo",
		"Tab: andar dentro (nasce onde está o mouse) | F1: esconder ajuda",
	])
	layer.add_child(_help)

	_walk_hud = Label.new()
	_walk_hud.position = Vector2(16, 12)
	_walk_hud.add_theme_color_override("font_outline_color", Color.BLACK)
	_walk_hud.add_theme_constant_override("outline_size", 6)
	_walk_hud.text = "Andando na sua montagem. Tab: voltar ao editor\nClique: prender o mouse | WASD: andar | Shift: correr | Espaço: pular\nE ou clique: abrir/fechar porta | F: voar (Espaço sobe, Q desce) | Esc: soltar o mouse"
	_walk_hud.visible = false
	layer.add_child(_walk_hud)

	_dialog = FileDialog.new()
	_dialog.access = FileDialog.ACCESS_FILESYSTEM
	_dialog.use_native_dialog = true
	_dialog.filters = PackedStringArray(["*.json ; Montagem (JSON)"])
	_dialog.size = Vector2i(900, 600)
	_dialog.file_selected.connect(_on_file_chosen)
	layer.add_child(_dialog)


func _button(text: String, cb: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.pressed.connect(cb)
	b.focus_mode = Control.FOCUS_NONE
	return b


func _select_kit(i: int) -> void:
	if i < 0 or i >= kits.size():
		return
	cur_kit = kits[i]
	_kit_opt.select(i)
	_fill_list()


func _fill_list() -> void:
	_list.clear()
	var q := _search.text.strip_edges().to_lower()
	for p in Montador.piece_list(cur_kit):
		if p == "player_scale_ref":
			continue
		if q == "" or p.to_lower().contains(q):
			_list.add_item(p)


func _on_piece_chosen(i: int) -> void:
	_set_ghost(cur_kit, _list.get_item_text(i))
	_list.release_focus()


# ---------------------------------------------------------------- peça fantasma

func _set_ghost(kit: String, piece: String) -> void:
	_clear_ghost()
	_select(null)
	var ps := Montador.piece_scene(kit, piece)
	if ps == null:
		return
	_ghost_kit = kit
	_ghost_piece = piece
	_ghost = Node3D.new()
	_ghost.add_child(ps.instantiate())
	var comp = _companion(kit, piece)
	if comp != null:
		var lps := Montador.piece_scene(kit, comp["leaf"])
		if lps:
			var leaf: Node3D = lps.instantiate()
			leaf.position = comp["offset"]
			leaf.rotation.y = deg_to_rad(comp["rot"])
			_ghost.add_child(leaf)
	add_child(_ghost)
	_set_overlay(_ghost, _ghost_mat)
	_show_preview(kit, piece)


func _refresh_ghost() -> void:
	if _ghost:
		_set_ghost(_ghost_kit, _ghost_piece)


func _clear_ghost() -> void:
	if _ghost:
		_ghost.queue_free()
	_ghost = null
	_ghost_piece = ""


func _companion(kit: String, piece: String):
	if not _attach_doors:
		return null
	return Montador.door_companions(kit).get(piece)


func _show_preview(kit: String, piece: String) -> void:
	var key := kit + "/" + piece
	if key == _preview_key:
		return
	_preview_key = key
	for c in _preview_root.get_children():
		c.queue_free()
	var ps := Montador.piece_scene(kit, piece)
	if ps == null:
		return
	var inst: Node3D = ps.instantiate()
	_preview_root.add_child(inst)
	var box := _local_aabb(inst)
	inst.position = -box.get_center()
	var r := maxf(box.size.length() * 0.5, 0.3)
	_preview_cam.position = Vector3(0, r * 0.55, r * 2.9)
	_preview_cam.look_at(Vector3.ZERO)
	_info.text = "%s / %s\n%s × %s × %s m (largura × altura × fundo)" % [
		kit, piece, _num(box.size.x), _num(box.size.y), _num(box.size.z)]


func _local_aabb(root: Node3D) -> AABB:
	var box := AABB()
	var first := true
	var inv := root.global_transform.affine_inverse()
	for mi in root.find_children("*", "MeshInstance3D", true, false):
		if mi.mesh == null:
			continue
		var b: AABB = (inv * mi.global_transform) * mi.get_aabb()
		box = b if first else box.merge(b)
		first = false
	return box


func _num(x: float) -> String:
	return ("%.2f" % x).replace(".", ",")


# ---------------------------------------------------------------- peças colocadas

# Cria uma peça colocada. Peças são Node3D com metadados kit/piece (e
# open_delta nas folhas de porta); filhos colocados são folhas presas à parede.
func _make_placed(kit: String, piece: String, pos: Vector3, rot_deg: float, parent: Node3D = null, local := false) -> Node3D:
	var ps := Montador.piece_scene(kit, piece)
	if ps == null:
		return null
	var n := Node3D.new()
	n.name = piece
	n.set_meta("kit", kit)
	n.set_meta("piece", piece)
	if Montador.is_door_leaf(piece):
		n.set_meta("open_delta", 85.0)
	(parent if parent else _pieces_root).add_child(n)
	if local:
		n.position = pos
		n.rotation.y = deg_to_rad(rot_deg)
	else:
		n.global_position = pos
		n.global_rotation = Vector3(0, deg_to_rad(rot_deg), 0)
	var inst: Node3D = ps.instantiate()
	n.add_child(inst)
	var body := StaticBody3D.new()
	body.collision_layer = 1 << (PICK_LAYER - 1)
	body.collision_mask = 0
	inst.add_child(body)
	Montador.add_shapes(inst, body)
	return n


func _place_ghost() -> void:
	if _ghost == null or not _cursor_ok:
		return
	_push_undo()
	var n := _make_placed(_ghost_kit, _ghost_piece, _ghost.global_position, _rot)
	var comp = _companion(_ghost_kit, _ghost_piece)
	if n and comp != null:
		var leaf := _make_placed(_ghost_kit, comp["leaf"], comp["offset"], comp["rot"], n, true)
		if leaf:
			leaf.set_meta("open_delta", comp["open"])
	_changed()


func _placed_of(node: Node) -> Node3D:
	while node and not node.has_meta("piece"):
		node = node.get_parent()
	return node as Node3D


func _select(n: Node3D) -> void:
	if _selected and is_instance_valid(_selected):
		_set_overlay(_selected, null)
	_selected = n
	if _selected:
		_set_overlay(_selected, _sel_mat)
		_show_preview(n.get_meta("kit"), n.get_meta("piece"))


func _set_hover(n: Node3D) -> void:
	if n == _hovered:
		return
	if _hovered and is_instance_valid(_hovered) and _hovered != _selected:
		_set_overlay(_hovered, null)
	_hovered = n
	if _hovered and _hovered != _selected:
		_set_overlay(_hovered, _hover_mat)


func _delete_selected() -> void:
	if _selected == null:
		return
	_push_undo()
	var n := _selected
	_select(null)
	_hovered = null
	n.get_parent().remove_child(n)
	n.queue_free()
	_changed()


func _rotate_selected(deg: float) -> void:
	_push_undo()
	_selected.rotation.y += deg_to_rad(deg)
	_changed()


func _move_selected(d: Vector3) -> void:
	_push_undo()
	_selected.global_position += d
	_changed()


# Seta para cima = o eixo do mundo mais perto da direção da câmera.
func _arrow_dir(key: int) -> Vector3:
	var f := -_cam.global_transform.basis.z
	f.y = 0
	var fwd := Vector3(signf(f.x), 0, 0) if absf(f.x) > absf(f.z) else Vector3(0, 0, signf(f.z))
	var right := Vector3(-fwd.z, 0, fwd.x)
	match key:
		KEY_UP: return fwd
		KEY_DOWN: return -fwd
		KEY_RIGHT: return right
		KEY_LEFT: return -right
	return Vector3.ZERO


# ---------------------------------------------------------------- JSON

func _serialize() -> Array:
	var out := []
	for n in _pieces_root.get_children():
		if n.is_queued_for_deletion():
			continue
		var idx := out.size()
		out.append(_entry(n))
		for c in n.get_children():
			if c.has_meta("piece"):
				var e := _entry(c)
				e["parent"] = idx
				out.append(e)
	return out


func _entry(n: Node3D) -> Dictionary:
	var p := n.global_position
	var rot := snappedf(fposmod(rad_to_deg(n.global_rotation.y), 360.0), 0.01)
	if is_equal_approx(rot, 360.0):
		rot = 0.0
	var e := {
		"kit": n.get_meta("kit"),
		"piece": n.get_meta("piece"),
		"pos": [snappedf(p.x, 0.001), snappedf(p.y, 0.001), snappedf(p.z, 0.001)],
		"rotY": rot,
	}
	if n.has_meta("open_delta"):
		e["door"] = {"closed": rot, "open": rot + float(n.get_meta("open_delta"))}
	return e


func _deserialize(arr: Array, offset: Vector3, clear: bool, default_kit := "") -> void:
	if clear:
		_select(null)
		_hovered = null
		for c in _pieces_root.get_children():
			_pieces_root.remove_child(c)
			c.queue_free()
	var made := []
	for e in arr:
		if not (e is Dictionary) or not e.has("piece") or e["piece"] == "player_scale_ref":
			made.append(null)
			continue
		var kit: String = e.get("kit", default_kit)
		var pos := Vector3(float(e["pos"][0]), float(e["pos"][1]), float(e["pos"][2])) + offset
		var rot := float(e.get("rotY", 0.0))
		if e.has("door"):
			rot = float(e["door"]["closed"])
		var n := _make_placed(kit, e["piece"], pos, rot)
		if n:
			if e.has("door"):
				n.set_meta("open_delta", float(e["door"]["open"]) - float(e["door"]["closed"]))
			elif n.has_meta("open_delta"):
				n.remove_meta("open_delta")
			var pi := int(e.get("parent", -1))
			if pi >= 0 and pi < made.size() and made[pi] != null:
				n.reparent(made[pi], true)
		made.append(n)


func _document() -> Dictionary:
	return {
		"format": "game-assets-montagem",
		"version": 1,
		"grid": {"snap": Montador.GRID_STEP, "module_width": Montador.MODULE, "floor_height": Montador.FLOOR_H},
		"arquivo": _file,
		"placements": _serialize(),
	}


func _write(path: String) -> bool:
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		return false
	f.store_string(JSON.stringify(_document(), " "))
	return true


func _changed() -> void:
	_dirty = true
	_write(AUTOSAVE)


func _push_undo() -> void:
	_undo.append(_serialize())
	if _undo.size() > UNDO_MAX:
		_undo.pop_front()


func _on_undo() -> void:
	if _undo.is_empty():
		return
	_deserialize(_undo.pop_back(), Vector3.ZERO, true)
	_changed()


func _on_new() -> void:
	_push_undo()
	_deserialize([], Vector3.ZERO, true)
	_file = ""
	_changed()


func _default_dir() -> String:
	var d := OS.get_system_dir(OS.SYSTEM_DIR_DOCUMENTS).path_join("Montagens GameAssets")
	DirAccess.make_dir_recursive_absolute(d)
	return d


func _on_open() -> void:
	_dialog.file_mode = FileDialog.FILE_MODE_OPEN_FILE
	_dialog.title = "Abrir montagem"
	_dialog.current_dir = _default_dir() if _file == "" else _file.get_base_dir()
	_dialog.popup_centered()


func _on_save() -> void:
	if _file == "":
		_on_save_as()
	elif _write(_file):
		_dirty = false
		_write(AUTOSAVE)


func _on_save_as() -> void:
	_dialog.file_mode = FileDialog.FILE_MODE_SAVE_FILE
	_dialog.title = "Salvar montagem"
	_dialog.current_dir = _default_dir() if _file == "" else _file.get_base_dir()
	_dialog.current_file = "minha_casa.json" if _file == "" else _file.get_file()
	_dialog.popup_centered()


func _on_file_chosen(path: String) -> void:
	if _dialog.file_mode == FileDialog.FILE_MODE_SAVE_FILE:
		if not path.ends_with(".json"):
			path += ".json"
		_file = path
		_on_save()
		return
	var data = Montador.read_json(path)
	if not (data is Dictionary) or not data.has("placements"):
		push_warning("Arquivo inválido: " + path)
		return
	_push_undo()
	# Um building_layout.json de kit não diz o kit de cada peça: usa o kit escolhido.
	_deserialize(data["placements"], Vector3.ZERO, true, cur_kit)
	_file = path
	_frame_all()
	_changed()
	_dirty = false


func _insert_whole_kit() -> void:
	var lay := Montador.kit_layout(cur_kit)
	if lay.is_empty():
		return
	_push_undo()
	var off := Vector3(snappedf(_target.x, 2.0), _level_y(), snappedf(_target.z, 2.0))
	if _cursor_ok:
		off = Vector3(snappedf(_cursor.x, 2.0), _level_y(), snappedf(_cursor.z, 2.0))
	_deserialize(lay, off, false, cur_kit)
	_changed()


func _to_menu() -> void:
	get_tree().change_scene_to_file("res://menu/menu.tscn")


# ---------------------------------------------------------------- câmera

func _update_cam() -> void:
	_pitch = clampf(_pitch, 0.08, 1.5)
	_dist = clampf(_dist, 2.0, 250.0)
	var dir := Vector3(sin(_yaw) * cos(_pitch), sin(_pitch), cos(_yaw) * cos(_pitch))
	_cam.global_position = _target + dir * _dist
	_cam.look_at(_target)


func _frame_all() -> void:
	var first := true
	var box := AABB()
	for n in _pieces_root.get_children():
		var p: Vector3 = n.global_position
		box = AABB(p, Vector3.ZERO) if first else box.expand(p)
		first = false
	if first:
		_target = Vector3.ZERO
		_dist = 30.0
	else:
		_target = box.get_center()
		_target.y = 0.0
		_dist = maxf(15.0, box.size.length() * 1.3)
	_update_cam()


# ---------------------------------------------------------------- entrada

func _mouse_over_ui() -> bool:
	var mp := get_viewport().get_mouse_position()
	if _panel.get_global_rect().has_point(mp):
		return true
	return _dialog.visible


func _input(event: InputEvent) -> void:
	# Tab vem antes da interface, que usaria a tecla para trocar o foco.
	if event is InputEventKey and event.pressed and not event.echo and event.physical_keycode == KEY_TAB:
		if get_viewport().gui_get_focus_owner() is LineEdit and not _walking:
			return
		get_viewport().set_input_as_handled()
		_toggle_walk()


func _unhandled_input(event: InputEvent) -> void:
	if _walking:
		return
	if event is InputEventMouseButton:
		_on_mouse_button(event)
	elif event is InputEventMouseMotion:
		if _orbiting:
			_yaw -= event.relative.x * 0.006
			_pitch += event.relative.y * 0.006
			_update_cam()
		elif _panning:
			var k := _dist * 0.0016
			var b := _cam.global_transform.basis
			var right := b.x
			var fwd := Vector3(-b.z.x, 0, -b.z.z).normalized()
			_target += (-right * event.relative.x + fwd * event.relative.y) * k
			_update_cam()
	elif event is InputEventKey and event.pressed:
		_on_key(event)


func _on_mouse_button(e: InputEventMouseButton) -> void:
	match e.button_index:
		MOUSE_BUTTON_RIGHT:
			if e.shift_pressed:
				_panning = e.pressed
			else:
				_orbiting = e.pressed
				if not e.pressed:
					_panning = false
		MOUSE_BUTTON_MIDDLE:
			_panning = e.pressed
		MOUSE_BUTTON_WHEEL_UP:
			if e.pressed:
				_dist *= 0.88
				_update_cam()
		MOUSE_BUTTON_WHEEL_DOWN:
			if e.pressed:
				_dist /= 0.88
				_update_cam()
		MOUSE_BUTTON_LEFT:
			if not e.pressed:
				return
			get_viewport().gui_release_focus()
			if _ghost:
				_place_ghost()
			else:
				_select(_pick())


func _on_key(e: InputEventKey) -> void:
	var k := e.physical_keycode
	if e.ctrl_pressed:
		match k:
			KEY_Z: _on_undo()
			KEY_S: _on_save()
			KEY_O: _on_open()
			KEY_N: _on_new()
			KEY_D:
				if _selected:
					_rot = rad_to_deg(_selected.global_rotation.y)
					_set_ghost(_selected.get_meta("kit"), _selected.get_meta("piece"))
			KEY_PAGEUP: _change_height(0.05)
			KEY_PAGEDOWN: _change_height(-0.05)
		return
	if e.echo and not k in [KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT]:
		return
	var step := 45.0 if e.shift_pressed else 90.0
	match k:
		KEY_Q, KEY_E:
			var d := step if k == KEY_Q else -step
			if _ghost:
				_rot = fposmod(_rot + d, 360.0)
			elif _selected:
				_rotate_selected(d)
		KEY_ESCAPE:
			if _ghost:
				_clear_ghost()
			else:
				_select(null)
		KEY_DELETE, KEY_BACKSPACE, KEY_X:
			_delete_selected()
		KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT:
			if _selected:
				_move_selected(_arrow_dir(k) * _snap())
		KEY_PAGEUP, KEY_PAGEDOWN:
			var up := 1 if k == KEY_PAGEUP else -1
			if _selected:
				_move_selected(Vector3(0, up * Montador.FLOOR_H, 0))
			else:
				_level += up
		KEY_G:
			_snap_i = (_snap_i + 1) % SNAPS.size()
		KEY_M:
			if _selected:
				var s := _selected
				_rot = rad_to_deg(s.global_rotation.y)
				var kit: String = s.get_meta("kit")
				var piece: String = s.get_meta("piece")
				_delete_selected()
				_set_ghost(kit, piece)
		KEY_C:
			var h := _pick()
			if h:
				_rot = rad_to_deg(h.global_rotation.y)
				_set_ghost(h.get_meta("kit"), h.get_meta("piece"))
		KEY_H:
			var h := _pick()
			if h:
				var y: float = h.global_position.y
				_level = int(floor((y + 0.001) / Montador.FLOOR_H))
				_extra_h = snappedf(y - _level * Montador.FLOOR_H, 0.001)
		KEY_F:
			_frame_all()
		KEY_F1:
			_help.visible = not _help.visible


func _change_height(d: float) -> void:
	if _selected:
		_move_selected(Vector3(0, d, 0))
	else:
		_extra_h = snappedf(_extra_h + d, 0.001)


func _mouse_ray() -> Array:
	var mp := get_viewport().get_mouse_position()
	return [_cam.project_ray_origin(mp), _cam.project_ray_normal(mp)]


func _pick() -> Node3D:
	if _mouse_over_ui():
		return null
	var r := _mouse_ray()
	var q := PhysicsRayQueryParameters3D.create(r[0], r[0] + r[1] * 1000.0, 1 << (PICK_LAYER - 1))
	var hit := get_world_3d().direct_space_state.intersect_ray(q)
	if hit.is_empty():
		return null
	return _placed_of(hit["collider"])


# ---------------------------------------------------------------- quadro a quadro

func _process(delta: float) -> void:
	if _walking:
		return
	_move_camera_keys(delta)
	var r := _mouse_ray()
	var plane := Plane(Vector3.UP, _level_y())
	var p = plane.intersects_ray(r[0], r[1])
	_cursor_ok = p != null and not _mouse_over_ui()
	if p != null:
		var s := _snap()
		_cursor = Vector3(snappedf(p.x, s), _level_y(), snappedf(p.z, s))
		_rebuild_grid(_cursor)
	_marker.visible = _cursor_ok and _ghost == null
	_marker.global_position = _cursor
	if _ghost:
		_ghost.visible = _cursor_ok
		_ghost.global_position = _cursor
		_ghost.rotation.y = deg_to_rad(_rot)
		_set_hover(null)
	else:
		_set_hover(_pick())
	_preview_root.rotate_y(delta * 0.6)
	_update_status()


func _move_camera_keys(delta: float) -> void:
	if get_viewport().gui_get_focus_owner() is LineEdit:
		return
	var v := Vector2.ZERO
	if Input.is_physical_key_pressed(KEY_W): v.y -= 1
	if Input.is_physical_key_pressed(KEY_S): v.y += 1
	if Input.is_physical_key_pressed(KEY_A): v.x -= 1
	if Input.is_physical_key_pressed(KEY_D): v.x += 1
	if v == Vector2.ZERO:
		return
	var speed := maxf(6.0, _dist * 0.8)
	var fwd := Vector3(-sin(_yaw), 0, -cos(_yaw))
	var right := Vector3(cos(_yaw), 0, -sin(_yaw))
	_target += (right * v.x - fwd * v.y) * speed * delta
	_update_cam()


func _update_status() -> void:
	var fname := _file.get_file() if _file != "" else "sem nome"
	var t := "Montagem: %s%s | %d peças | Grade: %s m | Altura do plano: %s m (andar %d) | Giro: %d°" % [
		fname, " *" if _dirty else "", _pieces_root.get_child_count(), _num(_snap()), _num(_level_y()), _level, int(_rot)]
	t += "\nCursor: x %s  z %s" % [_num(_cursor.x), _num(_cursor.z)]
	if _ghost:
		t += " | Colocando %s / %s (clique para pôr, Esc para soltar)" % [_ghost_kit, _ghost_piece]
	elif _selected:
		var sp := _selected.global_position
		t += " | Selecionada: %s / %s em (%s, %s, %s), %d°" % [_selected.get_meta("kit"), _selected.get_meta("piece"),
			_num(sp.x), _num(sp.y), _num(sp.z), int(roundf(fposmod(rad_to_deg(_selected.global_rotation.y), 360.0)))]
	_status.text = t


# ---------------------------------------------------------------- andar dentro

func _toggle_walk() -> void:
	if _walking:
		_stop_walk()
	else:
		_start_walk()


func _start_walk() -> void:
	var spawn := _cursor if _cursor_ok else Vector3(_target.x, _level_y(), _target.z)
	_clear_ghost()
	_select(null)
	_set_hover(null)
	var data := _serialize()
	_walking = true
	remove_child(_pieces_root)
	_grid.visible = false
	_marker.visible = false
	_panel.visible = false
	_status.visible = false
	_help.visible = false
	_walk_hud.visible = true
	_walk_root = Node3D.new()
	_walk_root.name = "Passeio"
	add_child(_walk_root)
	Montador.build_walkable(data, _walk_root)
	_player = PlayerScript.new()
	_player.name = "Jogador"
	add_child(_player)
	_player.respawn(spawn + Vector3(0, 0.1, 0))
	_player.rotation.y = _yaw


func _stop_walk() -> void:
	_walking = false
	if _player:
		_player.queue_free()
		_player = null
	if _walk_root:
		_walk_root.queue_free()
		_walk_root = null
	add_child(_pieces_root)
	_cam.current = true
	_grid.visible = true
	_panel.visible = true
	_status.visible = true
	_help.visible = true
	_walk_hud.visible = false
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
