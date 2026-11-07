import sys, os, json
sys.path.insert(0,'/home/user/game-assets/scripts/texturas')
import gerar_texturas as G
from PIL import Image
OUT=sys.argv[1]; PX=int(sys.argv[2])
C=dict(G.CORES)
variants={  # chave da demo: (material do gerador, cores extra)
 'brick':('brick',{}),'stone':('stone',{}),'plaster':('plaster',{}),'stone2':('stone2',{}),
 'render_padaria':('render',{'render':(206,112,78)}),'roof_padaria':('roof_tiles',{'roof_tiles':(128,72,50)}),
 'render_enx':('render',{'render':(236,222,196)}),'roof_enx':('roof_tiles',{'roof_tiles':(172,74,50)}),
 'siding':('siding',{}),'shingles':('shingles',{}),
}
info={}
for key,(mat,extra) in variants.items():
    cores=dict(C); cores.update(extra); fn,tile,orig=G.materials(cores)[mat]
    info[key]=[orig[0]/tile[0],orig[1]/tile[1]]
    for s in G.STYLES:
        alb,hm,rough,nstr,aod=fn(s,PX)
        d=os.path.join(OUT,s); G.save_set(d,key,alb,hm,rough,PX,nstr,aod)
        for m in ('albedo','normal','orm'):
            p=os.path.join(d,f'{key}_{m}.png'); Image.open(p).convert('RGB').save(p[:-4]+'.jpg',quality=88 if m!='normal' else 92); os.remove(p)
json.dump(info,open(os.path.join(OUT,'uv.json'),'w'))
print(info)
