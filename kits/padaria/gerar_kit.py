import numpy as np, trimesh, json, os, math
from trimesh.visual.material import PBRMaterial
from trimesh.visual import TextureVisuals
OUT = os.path.join(os.path.dirname(__file__), 'out')
os.makedirs(OUT+'/pieces', exist_ok=True)

COL = {
 'brick':(176,78,56),'trim':(226,212,184),'stone':(204,195,178),'glass':(160,196,214),
 'frame':(236,228,208),'iron':(46,40,38),'roof':(140,137,132),'door':(74,108,140),
 'wood':(184,110,62),'tower_roof':(76,82,96),'metal':(230,230,226),'leaf':(150,196,92),
 'trunk':(214,204,186),'pave':(224,214,194),'mat':(196,140,96),'grass':(110,170,90),
 'dark':(70,70,72),'light':(255,226,150),'plaster':(240,232,216),'floor':(196,150,104),'player':(90,140,220),'sofa':(96,124,156),'bedding':(246,242,232),'blanket':(204,124,92),'wood_light':(206,172,126),'ceramic':(250,250,247),'counter':(88,88,94),'rug':(176,96,84),'tile':(214,224,228),'plant':(108,160,90),'pot':(190,110,80),'screen':(40,44,52),
}
from PIL import Image, ImageDraw
import random
def brick_texture(px=512,rows=8,per=4,seed=7):
    # 1 m x 1 m tile: 8 courses of 0.125 m, bricks 0.25 m, running bond. Stylised toon palette.
    rnd=random.Random(seed); im=Image.new('RGB',(px,px),(214,196,170)); d=ImageDraw.Draw(im)
    rh=px/rows; bw=px/per; m=max(2,int(px*0.012))
    base=[(178,80,58),(168,72,52),(186,88,64),(160,68,50),(192,96,70)]
    for r in range(rows):
        off=(bw/2) if r%2 else 0
        for i in range(-1,per+1):
            x0=i*bw+off; y0=r*rh; c=rnd.choice(base)
            box=[x0+m/2,y0+m/2,x0+bw-m/2,y0+rh-m/2]
            for dx in (-px,0,px):
                d.rectangle([box[0]+dx,box[1],box[2]+dx,box[3]],fill=c)
                d.rectangle([box[0]+dx,box[1],box[2]+dx,box[1]+max(1,m*0.8)],fill=tuple(min(255,v+14) for v in c))
    return im.transpose(Image.FLIP_TOP_BOTTOM)
BRICK_TEX=brick_texture()
def _noise(px,cells,seed):
    # seamless value noise: random grid tiled 3x3, smooth-upscaled, centre crop
    r=np.random.RandomState(seed).rand(cells,cells); t=np.tile(r,(3,3))
    im=Image.fromarray((t*255).astype(np.uint8)).resize((px*3,px*3),Image.BICUBIC)
    return np.asarray(im,dtype=np.float32)[px:2*px,px:2*px]/255.0-0.5
def stone_texture(px=256,seed=3):
    # tile = 1.0 m wide x 0.8 m tall: two 0.4 m courses of 1.0 m ashlar blocks, running bond
    rnd=random.Random(seed); h=int(px*0.8); im=Image.new('RGB',(px,h),(168,158,142)); d=ImageDraw.Draw(im)
    base=[(206,197,180),(198,189,172),(212,204,188),(202,192,174)]; m=max(3,int(px*0.014))
    for r in range(2):
        off=px/2 if r%2 else 0; y0=r*h/2
        for i in range(-1,2):
            c=rnd.choice(base); x0=i*px+off
            for dx in (-px,0,px):
                d.rectangle([x0+dx+m/2,y0+m/2,x0+dx+px-m/2,y0+h/2-m/2],fill=c)
                d.rectangle([x0+dx+m/2,y0+m/2,x0+dx+px-m/2,y0+m/2+m*0.7],fill=tuple(min(255,v+12) for v in c))
    a=np.asarray(im,dtype=np.float32); n=_noise(px,12,seed)[:h,:]+0.5*_noise(px,40,seed+1)[:h,:]
    a=np.clip(a+n[...,None]*22,0,255).astype(np.uint8)
    return Image.fromarray(a).transpose(Image.FLIP_TOP_BOTTOM)
def plaster_texture(px=256,seed=5):
    # tile = 1 m: smooth stucco, soft blotches + fine grain, seamless
    n=_noise(px,5,seed)*0.5+_noise(px,32,seed+1)*0.5+_noise(px,128,seed+2)*0.9
    base=np.array([238,230,214],np.float32); a=base[None,None,:]+n[...,None]*16
    return Image.fromarray(np.clip(a,0,255).astype(np.uint8))
STONE_TEX=stone_texture()
PLASTER_TEX=plaster_texture(); PLASTER_TEX.save(os.path.join(OUT,'plaster_texture.png'))
TEX={'brick':(BRICK_TEX,1.0,1.0),'stone':(STONE_TEX,1.0,0.8),'plaster':(PLASTER_TEX,1.0,1.0)}  # material: (image, tile width m, tile height m)
MATS = {k:PBRMaterial(name=k, baseColorFactor=[c/255 for c in v]+[1.0], metallicFactor=0.0, roughnessFactor=0.9) for k,v in COL.items()}
for k,(im,_,_) in TEX.items(): MATS[k]=PBRMaterial(name=k,baseColorTexture=im,baseColorFactor=[1,1,1,1],metallicFactor=0.0,roughnessFactor=0.9)

class Piece:
    def __init__(s): s.parts={}
    def add(s,mat,m): s.parts.setdefault(mat,[]).append(m); return s
    def box(s,mat,x0,x1,y0,y1,z0,z1):
        b=trimesh.creation.box(extents=[x1-x0,y1-y0,z1-z0]); b.apply_translation([(x0+x1)/2,(y0+y1)/2,(z0+z1)/2]); return s.add(mat,b)
    def cyl(s,mat,r,y0,y1,x=0,z=0,sec=16):
        c=trimesh.creation.cylinder(radius=r,height=y1-y0,sections=sec); c.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0])); c.apply_translation([x,(y0+y1)/2,z]); return s.add(mat,c)
    def cone(s,mat,r,y0,y1,x=0,z=0,sec=16):
        c=trimesh.creation.cone(radius=r,height=y1-y0,sections=sec); c.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0])); c.apply_translation([x,y0,z]); return s.add(mat,c)
    def sphere(s,mat,r,x,y,z):
        c=trimesh.creation.icosphere(subdivisions=1,radius=r); c.apply_translation([x,y,z]); return s.add(mat,c)
    def seg(s,mat,p0,p1,w):
        p0,p1=np.array(p0,float),np.array(p1,float); d=p1-p0; L=np.linalg.norm(d)
        b=trimesh.creation.box(extents=[w,w,L]); z=np.array([0,0,1.0]); v=d/L
        ax=np.cross(z,v); ang=math.acos(np.clip(np.dot(z,v),-1,1))
        if np.linalg.norm(ax)>1e-6: b.apply_transform(trimesh.transformations.rotation_matrix(ang,ax))
        b.apply_translation((p0+p1)/2); return s.add(mat,b)
    def merge(s,other,T=np.eye(4)):
        for k,ms in other.parts.items():
            for m in ms: mm=m.copy(); mm.apply_transform(T); s.add(k,mm)
        return s
    def scene(s,name):
        sc=trimesh.Scene()
        for k,ms in s.parts.items():
            m=trimesh.util.concatenate(ms); m.unmerge_vertices()
            if k in TEX:
                v=m.vertices; n=m.vertex_normals; uv=np.zeros((len(v),2))
                ax=np.argmax(np.abs(n),axis=1)
                uv[ax==0]=v[ax==0][:,[2,1]]; uv[ax==2]=v[ax==2][:,[0,1]]; uv[ax==1]=v[ax==1][:,[0,2]]
                tw,th=TEX[k][1],TEX[k][2]; uv[:,0]/=tw; uv[ax!=1,1]/=th; uv[ax==1,1]/=tw
                if k=='sign': uv=np.stack([(v[:,0]-SIGN[0])/SIGN[2],(v[:,1]-SIGN[1])/SIGN[3]],1)
                if k=='plaster': uv[ax==1]=0.37   # plain colour on horizontal plaster (wall tops, ceilings): overlapping tops at wall junctions stay identical
                m.visual=TextureVisuals(uv=uv,material=MATS[k])
            else: m.visual=TextureVisuals(material=MATS[k])
            sc.add_geometry(m,node_name=f'{name}_{k}',geom_name=f'{name}_{k}')
        return sc

