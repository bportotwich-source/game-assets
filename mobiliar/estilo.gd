# Estilo das telas do Modo Mobiliar: o mesmo das telas de craft do Recomeço
# (painéis escuros, cabeçalho cor de brasa, fonte Barlow).
extends RefCounted

const CHAO := Color(0.05, 0.05, 0.045, 0.92)
const PAINEL := Color(0.12, 0.12, 0.105, 0.96)
const LINHA := Color(0.23, 0.23, 0.19)
const TEXTO := Color(0.91, 0.89, 0.83)
const APAGADO := Color(0.6, 0.58, 0.52)
const FERRUGEM := Color(0.85, 0.51, 0.17)
const BRASA := Color(0.95, 0.64, 0.23)
const OK := Color(0.55, 0.76, 0.42)
const FALTA := Color(0.89, 0.45, 0.36)
const SLOT := Color(0.17, 0.17, 0.145)
const TINTA := Color(0.1, 0.07, 0.035)

static var _fontes := {}


static func fonte(tipo := "texto") -> Font:
	if not _fontes.has(tipo):
		var arq: String = {"titulo": "BarlowCondensed-Bold", "rotulo": "BarlowCondensed-SemiBold",
			"forte": "Barlow-Medium"}.get(tipo, "Barlow-Regular")
		_fontes[tipo] = load("res://mobiliar/fontes/%s.ttf" % arq)
	return _fontes[tipo]


static func caixa(fundo: Color, borda: Color, margem := 8, largura := 1) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = fundo
	s.border_color = borda
	s.set_border_width_all(largura)
	s.set_corner_radius_all(3)
	s.set_content_margin_all(margem)
	return s


static func tema() -> Theme:
	var t := Theme.new()
	t.default_font = fonte()
	t.default_font_size = 16
	t.set_color("font_color", "Label", TEXTO)
	var normal := caixa(Color(0, 0, 0, 0), Color(0.35, 0.34, 0.29), 6)
	normal.content_margin_left = 12
	normal.content_margin_right = 12
	var sobre: StyleBoxFlat = normal.duplicate()
	sobre.bg_color = Color(0.25, 0.24, 0.2)
	var apertado: StyleBoxFlat = normal.duplicate()
	apertado.bg_color = SLOT
	apertado.border_color = BRASA
	var parado: StyleBoxFlat = normal.duplicate()
	parado.border_color = LINHA
	for tipo in ["Button", "OptionButton"]:
		t.set_stylebox("normal", tipo, normal)
		t.set_stylebox("hover", tipo, sobre)
		t.set_stylebox("pressed", tipo, apertado)
		t.set_stylebox("hover_pressed", tipo, apertado)
		t.set_stylebox("disabled", tipo, parado)
		t.set_stylebox("focus", tipo, StyleBoxEmpty.new())
		t.set_font("font", tipo, fonte("rotulo"))
		t.set_font_size("font_size", tipo, 17)
		t.set_color("font_color", tipo, TEXTO)
		t.set_color("font_hover_color", tipo, TEXTO)
		t.set_color("font_pressed_color", tipo, BRASA)
		t.set_color("font_hover_pressed_color", tipo, BRASA)
		t.set_color("font_focus_color", tipo, TEXTO)
		t.set_color("font_disabled_color", tipo, Color(0.45, 0.43, 0.38))
	t.set_stylebox("panel", "PanelContainer", caixa(PAINEL, LINHA, 10))
	t.set_stylebox("normal", "LineEdit", caixa(SLOT, LINHA, 6))
	t.set_stylebox("focus", "LineEdit", caixa(SLOT, BRASA, 6))
	t.set_color("font_color", "LineEdit", TEXTO)
	t.set_color("font_placeholder_color", "LineEdit", APAGADO)
	t.set_stylebox("panel", "PopupMenu", caixa(PAINEL, LINHA, 6))
	t.set_color("font_color", "PopupMenu", TEXTO)
	t.set_color("font_hover_color", "PopupMenu", BRASA)
	return t


# Botão de ação principal (Salvar): cheio, cor de brasa.
static func principal(b: Button) -> void:
	var n := caixa(BRASA, FERRUGEM, 6)
	n.content_margin_left = 14
	n.content_margin_right = 14
	var h: StyleBoxFlat = n.duplicate()
	h.bg_color = Color(1.0, 0.72, 0.33)
	b.add_theme_stylebox_override("normal", n)
	b.add_theme_stylebox_override("hover", h)
	b.add_theme_stylebox_override("pressed", h)
	for c in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color"]:
		b.add_theme_color_override(c, TINTA)


static func titulo(texto: String, tamanho := 22, cor := BRASA) -> Label:
	var l := Label.new()
	l.text = texto.to_upper()
	l.add_theme_font_override("font", fonte("titulo"))
	l.add_theme_font_size_override("font_size", tamanho)
	l.add_theme_color_override("font_color", cor)
	return l


static func rotulo(texto: String) -> Label:
	var l := Label.new()
	l.text = texto.to_upper()
	l.add_theme_font_override("font", fonte("rotulo"))
	l.add_theme_font_size_override("font_size", 14)
	l.add_theme_color_override("font_color", APAGADO)
	return l
