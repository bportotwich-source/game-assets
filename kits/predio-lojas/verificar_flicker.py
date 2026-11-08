import os,sys,math,collections,numpy as np
os.chdir(os.path.dirname(os.path.abspath(__file__)))
g={'__file__':os.path.abspath('gerar_kit.py'),'__name__':'verificar'}; exec(compile(open('gerar_kit.py',encoding='utf-8').read(),'gerar_kit.py','exec'),g)
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union
pieces,L=g['pieces'],g['L']
only=sys.argv[1:]  # optional piece filter
groups=collections.defaultdict(list); solids=[]
def add_mesh(m,srcid,label):
    b=m.bounds; vol_box=np.prod(b[1]-b[0])
    isbox=vol_box>0 and abs(abs(m.volume)-vol_box)/vol_box<0.01 and len(m.faces)==12
    solids.append((b,None if isbox else m))
    fn=m.face_normals; tri=m.triangles
    for i in range(len(fn)):
        n=fn[i]; ax=int(np.argmax(np.abs(n)))
        if abs(n[ax])<0.999: continue
        sg=1 if n[ax]>0 else -1; c=round(float(tri[i][:,ax].mean()),3); o=[k for k in range(3) if k!=ax]
        poly=Polygon(tri[i][:,o])
        if poly.area>1e-6: groups[(ax,sg,c)].append((srcid,label,poly))
sid=0
if os.environ.get('SOLO'):
    L=[{'piece':n,'pos':[i*100.0,0,0],'rotY':0} for i,n in enumerate(pieces)]
for e in L:
    if e['piece']=='player_scale_ref': continue
    T=trimesh.transformations.rotation_matrix(math.radians(e['rotY']),[0,1,0]); T[:3,3]=e['pos']
    for mat,ms in pieces[e['piece']].parts.items():
        for m in ms:
            mm=m.copy(); mm.apply_transform(T); add_mesh(mm,sid,(e['piece'],mat,tuple(e['pos']),e['rotY'])); sid+=1
B=np.array([s[0] for s in solids])
def inside(p):
    hit=np.where(np.all(B[:,0]<p+1e-4,axis=1)&np.all(B[:,1]>p-1e-4,axis=1))[0]
    for h in hit:
        m=solids[h][1]
        if m is None: return True
        try:
            if m.contains([p])[0]: return True
        except Exception: return True
    return False
issues=collections.Counter(); examples={}
oc={}
def opp(key):
    k=(key[0],-key[1],key[2])
    if k not in oc: oc[k]=unary_union([p for _,_,p in groups[k]]) if k in groups else None
    return oc[k]
for key,items in groups.items():
    if len(set(s for s,_,_ in items))<2: continue
    by=collections.defaultdict(list); lab={}
    for s,l,p in items: by[s].append(p); lab[s]=l
    ids=list(by); U={s:unary_union(by[s]) for s in ids}
    ax,sg,c=key; o=[k for k in range(3) if k!=ax]
    if ax==1 and sg<0 and c<=0.001: continue   # undersides at ground level
    for a in range(len(ids)):
        for b in range(a+1,len(ids)):
            A,Bb=U[ids[a]],U[ids[b]]
            if A.bounds[2]<Bb.bounds[0] or Bb.bounds[2]<A.bounds[0] or A.bounds[3]<Bb.bounds[1] or Bb.bounds[3]<A.bounds[1]: continue
            la,lb=lab[ids[a]],lab[ids[b]]
            if la[1]==lb[1] and (la[1] not in tuple(g['TEX']) or (la[1] in ('plaster','siding','planks','render','saltillo','roofdeck') and ax==1) or (la[0]==lb[0] and la[2]==lb[2])): continue  # same colour (brick UVs align within a piece)
            I=A.intersection(Bb)
            if I.area<=2e-4: continue
            O=opp(key)
            if O is not None: I=I.difference(O)
            comps=getattr(I,'geoms',[I]); vis=0; pt=None
            for comp in comps:
                if comp.area<1e-5 or comp.geom_type!='Polygon': continue
                q=comp.representative_point(); p=np.zeros(3); p[o[0]],p[o[1]]=q.x,q.y; p[ax]=c+sg*0.003
                if not inside(p): vis+=comp.area; pt=tuple(round(float(v),3) for v in p)
            if vis>2e-4:
                k=tuple(sorted([(la[0],la[1]),(lb[0],lb[1])]))
                issues[k]+=vis; examples.setdefault(k,(key,la[2],lb[2],pt))
for k,v in sorted(issues.items(),key=lambda x:-x[1]):
    print(f'{v:7.3f}  {k[0][0]}:{k[0][1]} <-> {k[1][0]}:{k[1][1]}  eg {examples[k]}')
print('TOTAL',len(issues))