W=2.0; T=0.3; H=3.0; HG=3.2   # module width, wall thickness, floor heights

from shapely.geometry import Polygon, box as sbox
def grid_solid(xs,ys,zs,cell):
    """Watertight mesh on a rectilinear grid. cell(i,j,k) -> material or None.
    Every face is split on the same grid lines, so neighbouring faces share vertices:
    no T-junctions, no slivers, no pixel cracks."""
    out={}
    nx,ny,nz=len(xs)-1,len(ys)-1,len(zs)-1
    def get(i,j,k):
        if 0<=i<nx and 0<=j<ny and 0<=k<nz: return cell(i,j,k)
        return None
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                m=get(i,j,k)
                if m is None: continue
                x0,x1,y0,y1,z0,z1=xs[i],xs[i+1],ys[j],ys[j+1],zs[k],zs[k+1]
                quads=[]
                if get(i-1,j,k) is None: quads.append([(x0,y0,z0),(x0,y0,z1),(x0,y1,z1),(x0,y1,z0)])
                if get(i+1,j,k) is None: quads.append([(x1,y0,z0),(x1,y1,z0),(x1,y1,z1),(x1,y0,z1)])
                if get(i,j-1,k) is None: quads.append([(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1)])
                if get(i,j+1,k) is None: quads.append([(x0,y1,z0),(x0,y1,z1),(x1,y1,z1),(x1,y1,z0)])
                if get(i,j,k-1) is None: quads.append([(x0,y0,z0),(x0,y1,z0),(x1,y1,z0),(x1,y0,z0)])
                if get(i,j,k+1) is None: quads.append([(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)])
                for q in quads: out.setdefault(m,[]).append(q)
    meshes={}
    for m,qs in out.items():
        v=[];f=[]
        for q in qs:
            b=len(v); v+=q; f+=[[b,b+1,b+2],[b,b+2,b+3]]
        mm=trimesh.Trimesh(vertices=np.array(v,float),faces=np.array(f),process=False); mm.merge_vertices(); meshes[m]=mm
    return meshes
def wall_with_opening(p,mat,ow,oy0,oy1,h,inner='plaster',t=T,centered=False):
    x=ow/2; z0=-t/2 if centered else -t
    zs=[z0,z0+0.02,z0+t]
    if ow>0:
        xs=[-W/2,-x,x,W/2]; ys=sorted(set([0.0,max(oy0,0.0),oy1,h]))
        def cell(i,j,k):
            if i==1 and ys[j]>=max(oy0,0.0)-1e-9 and ys[j+1]<=oy1+1e-9: return None
            return inner if k==0 else mat
    else:
        xs=[-W/2,W/2]; ys=[0.0,h]
        def cell(i,j,k): return inner if k==0 else mat
    for m,mesh in grid_solid(xs,ys,zs,cell).items(): p.add(m,mesh)

def window(p,ow,oy0,oy1,lintel='trim',mull=True,sill_top=None,glass=True):
    x=ow/2; f=0.07
    if glass: p.box('glass',-x,x,oy0,oy1,-0.16,-0.14)
    p.box('frame',-x,-x+f,oy0,oy1,-0.18,-0.06); p.box('frame',x-f,x,oy0,oy1,-0.18,-0.06)
    p.box('frame',-x,x,oy1-f,oy1,-0.18,-0.06); p.box('frame',-x,x,oy0,oy0+f,-0.18,-0.06)
    if mull:
        p.box('frame',-0.025,0.025,oy0,oy1,-0.17,-0.1)
        m=oy0+(oy1-oy0)*0.55; p.box('frame',-x,x,m-0.025,m+0.025,-0.17,-0.1)
    st=oy0+0.015 if sill_top is None else sill_top   # never level with the opening floor
    p.box('trim',-x-0.08,x+0.08,st-0.08,st,-0.05,0.08)      # sill
    if lintel: p.box(lintel,-x-0.06,x+0.06,oy1+0.01,oy1+0.15,-0.02,0.04)

def ledge(p,h,mat='trim',th=0.1,d=0.06):
    p.box(mat,-W/2,W/2,h-th+0.015,h+0.015,0.0,d)   # rises 1.5 cm above the module top: hides the slab edge, never level with the wall top

P={}
def wall_brick_window():
    p=Piece(); wall_with_opening(p,'brick',0.9,0.85,2.3,H); window(p,0.9,0.85,2.3); ledge(p,H,th=0.08,d=0.04); return p
def wall_brick_plain():
    p=Piece(); wall_with_opening(p,'brick',0,0,0,H); ledge(p,H,th=0.08,d=0.04); return p
def wall_brick_balcony_door():
    p=Piece(); wall_with_opening(p,'brick',0.9,0.05,2.35,H); window(p,0.9,0.05,2.35,sill_top=0.015,glass=False,mull=False); ledge(p,H,th=0.08,d=0.04); return p
def wall_ground_window():
    p=Piece(); wall_with_opening(p,'stone',0.9,0.9,2.3,HG); window(p,0.9,0.9,2.3,lintel='stone')
    p.box('dark',-W/2,W/2,0,0.12,0.0,0.03); ledge(p,HG,th=0.2,d=0.08); return p
def wall_ground_door():
    p=Piece(); ow=1.1; wall_with_opening(p,'stone',ow,0,2.4,HG)
    x=ow/2
    p.box('frame',-x,-x+0.07,0,2.4,-0.22,0.02); p.box('frame',x-0.07,x,0,2.4,-0.22,0.02); p.box('frame',-x,x,2.33,2.4,-0.22,0.02)
    p.box('stone',-0.75,0.75,0,0.15,0,0.45)  # step
    p.box('dark',-W/2,-x,0,0.12,0.0,0.03); p.box('dark',x,W/2,0,0.12,0.0,0.03)
    ledge(p,HG,th=0.2,d=0.08); return p
def corner(mat,h,ledge_th,ledge_d,plinth=False):
    p=Piece(); e=0.03; p.box(mat,-T-0.01,e,0,h,-T-0.01,e)
    p.box('trim',-T,e+ledge_d,h-ledge_th+0.015,h+0.015,-T,e+ledge_d)
    if plinth: p.box('dark',-T,e+0.03,0,0.12,-T,e+0.03)
    return p
def cornice(corner_=False,gap=0.0):
    p=Piece(); x0,x1=(-T,0.03) if corner_ else (-W/2,W/2)
    def bx(mat,y0,y1,d,back=-T):
        if corner_: p.box(mat,-T,0.03+d,y0,y1,-T,0.03+d)
        elif gap: p.box(mat,-W/2,-gap/2,y0,y1,back,d); p.box(mat,gap/2,W/2,y0,y1,back,d)
        else: p.box(mat,-W/2,W/2,y0,y1,back,d)
    bx('brick',0,0.6,0.03); bx('trim',0.6,0.72,0.12); bx('trim',0.72,0.82,0.2)
    bx('brick',0.82,1.3,0.0); bx('trim',1.3,1.4,0.06)
    if not corner_:
        for i in range(6):
            cx=-W/2+W/12+i*W/6
            if abs(cx)>gap/2+0.07: p.box('trim',cx-0.07,cx+0.07,0.2,0.42,0,0.12)
        if gap: p.box('trim',-W/2,-gap/2,1.3,1.4,-T-0.06,-T); p.box('trim',gap/2,W/2,1.3,1.4,-T-0.06,-T)
        else: p.box('trim',-W/2,W/2,1.3,1.4,-T-0.06,-T)  # inner cap lip
        if gap: p.box('roof',-gap/2,gap/2,-0.04,0.02,-T,0.04)  # threshold (2 cm sill hides the wall top + roof edge)
    return p
