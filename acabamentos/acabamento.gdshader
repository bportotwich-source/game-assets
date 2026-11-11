// Acabamento por cômodo (papel de parede, azulejo, lambri, piso) em cima das paredes lisas e pisos genéricos dos kits.
// Quem monta: acabamentos/acabamento.gd, a partir de kits/<kit>/acabamento.json e acabamentos/estilos.json.
// O mapa diz, para cada célula de 0,25 m de cada andar, o estilo de parede (R), de piso (G) e o pé-direito (B).
// Parede: lê a célula 0,2 m na frente da face. Piso: lê a célula embaixo. Fora dos cômodos fica o material original.
shader_type spatial;

uniform sampler2D orig_albedo : source_color, hint_default_white, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D orig_normal : hint_normal, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D orig_orm : hint_default_white, filter_linear_mipmap_anisotropic, repeat_enable;
uniform vec4 orig_cor : source_color = vec4(1.0);
uniform vec3 orig_uv_escala = vec3(1.0);
uniform bool orig_tem_normal = false;
uniform bool orig_tem_orm = false;
uniform float orig_rugosidade = 0.9;

uniform sampler2D mapa : filter_nearest;
uniform vec2 mapa_origem;
uniform float mapa_cel = 0.25;
uniform ivec2 mapa_tam;
uniform int n_niveis = 1;
uniform float niveis[48];
uniform bool eh_piso = false;
uniform bool ligado = true;
uniform bool molduras_modeladas = false;   // o kit traz rodapé e sanca em geometria (scripts/detalhe/molduras.py): não pinta os do shader

uniform sampler2DArray acab_albedo : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2DArray acab_normal : hint_normal, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2DArray acab_orm : hint_default_white, filter_linear_mipmap_anisotropic, repeat_enable;

// estilos de parede: x = camada de cima, y = camada de baixo, z = altura da troca, w = bits (1 rodapé, 2 sanca)
uniform vec4 parede_def[32];
uniform vec3 parede_cor_cima[32];
uniform vec3 parede_cor_baixo[32];
// estilos de piso: x = camada; cor em piso_cor
uniform int piso_camada[16];
uniform vec3 piso_cor[16];

varying vec3 wpos;
varying vec3 wnrm;

void vertex() {
	wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	wnrm = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

int andar_de(float y) {
	int a = 0;
	for (int i = 1; i < 48; i++) {
		if (i >= n_niveis) break;
		if (y >= niveis[i] - 0.05) a = i;
	}
	return a;
}

vec4 celula(vec2 xz, int a) {
	ivec2 c = ivec2(floor((xz - mapa_origem) / mapa_cel));
	if (c.x < 0 || c.y < 0 || c.x >= mapa_tam.x || c.y >= mapa_tam.y) return vec4(0.0);
	return texelFetch(mapa, ivec2(c.x, c.y + a * mapa_tam.y), 0);
}

void fragment() {
	bool parede = abs(wnrm.y) < 0.5;
	bool piso = eh_piso && wnrm.y > 0.5;
	int a = andar_de(wpos.y + (piso ? 0.05 : 0.0));
	vec4 c = vec4(0.0);
	if (parede) c = celula(wpos.xz + normalize(wnrm.xz) * 0.2, a);
	else if (piso) c = celula(wpos.xz, a);
	int estilo = parede ? int(c.r * 255.0 + 0.5) - 1 : int(c.g * 255.0 + 0.5) - 1;
	if (!ligado || c.a < 0.5 || estilo < 0 || (!parede && !piso)) {
		vec2 uvo = UV * orig_uv_escala.xy;
		ALBEDO = texture(orig_albedo, uvo).rgb * orig_cor.rgb;
		if (orig_tem_orm) {
			vec3 o = texture(orig_orm, uvo).rgb;
			AO = o.r;
			ROUGHNESS = o.g;
		} else {
			ROUGHNESS = orig_rugosidade;
		}
		if (orig_tem_normal) NORMAL_MAP = texture(orig_normal, uvo).rgb;
	} else {
		vec3 n_mundo;
		vec3 alb; vec3 orm; vec3 nm;
		if (parede) {
			vec3 t = normalize(vec3(-wnrm.z, 0.0, wnrm.x));
			float u = dot(wpos, t);
			float alt = wpos.y - niveis[a];
			float pe = c.b * 255.0 * 0.02;
			vec4 d = parede_def[estilo];
			bool baixo = alt < d.z;
			float camada = baixo ? d.y : d.x;
			vec3 cor = baixo ? parede_cor_baixo[estilo] : parede_cor_cima[estilo];
			// lambri e azulejo começam no piso; papel e tinta, no alto (a emenda some no teto)
			vec2 uv = vec2(u, baixo ? -alt : (pe - alt));
			alb = texture(acab_albedo, vec3(uv, camada)).rgb * cor;
			orm = texture(acab_orm, vec3(uv, camada)).rgb;
			nm = texture(acab_normal, vec3(uv, camada)).rgb * 2.0 - 1.0;
			int bits = molduras_modeladas ? 0 : int(d.w + 0.5);
			// arremate de madeira em cima do lambri/azulejo
			if (d.z > 0.05 && abs(alt - d.z) < 0.025) {
				float k = (alt - d.z) / 0.025;
				alb = d.y == 9.0 ? vec3(0.32, 0.2, 0.12) : vec3(0.93, 0.92, 0.88);
				orm = vec3(1.0, 0.45, 0.0);
				nm = vec3(0.0, k * 0.8, 1.0);
			}
			if ((bits & 1) != 0 && alt < 0.12) {          // rodapé pintado
				alb = vec3(0.95, 0.94, 0.9) * (alt > 0.105 ? 0.8 : 1.0);
				orm = vec3(alt > 0.105 ? 0.7 : 1.0, 0.45, 0.0);
				nm = vec3(0.0, alt > 0.105 ? 0.7 : 0.0, 1.0);
			}
			if ((bits & 2) != 0 && pe - alt < 0.10 && pe - alt > -0.02 && pe > 1.0) {   // sanca
				float k = (pe - alt) / 0.10;
				alb = vec3(0.96, 0.95, 0.92);
				orm = vec3(mix(0.75, 1.0, k), 0.6, 0.0);
				nm = vec3(0.0, -0.6 * (1.0 - k), 1.0);
			}
			// sombra perto do piso e do teto (oclusão assada, barata)
			orm.r *= mix(0.72, 1.0, smoothstep(0.0, 0.35, alt)) * mix(0.8, 1.0, smoothstep(0.0, 0.3, abs(pe - alt)));
			nm = normalize(nm);
			n_mundo = normalize(t * nm.x + vec3(0.0, 1.0, 0.0) * nm.y + wnrm * nm.z);
		} else {
			vec2 uv = vec2(wpos.x, wpos.z);
			float camada = float(piso_camada[estilo]);
			alb = texture(acab_albedo, vec3(uv, camada)).rgb * piso_cor[estilo];
			orm = texture(acab_orm, vec3(uv, camada)).rgb;
			nm = normalize(texture(acab_normal, vec3(uv, camada)).rgb * 2.0 - 1.0);
			n_mundo = normalize(vec3(1.0, 0.0, 0.0) * nm.x + vec3(0.0, 0.0, -1.0) * nm.y + wnrm * nm.z);
		}
		ALBEDO = alb;
		AO = orm.r;
		ROUGHNESS = orm.g;
		NORMAL = normalize((VIEW_MATRIX * vec4(n_mundo, 0.0)).xyz);
	}
}
