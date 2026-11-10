"""Monta a cena com os materiais procedurais ligados (sem bake) e salva um .blend para o foto.py."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
import modelo, lib, texturas
ps = modelo.construir()
tot = 0
for o in ps:
    t = lib.tris(o); tot += t
    print(f'{o.name:22s} {t:6d} tris grupo {o["grupo"]}')
print('TOTAL', tot)
falta = {m.name for m in bpy.data.materials} - set(texturas.CLASSES)
print('sem classe:', falta)
texturas.preparar_materiais(); texturas.previa()
bpy.ops.wm.save_as_mainfile(filepath=sys.argv[1] if len(sys.argv) > 1 else '/home/user/tmp/casa.blend')