def roof_tile():
    p=Piece(); p.box('roof',-W/2,W/2,-0.04,0.0,-W/2,W/2); p.box('plaster',-W/2+0.02,W/2-0.02,-0.2,-0.04,-W/2+0.02,W/2-0.02); return p
def roof_stair_hut():
    p=Piece(); s=1.0; h=2.6
    p.box('brick',-s,s,0,h,-s,s); p.box('roof',-s-0.12,s+0.12,h,h+0.14,-s-0.12,s+0.12)
    p.box('trim',-s-0.04,s+0.04,h-0.12,h,-s-0.04,s+0.04)
    p.box('dark',-0.45,0.45,0,2.1,s,s+0.03); p.box('frame',-0.5,0.5,2.1,2.18,s,s+0.05)
    p.box('frame',-0.5,-0.45,0,2.1,s,s+0.05); p.box('frame',0.45,0.5,0,2.1,s,s+0.05)
    p.box('metal',0.28,0.36,1.0,1.08,s+0.03,s+0.07); return p
def water_tower():
    p=Piece(); r=0.8; leg=1.6
    for sx in (-1,1):
        for sz in (-1,1): p.cyl('iron',0.05,0,leg,sx*0.55,sz*0.55,8)
    p.seg('iron',(-0.55,0.5,0.55),(0.55,1.2,0.55),0.04); p.seg('iron',(-0.55,0.5,-0.55),(0.55,1.2,-0.55),0.04)
    p.box('iron',-0.95,0.95,leg,leg+0.1,-0.95,0.95)
    p.cyl('wood',r,leg+0.1,leg+1.9,sec=20)
    for y in (leg+0.5,leg+1.1,leg+1.7): p.cyl('iron',r+0.02,y,y+0.05,sec=20)
    p.cone('tower_roof',r+0.12,leg+1.9,leg+2.7,sec=20); p.sphere('tower_roof',0.06,0,leg+2.72,0); return p
def ac_unit():
    p=Piece(); p.box('metal',-0.45,0.45,0,0.6,-0.3,0.3); p.cyl('dark',0.2,0.3,0.31,0,0,20)
    p.add('dark',p.parts['dark'].pop().apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[1,0,0],[0,0.3,0])).apply_translation([0.08,0,0.3]))
    p.box('dark',-0.42,-0.38,0,0.05,-0.27,0.27); p.box('dark',0.38,0.42,0,0.05,-0.27,0.27); return p
def railing(p,x0,x1,z0,z1,y,h=0.9,sides=(True,True,True),n=None):
    def run(a,b):
        L=np.linalg.norm(np.subtract(b,a)); k=n or max(2,int(L/0.12))
        for i in range(k+1):
            t=i/k; q=np.add(a,np.multiply(t,np.subtract(b,a))); p.box('iron',q[0]-0.015,q[0]+0.015,y,y+h,q[1]-0.015,q[1]+0.015)
        p.seg('iron',(a[0],y+h,a[1]),(b[0],y+h,b[1]),0.05); p.seg('iron',(a[0],y+0.1,a[1]),(b[0],y+0.1,b[1]),0.035)
    if sides[0]: run((x0,z1),(x1,z1))
    if sides[1]: run((x0,z0),(x0,z1))
    if sides[2]: run((x1,z0),(x1,z1))
def balcony():
    p=Piece(); x=0.75; d=0.8
    p.box('dark',-x,x,-0.08,0.0,0,d); p.box('iron',-x,x,-0.16,-0.08,d-0.05,d)
    railing(p,-x+0.02,x-0.02,0.02,d-0.02,0); return p
def fire_escape_platform():
    p=Piece(); x=1.0; d=0.9
    for i in range(10): p.box('iron',-x+i*0.2+0.02,-x+i*0.2+0.16,-0.05,0,0,d)
    p.box('iron',-x,x,-0.12,0,d-0.04,d); p.box('iron',-x,x,-0.12,0,0,0.04)
    railing(p,-x+0.02,x-0.02,0.02,d-0.02,0)
    p.seg('iron',(-x+0.1,-0.1,0.02),(-x+0.1,-0.7,0.02),0.06); p.seg('iron',(-x+0.1,-0.7,0.02),(-x+0.1,-0.1,d-0.1),0.05)
    p.seg('iron',(x-0.1,-0.1,0.02),(x-0.1,-0.7,0.02),0.06); p.seg('iron',(x-0.1,-0.7,0.02),(x-0.1,-0.1,d-0.1),0.05)
    return p
def fire_escape_stairs():
    p=Piece(); run=1.7; rise=H; w=0.6; z0=0.15; z1=z0+w
    for z in (z0,z1): p.seg('iron',(-run/2,0,z),(run/2,rise,z),0.06)
    n=14
    for i in range(1,n):
        t=i/n; xx=-run/2+t*run; yy=t*rise; p.box('iron',xx-0.06,xx+0.06,yy-0.02,yy+0.01,z0,z1)
    p.seg('iron',(-run/2,0.9,z1),(run/2,rise+0.9,z1),0.04)
    return p
FE_D=2.0; FE_W=1.0   # platform depth (1 m walkway + 1 m stair strip)
def fe_rail_run(p,a,b,y=0,h=1.0,step=0.12):
    L=np.linalg.norm(np.subtract(b,a)); k=max(2,int(L/step))
    for i in range(k+1):
        t=i/k; q=np.add(a,np.multiply(t,np.subtract(b,a))); p.box('iron',q[0]-0.015,q[0]+0.015,y,y+h,q[1]-0.015,q[1]+0.015)
    p.seg('iron',(a[0],y+h,a[1]),(b[0],y+h,b[1]),0.05); p.seg('iron',(a[0],y+0.1,a[1]),(b[0],y+0.1,b[1]),0.035)
def fe_deck(p,z0,z1):
    p.box('iron',-W/2,W/2,-0.06,-0.02,z0,z1)
    n=int((z1-z0)/0.1)
    for i in range(n): zz=z0+0.03+i*0.1; p.box('iron',-W/2,W/2,-0.02,0,zz,zz+0.05)
    p.box('iron',-W/2,W/2,-0.16,-0.06,z1-0.05,z1); p.box('iron',-W/2,W/2,-0.16,-0.06,z0,z0+0.05)
def fe_brackets(p,d=FE_D):
    for xx in (-W/2+0.08,W/2-0.08):
        p.box('iron',xx-0.03,xx+0.03,-0.16,-0.06,0,d); p.seg('iron',(xx,-0.7,0.02),(xx,-0.14,d*0.8),0.05)
def fire_escape_platform():
    p=Piece(); fe_deck(p,0,FE_D); fe_brackets(p); fe_rail_run(p,(-W/2,FE_D-0.02),(W/2,FE_D-0.02)); return p
def fire_escape_platform_stairwell():
    p=Piece(); fe_deck(p,0,FE_W); fe_brackets(p,FE_W); p.box('iron',-W/2,W/2,-0.16,-0.02,FE_D-0.05,FE_D); return p
def fire_escape_end_rail():
    p=Piece(); fe_rail_run(p,(0,0.05),(0,FE_D-0.02)); return p
def fire_escape_stairs(rise=H,run=4.0,w=0.9):
    p=Piece(); n=round(rise/0.18); tr=run/n; st=rise/n; z0=FE_W+0.05; z1=z0+w
    for i in range(n):
        x0=i*tr; top=(i+1)*st; p.box('iron',x0,x0+tr,top-0.04,top,z0,z1)
        for k in range(1,3): p.box('dark',x0+0.02,x0+tr-0.02,top-0.005,top+0.003,z0+k*w/3-0.01,z0+k*w/3+0.01)
    for z in (z0,z1): p.seg('iron',(0,0,z),(run,rise,z),0.07)
    p.seg('iron',(0,1.0,z1),(run,rise+1.0,z1),0.05)
    for i in range(0,n+1,3): xx=i*tr; yy=i*st; p.box('iron',xx-0.02,xx+0.02,yy,yy+1.0,z1-0.02,z1+0.02)
    return p
