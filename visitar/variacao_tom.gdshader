// Variação de tom em coordenadas do mundo, desenhada por cima das paredes, pisos e tetos (next_pass).
// Multiplica a cor final por um valor entre ~0,86 e 1,0: manchas grandes e suaves, que tiram a cara de "uma cor só"
// e escondem a repetição das texturas, sem mexer nos arquivos dos kits.
shader_type spatial;
render_mode unshaded, blend_mul, depth_draw_never, cull_back, shadows_disabled, fog_disabled;

varying vec3 wpos;

float hash(vec3 p) {
	p = fract(p * 0.3183099 + 0.1);
	p *= 17.0;
	return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
}

float vnoise(vec3 x) {
	vec3 i = floor(x);
	vec3 f = fract(x);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(mix(hash(i), hash(i + vec3(1, 0, 0)), f.x), mix(hash(i + vec3(0, 1, 0)), hash(i + vec3(1, 1, 0)), f.x), f.y),
		mix(mix(hash(i + vec3(0, 0, 1)), hash(i + vec3(1, 0, 1)), f.x), mix(hash(i + vec3(0, 1, 1)), hash(i + vec3(1, 1, 1)), f.x), f.y), f.z);
}

void vertex() {
	wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	float n = vnoise(wpos * 0.35) * 0.6 + vnoise(wpos * 1.3) * 0.3 + vnoise(wpos * 4.0) * 0.1;
	float k = mix(0.86, 1.0, smoothstep(0.2, 0.8, n));
	ALBEDO = vec3(k);
}
