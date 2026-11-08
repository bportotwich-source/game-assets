// Encardido da cidade abandonada: segunda passada que multiplica a cor da
// peça. Mais sujeira perto do chão, manchas soltas e escorridos verticais
// nas paredes. "forca" vem de ruinas.gd (0 = limpo), em poucos níveis.
shader_type spatial;
render_mode blend_mul, unshaded, depth_draw_never, cull_back, fog_disabled, shadows_disabled;

uniform float forca = 0.0;
uniform vec3 cor_sujeira : source_color = vec3(0.40, 0.36, 0.30);

varying vec3 wpos;
varying vec3 wnorm;

float hash(vec3 p) {
	p = fract(p * 0.3183099 + 0.1);
	p *= 17.0;
	return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
}

float ruido(vec3 x) {
	vec3 i = floor(x);
	vec3 f = fract(x);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(mix(hash(i), hash(i + vec3(1, 0, 0)), f.x),
	               mix(hash(i + vec3(0, 1, 0)), hash(i + vec3(1, 1, 0)), f.x), f.y),
	           mix(mix(hash(i + vec3(0, 0, 1)), hash(i + vec3(1, 0, 1)), f.x),
	               mix(hash(i + vec3(0, 1, 1)), hash(i + vec3(1, 1, 1)), f.x), f.y), f.z);
}

void vertex() {
	wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	wnorm = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

void fragment() {
	float manchas = ruido(wpos * 0.7) * 0.6 + ruido(wpos * 2.3) * 0.4;
	float chao = 1.0 - smoothstep(0.0, 1.8, wpos.y);
	float parede = 1.0 - abs(wnorm.y);
	float escorrido = smoothstep(0.55, 0.9, ruido(vec3(wpos.x * 4.0 + wpos.z * 4.0, wpos.y * 0.25, wpos.z * 4.0 - wpos.x * 4.0))) * parede;
	float topo = smoothstep(0.7, 1.0, wnorm.y) * smoothstep(0.4, 0.8, manchas);
	float q = 0.45 * chao + 0.5 * smoothstep(0.5, 0.85, manchas) + 0.35 * escorrido + 0.3 * topo;
	q = clamp(q * forca, 0.0, 0.7);
	ALBEDO = mix(vec3(1.0), cor_sujeira, q);
}