def entrance_canopy():
    p=Piece(); x=0.9; d=1.0
    p.box('dark',-x,x,0,0.14,0,d); p.box('iron',-x-0.02,x+0.02,0.14,0.18,-0.02,d+0.02)
    p.seg('iron',(-x+0.1,0.07,d-0.05),(-x+0.1,0.9,0.02),0.03); p.seg('iron',(x-0.1,0.07,d-0.05),(x-0.1,0.9,0.02),0.03); return p
def wall_lamp():
    p=Piece(); p.box('iron',-0.04,0.04,0,0.06,0,0.25); p.box('iron',-0.1,0.1,-0.35,-0.3,0.15,0.35)
    p.box('light',-0.08,0.08,-0.3,-0.05,0.17,0.33); p.box('iron',-0.11,0.11,-0.05,0.0,0.14,0.36); return p
def street_lamp():
    p=Piece(); p.cyl('iron',0.05,0,2.6,sec=8); p.box('iron',-0.14,0.14,2.6,2.65,-0.14,0.14)
    p.box('light',-0.11,0.11,2.65,2.95,-0.11,0.11); p.cone('iron',0.18,2.95,3.15,sec=4); return p
def tree():
    p=Piece(); p.cyl('trunk',0.07,0,1.2,sec=8)
    for (x,y,z,r) in [(0,1.6,0,0.5),(0.28,1.25,0.15,0.38),(-0.22,1.3,-0.1,0.36),(0.05,2.0,0.05,0.35)]: p.sphere('leaf',r,x,y,z)
    p.box('dark',-0.3,0.3,0,0.06,-0.3,0.3); return p
def sidewalk_tile():
    p=Piece(); p.box('pave',-W/2,W/2,-0.12,0,-W/2,W/2); return p
def sidewalk_curb():
    p=Piece(); p.box('stone',-W/2,W/2,-0.15,0.0,-0.15,0.0); return p
def grass_strip():
    p=Piece(); p.box('grass',-W/2,W/2,0,0.04,-0.2,0.0); return p
def doormat():
    p=Piece(); p.box('mat',-0.4,0.4,0,0.02,-0.25,0.25); return p

SLAB=0.2
def floor_tile():
    p=Piece(); p.box('floor',-W/2,W/2,-0.03,0,-W/2,W/2); p.box('plaster',-W/2+0.02,W/2-0.02,-SLAB,-0.03,-W/2+0.02,W/2-0.02); return p
def floor_tile_bath():
    p=Piece(); p.box('tile',-W/2,W/2,-0.03,0,-W/2,W/2); p.box('plaster',-W/2+0.02,W/2-0.02,-SLAB,-0.03,-W/2+0.02,W/2-0.02); return p
CORE=4.0; HOLE=1.35
def stair_core_slab(top='floor'):
    """4x4 m slab with the stair hole (x in [-1.35,1.35], full depth). Pivot: centre."""
    p=Piece(); h=CORE/2
    for (a,b) in ((-h,-HOLE),(HOLE,h)):
        p.box(top,a,b,-0.03 if top!='roof' else -0.04,0,-h,h); p.box('plaster',a+0.02,b-0.02,-SLAB,-0.03 if top!='roof' else -0.04,-h+0.02,h-0.02)
    return p
def stairs_u(rise,run=2.0,w=1.2,gap=0.1,land=1.7):
    """U-shaped stair: flight A goes up toward -Z on the left, landing at the back, flight B returns on the right.
    Pivot: centre of the core's open (front) edge, at the lower floor level."""
    p=Piece(); n=math.ceil(rise/0.18-1e-9); n+=n%2; k=n//2; st=rise/n; tr=run/k
    xa0,xa1=-gap/2-w,-gap/2; xb0,xb1=gap/2,gap/2+w
    for i in range(k-1):
        top=(i+1)*st; p.box('floor',xa0,xa1,top-0.04,top,-(i+1)*tr,-i*tr); p.box('plaster',xa0,xa1,top-0.26,top-0.04,-(i+1)*tr,-i*tr)
    mid=k*st
    p.box('floor',xa0,xb1,mid-0.04,mid,-run-land,-run+tr); p.box('plaster',xa0,xb1,mid-0.24,mid-0.04,-run-land,-run+tr)
    for j in range(1,k):
        top=mid+j*st
        p.box('floor',xb0,xb1,top-0.04,top,-run+(j)*tr,-run+(j+1)*tr); p.box('plaster',xb0,xb1,top-0.26,top-0.04,-run+(j)*tr,-run+(j+1)*tr)
    # handrails (inner pair + outer pair)
    for x in (xa0+0.04,xa1-0.04):
        p.seg('iron',(x,0.9,0),(x,mid+0.9,-run),0.05)
    for x in (xb0+0.04,xb1-0.04):
        p.seg('iron',(x,mid+0.9,-run+tr),(x,rise+0.9,0),0.05)
    for i in range(0,k+1,2):
        z=-i*tr; ya=i*st; yb=rise-i*st
        p.box('iron',xa1-0.06,xa1-0.02,ya,ya+0.9,z-0.02,z+0.02); p.box('iron',xb0+0.02,xb0+0.06,yb,yb+0.9,z-0.02,z+0.02)
    return p
def door_leaf_balcony(w=0.76,h=2.16):
    """Glazed leaf for the balcony / fire-escape door. Pivot: hinge, bottom. Closed = along +X."""
    p=Piece(); f=0.06
    p.box('frame',0,f,0,h,-0.02,0.02); p.box('frame',w-f,w,0,h,-0.02,0.02)
    p.box('frame',f,w-f,0,0.25,-0.02,0.02); p.box('frame',f,w-f,h-f,h,-0.02,0.02); p.box('frame',f,w-f,1.2,1.25,-0.02,0.02)
    p.box('glass',f,w-f,0.25,h-f,-0.008,0.008); p.box('metal',w-0.12,w-0.08,1.0,1.06,-0.05,0.05); return p
def door_leaf(w=0.96,h=2.32,glass=True,mat='door'):
    p=Piece(); p.box(mat,0,w,0,h,-0.025,0.025)
    if glass: p.box('glass',w*0.2,w*0.8,h*0.62,h*0.9,-0.03,0.03)
    p.box('metal',w-0.14,w-0.06,1.0,1.06,-0.06,0.06); return p
def interior_wall(doorway,h=H-SLAB,ow=0.9):
    p=Piece(); t=0.12; ow=ow if doorway else 0
    wall_with_opening(p,'plaster',ow,0,2.1,h,inner='plaster',t=t,centered=True)
    if doorway:
        for xx in (-ow/2,ow/2): p.box('frame',xx-0.04,xx+0.04,0,2.14,-t/2-0.02,t/2+0.02)
        p.box('frame',-ow/2-0.04,ow/2+0.04,2.08,2.18,-t/2-0.02,t/2+0.02)
    segs=[(-W/2,-ow/2-0.04),(ow/2+0.04,W/2)] if doorway else [(-W/2,W/2)]  # rodapé para na porta
    for a,b in segs: p.box('trim',a,b,0,0.1,t/2,t/2+0.015); p.box('trim',a,b,0,0.1,-t/2-0.015,-t/2)
    return p
def interior_wall_end(h=H-SLAB):
    # plain interior wall that stops at the inner face of an exterior wall (+X end shortened by T)
    p=Piece(); t=0.12; L=W-T
    m=trimesh.creation.box(extents=[L,h,t]); m.apply_translation([-W/2+L/2,h/2,0]); p.add('plaster',m)
    p.box('trim',-W/2,-W/2+L,0,0.1,t/2,t/2+0.015); p.box('trim',-W/2,-W/2+L,0,0.1,-t/2-0.015,-t/2); return p
def player_ref():
    p=Piece(); c=trimesh.creation.capsule(height=1.8-0.6,radius=0.3,count=[8,8]); c.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0])); c.apply_translation([0,0.9,0]); p.add('player',c)
    p.box('dark',-0.15,0.15,1.5,1.6,0.22,0.32); return p
