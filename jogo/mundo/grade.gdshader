// Grade de 2 m do modo prefeito: linhas finas desenhadas num plano logo
// acima das calçadas. Some aos poucos longe do centro da vista.
shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, fog_disabled;

uniform vec4 cor : source_color = vec4(1.0, 0.92, 0.65, 0.45);
uniform float celula = 2.0;
uniform vec3 centro = vec3(0.0);
uniform float raio = 70.0;

varying vec3 wpos;

void vertex() {
	wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	vec2 g = wpos.xz / celula;
	vec2 d = abs(fract(g - 0.5) - 0.5) / fwidth(g);
	float linha = 1.0 - min(min(d.x, d.y), 1.0);
	float some = 1.0 - smoothstep(raio * 0.6, raio, distance(wpos.xz, centro.xz));
	ALBEDO = cor.rgb;
	ALPHA = cor.a * linha * some;
}