def roof_stair_hut(wx=4.0,dz=5.4,h=2.8):
    """Walk-in hut over the stair core. Pivot: centre of footprint on the roof. Door on +Z."""
    p=Piece(); x=wx/2; z=dz/2; t=0.2
    p.box('brick',-x,x,0,h,-z,-z+t); p.box('brick',-x,-x+t,0,h,-z,z); p.box('brick',x-t,x,0,h,-z,z)
    p.box('brick',-x,-0.6,0,h,z-t,z); p.box('brick',0.6,x,0,h,z-t,z); p.box('brick',-0.6,0.6,2.3,h,z-t,z)
    for (a,b,c,d) in ((-x+t,x-t,-z+t,-z+t+0.02),):
        p.box('plaster',a,b,0,h,c,d)
    p.box('plaster',-x+t,-x+t+0.02,0,h,-z+t,z-t); p.box('plaster',x-t-0.02,x-t,0,h,-z+t,z-t)
    p.box('roof',-x-0.12,x+0.12,h,h+0.14,-z-0.12,z+0.12); p.box('trim',-x-0.04,x+0.04,h-0.12,h,-z-0.04,z+0.04)
    for xx in (-0.6,0.6): p.box('frame',xx-0.05,xx+0.05,0,2.3,z-0.02,z+0.03)
    p.box('frame',-0.65,0.65,2.28,2.36,z-0.02,z+0.03); p.box('light',-0.12,0.12,2.45,2.6,z,z+0.08)
    return p

# =====================================================================================
# KIT 3: narrow two-storey shop-house (bakery) with gable roof, dormer and attic
# =====================================================================================
from PIL import ImageFont
COL.update({'render':(206,112,78),'roof_tiles':(128,72,50),'ridge':(104,58,42),'shop_paint':(132,40,40),'frame':(244,238,226),
            'trim':(244,236,220),'canvas':(200,60,56),'slate':(78,84,96),'sign':(236,214,160),'iron':(40,38,40),'door':(120,40,38)})
def render_texture(px=256,seed=21):
    n=_noise(px,6,seed)*0.6+_noise(px,32,seed+1)*0.5+_noise(px,128,seed+2)*0.7
    a=np.array(COL['render'],np.float32)[None,None,:]+n[...,None]*18
    return Image.fromarray(np.clip(a,0,255).astype(np.uint8))
def roof_tiles_texture(px=256,seed=23):
    # tile 1 x 1 m: 4 rows of 0.25 m clay tiles, 0.2 m wide, staggered, shadow line at each row
    rnd=random.Random(seed); im=Image.new('RGB',(px,px),(84,46,34)); d=ImageDraw.Draw(im); rh=px/4; tw=px/5
    base=[(134,76,52),(126,70,48),(140,82,56),(120,66,46)]
    for r in range(4):
        off=tw/2 if r%2 else 0
        for i in range(-1,6):
            c=rnd.choice(base); x0=i*tw+off
            for dx in (-px,0,px):
                d.rounded_rectangle([x0+dx+1,r*rh+1,x0+dx+tw-1,r*rh+rh-2],radius=int(tw*0.3),fill=c)
                d.rectangle([x0+dx+2,r*rh+rh*0.72,x0+dx+tw-2,r*rh+rh-3],fill=tuple(int(v*0.82) for v in c))
    return im
def canvas_texture(px=256):
    # tile 1 m: red / cream stripes, 0.25 m each
    im=Image.new('RGB',(px,px),(244,236,220)); d=ImageDraw.Draw(im)
    for i in (0,2): d.rectangle([i*px/4,0,(i+1)*px/4-1,px],fill=(200,60,56))
    return im
def sign_texture(w=512,h=96,text='PADARIA'):
    im=Image.new('RGB',(w,h),(236,214,160)); d=ImageDraw.Draw(im)
    d.rectangle([6,6,w-7,h-7],outline=(132,40,40),width=5)
    f=ImageFont.load_default(size=58); bb=d.textbbox((0,0),text,font=f)
    d.text(((w-(bb[2]-bb[0]))/2-bb[0],(h-(bb[3]-bb[1]))/2-bb[1]),text,font=f,fill=(110,36,32))
    return im
RENDER_TEX=render_texture(); TILES_TEX=roof_tiles_texture(); CANVAS_TEX=canvas_texture(); SIGN_TEX=sign_texture()
for nm,im in (('render',RENDER_TEX),('roof_tiles',TILES_TEX),('canvas',CANVAS_TEX),('sign',SIGN_TEX)): im.save(os.path.join(OUT,nm+'_texture.png'))
TEX={'render':(RENDER_TEX,1.0,1.0),'roof_tiles':(TILES_TEX,1.0,1.0),'canvas':(CANVAS_TEX,1.0,1.0),'plaster':(PLASTER_TEX,1.0,1.0),
     'brick':(BRICK_TEX,1.0,1.0),'sign':(SIGN_TEX,1.0,1.0)}
SIGN=(-1.3,3.25,2.6,0.45)   # sign board: x0, y0, width, height (UVs span the board exactly)
MATS = {k:PBRMaterial(name=k, baseColorFactor=[c/255 for c in v]+[1.0], metallicFactor=0.0, roughnessFactor=0.9) for k,v in COL.items()}
for k,(im,_,_) in TEX.items(): MATS[k]=PBRMaterial(name=k,baseColorTexture=im,baseColorFactor=[1,1,1,1],metallicFactor=0.0,roughnessFactor=0.9)

HS=4.0     # shop ground floor height (standard)
KNEE=1.3   # attic knee wall (top hidden inside the roof)
def lvl(fl): return 0.0 if fl==0 else HS+(fl-1)*H
def ext(p,mat,poly,z0,z1):
    for g in getattr(poly,'geoms',[poly]):
        if g.area<1e-6: continue
        m=trimesh.creation.extrude_polygon(g,z1-z0); m.apply_translation([0,0,z0]); p.add(mat,m)
def hull(p,mat,pts): p.add(mat,trimesh.convex.convex_hull(np.array(pts,float)))

# ---------- ground floor: shop front + rendered walls (4.0 m) ----------
def shopfront_window():
    p=Piece(); ow=1.6; wall_with_opening(p,'shop_paint',ow,0.55,3.0,HS)
    x=ow/2; f=0.08
    p.box('glass',-x,x,0.55,3.0,-0.16,-0.14)
    for (a,b,c,d) in ((-x,-x+f,0.55,3.0),(x-f,x,0.55,3.0),(-x,x,3.0-f,3.0),(-x,x,0.55,0.55+f),(-0.03,0.03,0.55,3.0),(-x,x,2.42,2.47)):
        p.box('frame',a,b,c,d,-0.19,-0.06)
    p.box('trim',-x-0.06,x+0.06,0.47,0.565,-0.06,0.1)               # display sill
    for xx in (-0.45,0.45): p.box('shop_paint',xx-0.3,xx+0.3,0.12,0.42,0.0,0.025)   # riser panels
    return p
def shopfront_door():
    p=Piece(); ow=1.1; x=ow/2; oy0=0.015; wall_with_opening(p,'shop_paint',ow,oy0,3.0,HS)
    p.box('frame',-x,-x+0.08,oy0,3.0,-0.22,0.02); p.box('frame',x-0.08,x,oy0,3.0,-0.22,0.02); p.box('frame',-x,x,2.4,2.48,-0.22,0.02)
    p.box('frame',-x,x,2.92,3.0,-0.22,0.02); p.box('glass',-x+0.08,x-0.08,2.48,2.92,-0.16,-0.14)
    return p
def shop_fascia():
    """Painted sign band over the shop front with a small cornice. Pivot: bottom-centre at the facade (ground level)."""
    p=Piece(); p.box('shop_paint',-W/2,W/2,3.05,3.86,0,0.1); p.box('trim',-W/2,W/2,3.86,4.03,0,0.2); p.box('trim',-W/2,W/2,3.0,3.05,0,0.12); return p
def shop_sign():
    p=Piece(); x0,y0,w,h=SIGN; p.box('sign',x0,x0+w,y0,y0+h,0.1,0.15)
    p.box('trim',x0-0.05,x0+w+0.05,y0-0.05,y0,0.1,0.17); p.box('trim',x0-0.05,x0+w+0.05,y0+h,y0+h+0.05,0.1,0.17)
    p.box('trim',x0-0.05,x0,y0,y0+h,0.1,0.17); p.box('trim',x0+w,x0+w+0.05,y0,y0+h,0.1,0.17); return p
def awning():
    """Striped canvas awning for one 2 m shop bay. Pivot: bottom-centre at the facade (ground level)."""
    p=Piece(); d=1.4; y0,y1=2.98,2.38
    hull(p,'canvas',[(x,y,z) for x in (-W/2,W/2) for (y,z) in ((y0,0.0),(y0+0.04,0.0),(y1,d),(y1+0.04,d))])
    p.box('canvas',-W/2,W/2,y1-0.26,y1+0.02,d-0.02,d+0.02)
    for xx in (-W/2+0.08,W/2-0.08):
        p.seg('iron',(xx,y1-0.05,d-0.06),(xx,2.2,0.02),0.03)
    p.box('iron',-W/2+0.01,W/2-0.01,y0-0.07,y0-0.01,0.025,0.07); return p
def wall_render_shop_window():
    p=Piece(); wall_with_opening(p,'render',0.9,1.0,2.6,HS); window(p,0.9,1.0,2.6); ledge(p,HS,th=0.15,d=0.06); return p
def wall_render_shop_small_window():
    p=Piece(); wall_with_opening(p,'render',0.6,1.6,2.4,HS); window(p,0.6,1.6,2.4,mull=False); ledge(p,HS,th=0.15,d=0.06); return p
def wall_render_shop_plain():
    p=Piece(); wall_with_opening(p,'render',0,0,0,HS); ledge(p,HS,th=0.15,d=0.06); return p
def wall_render_shop_door():
    p=Piece(); ow=1.1; x=ow/2; oy0=0.015; wall_with_opening(p,'render',ow,oy0,2.4,HS)
    p.box('frame',-x,-x+0.07,oy0,2.4,-0.22,0.02); p.box('frame',x-0.07,x,oy0,2.4,-0.22,0.02); p.box('frame',-x,x,2.33,2.4,-0.22,0.02)
    p.box('trim',-x-0.1,x+0.1,2.41,2.55,-0.02,0.06); p.box('trim',-0.7,0.7,0,0.15,0,0.35); ledge(p,HS,th=0.15,d=0.06); return p
# ---------- first floor (3.0 m) ----------
def wall_render_window():
    p=Piece(); wall_with_opening(p,'render',0.9,0.85,2.3,H); window(p,0.9,0.85,2.3); ledge(p,H,th=0.08,d=0.04); return p
def wall_render_small_window():
    p=Piece(); wall_with_opening(p,'render',0.6,1.4,2.2,H); window(p,0.6,1.4,2.2,mull=False); ledge(p,H,th=0.08,d=0.04); return p
def wall_render_balconette():
    p=Piece(); wall_with_opening(p,'render',0.9,0.3,2.4,H); window(p,0.9,0.3,2.4)
    railing(p,-0.55,0.55,0.0,0.12,0.33,h=0.8,sides=(True,False,False),n=9); p.box('iron',-0.58,0.58,0.27,0.33,-0.04,0.16); ledge(p,H,th=0.08,d=0.04); return p
def wall_render_plain():
    p=Piece(); wall_with_opening(p,'render',0,0,0,H); ledge(p,H,th=0.08,d=0.04); return p
def corner_knee():
    p=Piece(); e=0.03; p.box('render',-T-0.01,e,0,KNEE,-T-0.01,e); return p
# ---------- attic: knee walls, gable, roof ----------
def knee_wall():
    p=Piece(); wall_with_opening(p,'render',0,0,0,KNEE); return p
HSP=5.0     # half span of the gable roof (building depth 10 m)
KR=0.84     # roof pitch: rise per metre (about 40 degrees)
TV=0.3      # roof thickness (vertical)
def roof_in(u): return 1.0+KR*u          # roof underside height above the attic floor, u = metres in from the facade
def roof_out(u): return 1.0+TV+KR*u
def knee_wall_dormer():
    """Knee wall module whose middle rises into a dormer front with a window (sill 0.8 m above the attic floor)."""
    p=Piece(); top=2.6; u1=(top-1.0-TV)/KR        # hole in the roof reaches where the roof top passes the dormer top
    xs=[-W/2,-0.8,-0.4,0.4,0.8,W/2]; ys=[0.0,0.8,KNEE,2.3,top]; zs=[-T,-T+0.02,0.0]
    def cell(i,j,k):
        if i in (0,4) and j>=2: return None
        if i==2 and j in (1,2): return None
        return 'plaster' if k==0 else 'render'
    for m,mesh in grid_solid(xs,ys,zs,cell).items(): p.add(m,mesh)
    window(p,0.8,0.8,2.3)
    ridge=top+0.5; yu=lambda x:ridge-abs(x)/0.92*0.56          # underside of the dormer roof
    tri=Polygon([(-0.8,top),(0.8,top),(0.8,yu(0.8)+0.02),(0,ridge+0.02),(-0.8,yu(0.8)+0.02)])
    ext(p,'render',tri,-T+0.02,0.0); ext(p,'plaster',tri,-T,-T+0.02)
    mid=lambda y:((y-1.0-TV/2)/KR)               # u where height y sits in the middle of the roof thickness
    for sx in (-1,1):   # cheeks: slate outside, plaster inside; bottom edge buried in the roof
        for (a,b,mat) in ((0.59,0.67,'plaster'),(0.67,0.8,'slate')):
            xa,xb=sorted((sx*a,sx*b))
            hull(p,mat,[(x,y,z) for x in (xa,xb) for (z,y) in ((-T,KNEE+0.15),(-T,yu(x)+0.03),(-u1,yu(x)+0.03),(-u1,roof_in(u1)+0.15))])
    for sx in (-1,1):   # dormer gable roof (slate); back ends stay inside the main roof thickness
        hull(p,'slate',[(x,y,z) for (x,y) in ((0,ridge),(sx*0.92,top-0.06),(0,ridge+0.08),(sx*0.92,top+0.02)) for z in (0.15,-mid(y+0.04))])
    ext(p,'plaster',Polygon([(-0.6,top),(0.6,top),(0.6,yu(0.6)+0.02),(0,ridge+0.02),(-0.6,yu(0.6)+0.02)]),-u1-0.02,-u1)
    p.box('trim',-0.86,0.86,top-0.06,top,0.0,0.05)
    return p
DORMER_U1=(2.6-1.0-TV)/KR
def roof_panel(p,x0,x1,hole=None):
    """Roof slope for one module: from the eave (0.4 m overhang) to the ridge HSP m in.
    Grid space (x, u, v): u = distance in from the facade, v = layer (plaster underside, tiles on top)."""
    us=[-0.4,HSP]; vs=[0.0,0.02,TV]
    if hole:
        hx,u1=hole; xs=[x0,-hx,hx,x1]; us=[-0.4,u1,HSP]
        def cell(i,j,k): return None if (i==1 and j==0) else ('plaster' if k==0 else 'roof_tiles')
    else:
        xs=[x0,x1]
        def cell(i,j,k): return 'plaster' if k==0 else 'roof_tiles'
    for m,mesh in grid_solid(xs,us,vs,cell).items():
        v=mesh.vertices.copy(); u=v[:,1].copy(); w=v[:,2].copy()
        v[:,1]=1.0+KR*u+w; v[:,2]=-u; mesh.vertices=v
        p.add(m,mesh)
def roof_slope(): p=Piece(); roof_panel(p,-W/2,W/2); return p
def roof_slope_end(): p=Piece(); roof_panel(p,-W/2,W/2+0.3); return p          # +x end runs 0.3 m past the gable
def roof_slope_end_l(): p=Piece(); roof_panel(p,-W/2-0.3,W/2); return p
def roof_slope_dormer(): p=Piece(); roof_panel(p,-W/2,W/2,hole=(0.6,DORMER_U1)); return p
def ridge_cap(x0=-W/2,x1=W/2):
    p=Piece(); y=roof_out(HSP); d=0.22
    hull(p,'ridge',[(x,yy,z) for x in (x0,x1) for (yy,z) in ((y-d*KR-0.04,d),(y-d*KR-0.04,-d),(y+0.08,0.0),(y-d*KR+0.06,d),(y-d*KR+0.06,-d))]); return p
def gable_wall():
    """Whole gable end (10 m) above the first floor: knee height at the eaves, apex under the ridge, attic window."""
    p=Piece(); top=lambda x:roof_in(HSP-abs(x))+0.15
    outer=Polygon([(-HSP,0),(HSP,0),(HSP,top(HSP)),(0,top(0)),(-HSP,top(-HSP))])
    hole=sbox(-0.45,1.4,0.45,2.6); body=outer.difference(hole)
    ext(p,'render',body,-T+0.02,0.0); ext(p,'plaster',body,-T,-T+0.02)
    window(p,0.9,1.4,2.6)
    return p
def bake_oven():
    """Built-in masonry bread oven against a wall. Pivot: back-centre on the floor, mouth toward +Z."""
    p=Piece(); w=1.2; d=2.0; h=1.4
    p.box('brick',-w,w,0,h,0,d)
    a=np.linspace(0,math.pi,13); hull(p,'brick',[(w*math.cos(t),h-0.01+0.6*math.sin(t),z) for t in a for z in (0.0,d)])
    p.box('trim',-w-0.05,w+0.05,0.82,0.9,d,d+0.06)                    # stone hearth ledge
    p.box('trim',-0.7,0.7,0.86,0.9,d+0.06,d+0.3)
    p.box('dark',-0.4,0.4,0.9,1.25,d,d+0.02); ext(p,'dark',half_disc(0,1.25,0.4),d,d+0.02)   # mouth
    ext(p,'trim',arch_half(0,1.25,0.4,0.5),d,d+0.04); p.box('iron',-0.35,0.35,0.92,1.2,d+0.02,d+0.04)
    return p
def oven_flue(h):
    """Masonry flue from the oven dome up through both floors and the roof. Pivot: base centre."""
    p=Piece(); p.box('brick',-0.3,0.3,0,h,-0.3,0.3); p.box('trim',-0.38,0.38,h,h+0.12,-0.38,0.38)
    for xx in (-0.13,0.13): p.cyl('roof_tiles',0.08,h+0.12,h+0.42,xx,0,10)
    return p
def arch_half(cx,cy,r0,r1,n=24):
    a=np.linspace(0,math.pi,n); o=[(cx+r1*math.cos(t),cy+r1*math.sin(t)) for t in a]; i=[(cx+r0*math.cos(t),cy+r0*math.sin(t)) for t in a[::-1]]
    return Polygon(o+i)
def half_disc(cx,cy,r,n=24):
    a=np.linspace(0,math.pi,n); return Polygon([(cx+r*math.cos(t),cy+r*math.sin(t)) for t in a])
def interior_wall_end_doorway(h=H-SLAB):
    """End wall (stops at the exterior wall's inner face) with a 0.9 m doorway in the middle of the module."""
    p=Piece(); t=0.12; e=W/2-T
    xs=[-W/2,-0.45,0.45,e]; ys=[0.0,2.1,h]; zs=[-t/2,t/2]
    def cell(i,j,k): return None if (i==1 and j==0) else 'plaster'
    for m,mesh in grid_solid(xs,ys,zs,cell).items(): p.add(m,mesh)
    for xx in (-0.45,0.45): p.box('frame',xx-0.04,xx+0.04,0,2.14,-t/2-0.02,t/2+0.02)
    p.box('frame',-0.49,0.49,2.08,2.18,-t/2-0.02,t/2+0.02)
    for (a,b) in ((-W/2,-0.49),(0.49,e)): p.box('trim',a,b,0,0.1,t/2,t/2+0.015); p.box('trim',a,b,0,0.1,-t/2-0.015,-t/2)
    return p
def stair_core_rail():
    p=Piece(); railing(p,-0.02,0.02,-1.98,1.98,0,sides=(False,True,False),n=24); return p

HI=HS-SLAB
FLUE_Y=1.6; FLUE_U=0.7
FLUE_H=round(HS+H+roof_out(FLUE_U)+1.1-FLUE_Y,2)   # from inside the oven dome to 1.1 m above the back roof
pieces={'floor_tile':floor_tile(),'floor_tile_bath':floor_tile_bath(),'stair_core_slab':stair_core_slab(),'stair_core_rail':stair_core_rail(),
 'stairs_u_4m':stairs_u(HS,run=3.0,land=0.95),'stairs_u_3m':stairs_u(H),
 'door_leaf_shop':door_leaf(0.94,2.36,True,'door'),'door_leaf_back':door_leaf(0.96,2.3,False,'door'),'door_leaf_interior':door_leaf(0.86,2.08,False,'frame'),
 'interior_wall_plain':interior_wall(False),'interior_wall_doorway':interior_wall(True),'interior_wall_end':interior_wall_end(),'interior_wall_end_doorway':interior_wall_end_doorway(),
 'interior_wall_plain_shop':interior_wall(False,HI),'interior_wall_doorway_shop':interior_wall(True,HI),'interior_wall_end_shop':interior_wall_end(HI),'interior_wall_end_doorway_shop':interior_wall_end_doorway(HI),
 'shopfront_window':shopfront_window(),'shopfront_door':shopfront_door(),'shop_fascia':shop_fascia(),'shop_sign':shop_sign(),'awning':awning(),
 'wall_render_shop_window':wall_render_shop_window(),'wall_render_shop_plain':wall_render_shop_plain(),'wall_render_shop_small_window':wall_render_shop_small_window(),'wall_render_shop_door':wall_render_shop_door(),
 'corner_shop':corner('render',HS,0.15,0.06),'corner_render':corner('render',H,0.08,0.04),'corner_knee':corner_knee(),
 'wall_render_window':wall_render_window(),'wall_render_small_window':wall_render_small_window(),'wall_render_balconette':wall_render_balconette(),'wall_render_plain':wall_render_plain(),
 'knee_wall':knee_wall(),'knee_wall_dormer':knee_wall_dormer(),'gable_wall':gable_wall(),
 'roof_slope':roof_slope(),'roof_slope_end':roof_slope_end(),'roof_slope_end_l':roof_slope_end_l(),'roof_slope_dormer':roof_slope_dormer(),
 'ridge_cap':ridge_cap(),'ridge_cap_end':ridge_cap(-0.17,0.17),'bake_oven':bake_oven(),'oven_flue':oven_flue(FLUE_H),'player_scale_ref':player_ref(),
}
import shutil; shutil.rmtree(f'{OUT}/pieces',ignore_errors=True); os.makedirs(f'{OUT}/pieces')
for n,p in pieces.items(): p.scene(n).export(f'{OUT}/pieces/{n}.glb',include_normals=True)

# ================= assembly: 12 x 10 m bakery, shop front on +Z, gables on +-X =================
SX,SZ=6.0,5.0
L=[]
def put(n,x,y,z,ry=0,tags=(),door=None):
    e={'piece':n,'pos':[round(x,3),round(y,3),round(z,3)],'rotY':ry,'tags':list(tags)}
    if door is not None: e['door']={'closed':ry,'open':ry+door}; e['tags'].append('door')
    L.append(e)
def hinge(x,z,ry,lx,lz):
    r=math.radians(ry); return x+lx*math.cos(r)+lz*math.sin(r), z-lx*math.sin(r)+lz*math.cos(r)
def ftag(fl): return f'floor{fl}'
FB=[-5,-3,-1,1,3,5]; SB=[-4,-2,0,2,4]
faces=[(0,FB,lambda u:(u,SZ),'front'),(90,SB,lambda u:(SX,-u),'right'),(180,FB,lambda u:(-u,-SZ),'back'),(-90,SB,lambda u:(-SX,u),'left')]
SW,SP,SD='wall_render_shop_window','wall_render_shop_plain','wall_render_shop_door'
G={'front':{-5:'shopfront_window',-3:'shopfront_window',-1:'shopfront_door',1:'shopfront_window',3:'shopfront_window',5:'shopfront_window'},
   'back':{-5:SW,-3:SP,-1:SP,1:SD,3:SP,5:SP},           # oven against the back wall at x=-2, loading door at x=1, stair core x>2
   'left':{4:SW,2:SW,0:SP,-2:SP,-4:SW},
   'right':{4:SW,2:SW,0:'wall_render_shop_small_window',-2:SP,-4:SP}}
RW,RS,RB,RP='wall_render_window','wall_render_small_window','wall_render_balconette','wall_render_plain'
F1={'front':{-5:RB,-3:RB,-1:RW,1:RW,3:RW,5:RW},
    'back':{-5:RW,-3:RW,-1:RS,1:RS,3:RP,5:RP},
    'left':{4:RW,2:RW,0:RW,-2:RW,-4:RW},
    'right':{4:RW,2:RW,0:RW,-2:RP,-4:RP}}
DORMERS={-3,3}
for ry,bays,f,tag in faces:
    for u in bays:
        x,z=f(u); wk=x if tag in ('front','back') else z
        put(G[tag][wk],x,0,z,ry,[tag,'ext',ftag(0)])
        put(F1[tag][wk],x,lvl(1),z,ry,[tag,'ext',ftag(1)])
        if tag in ('front','back'):
            dorm=(tag=='front' and x in DORMERS)
            put('knee_wall_dormer' if dorm else 'knee_wall',x,lvl(2),z,ry,[tag,'ext',ftag(2)])
            if dorm: rn='roof_slope_dormer'
            elif abs(x)==5: rn='roof_slope_end' if (x>0)==(tag=='front') else 'roof_slope_end_l'
            else: rn='roof_slope'
            put(rn,x,lvl(2),z,ry,[tag,'roof'])
for x in FB: put('ridge_cap',x,lvl(2),0,0,['roof'])
for x in (-SX-0.15,SX+0.15): put('ridge_cap_end',x,lvl(2),0,0,['roof'])
put('gable_wall',SX,lvl(2),0,90,['right','ext',ftag(2)]); put('gable_wall',-SX,lvl(2),0,-90,['left','ext',ftag(2)])
for ry,x,z,tg in [(0,SX,SZ,('front','right')),(90,SX,-SZ,('right','back')),(180,-SX,-SZ,('back','left')),(-90,-SX,SZ,('left','front'))]:
    put('corner_shop',x,0,z,ry,tg+('ext',ftag(0))); put('corner_render',x,lvl(1),z,ry,tg+('ext',ftag(1))); put('corner_knee',x,lvl(2),z,ry,tg+('ext',ftag(2)))
for x in FB: put('shop_fascia',x,0,SZ,0,['front','ext',ftag(0)]); put('awning',x,0,SZ,0,['front','ext',ftag(0)])
put('shop_sign',-1,0,SZ,0,['front','ext',ftag(0)])
# oven + flue (flue runs inside the upstairs wall line x=-2 and exits the back roof slope)
put('bake_oven',-2,0,-SZ+T,0,[ftag(0)])
put('oven_flue',-2,FLUE_Y,-SZ+FLUE_U,0,['roof'])
# slabs: stair core x in [2,6], z in [-5,-1]
CORE={(3,-4),(5,-4),(3,-2),(5,-2)}
TILE={0:{(a,b) for a in (-3,-1,1) for b in (-4,-2,0)}|{(5,0)},1:{(1,-4),(1,-2)}}
for fl in range(0,3):
    y=lvl(fl)
    for a in FB:
        for b in SB:
            if fl>0 and (a,b) in CORE: continue
            put('floor_tile_bath' if (a,b) in TILE.get(fl,()) else 'floor_tile',a,y,b,0,[ftag(fl)])
    if fl>0:
        put('stair_core_slab',4,y,-3,0,[ftag(fl)]); put('stair_core_rail',4-1.4,y,-3,0,[ftag(fl)]); put('stair_core_rail',4+1.4,y,-3,0,[ftag(fl)])
put('stairs_u_4m',4,0,-1,0,[ftag(0)]); put('stairs_u_3m',4,lvl(1),-1,0,[ftag(1)])
def wl(fl,x0,z0,x1,z1,doors=()):
    y=lvl(fl); g='_shop' if fl==0 else ''
    if z0==z1:
        for c in range(int(min(x0,x1))+1,int(max(x0,x1)),2):
            if abs(c)+1>=SX: put(('interior_wall_end_doorway' if c in doors else 'interior_wall_end')+g,c,y,z0,0 if c>0 else 180,[ftag(fl)]); continue
            put(('interior_wall_doorway' if c in doors else 'interior_wall_plain')+g,c,y,z0,0,[ftag(fl)])
    else:
        for c in range(int(min(z0,z1))+1,int(max(z0,z1)),2):
            if abs(c)+1>=SZ: put(('interior_wall_end_doorway' if c in doors else 'interior_wall_end')+g,x0,y,c,-90 if c>0 else 90,[ftag(fl)]); continue
            put(('interior_wall_doorway' if c in doors else 'interior_wall_plain')+g,x0,y,c,90,[ftag(fl)])
def door(fl,x,z,ry,ang=70):
    hx,hz=hinge(x,z,ry,-0.43,0); put('door_leaf_interior',hx,lvl(fl),hz,ry,[ftag(fl)],door=ang)
# ground: shop + cafe (front, 12 x 4), production with oven (6 x 6), flour/dry store, customer WC, staff hall + stair
wl(0,-6,1,6,1,doors=(-1,5)); wl(0,-4,-5,-4,1,doors=(-2,)); wl(0,2,-5,2,1,doors=(0,)); wl(0,4,-1,4,1); wl(0,4,-1,6,-1)
door(0,-1,1,0); door(0,-4,-2,90); door(0,2,0,90,-70); door(0,5,1,0)
# first floor (bakery support): pastry room, office, staff room (front); dry store, changing room, staff WC (back)
wl(1,-6,1,6,1,doors=(-3,-1,3)); wl(1,-6,-1,2,-1,doors=(-3,-1,1))
wl(1,-2,1,-2,5); wl(1,2,1,2,5); wl(1,-2,-5,-2,-1); wl(1,0,-5,0,-1); wl(1,2,-5,2,-1)
for (x,z) in ((-3,1),(-1,1),(3,1)): door(1,x,z,0)
for (x,z) in ((-3,-1),(-1,-1),(1,-1)): door(1,x,z,0,-70)
# attic: open dry-goods loft
put('door_leaf_shop',-1-0.47,0.015,SZ-0.18,0,['front','ext',ftag(0)],door=85)
hx,hz=hinge(1,-SZ,180,-0.48,-0.18); put('door_leaf_back',hx,0.015,hz,180,['back','ext',ftag(0)],door=85)
put('player_scale_ref',2.6,0,SZ+1.6); put('player_scale_ref',-1,0,3,0,[ftag(0)]); put('player_scale_ref',-1,lvl(1),0,0,[ftag(1)]); put('player_scale_ref',-1,lvl(2),0,0,[ftag(2)])
json.dump({'grid':{'module_width':W,'floor_height':H,'shop_ground_floor_height':HS,'wall_thickness':T,'slab':SLAB,'footprint':[2*SX,2*SZ],'roof':'gable, pitch 0.84 (40 deg), ridge along X at z=0'},'placements':L},open(f'{OUT}/building_layout.json','w'),indent=1)
asm=Piece()
for e in L:
    if e['piece']=='player_scale_ref': continue
    Tm=trimesh.transformations.rotation_matrix(math.radians(e['rotY']),[0,1,0]); Tm[:3,3]=e['pos']
    asm.merge(pieces[e['piece']],Tm)
asm.scene('building').export(f'{OUT}/building_assembled.glb',include_normals=True)
print(len(pieces),'pieces',len(L),'placements',sum(1 for e in L if 'door' in e),'doors')
